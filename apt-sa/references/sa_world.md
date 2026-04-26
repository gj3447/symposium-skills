# SA World Reference

> APT v11 SA Phase 상세 레퍼런스. SKILL.md가 "무엇을 하라"이면 이 문서는 "구체적으로 어떻게"를 제공한다.

---

## 1. Progressive Disclosure 3단계

### L1: 메타데이터 (토큰 예산 ~2K)

프로젝트 정체성과 최상위 Span 이름/설명만 로드. KG 전체를 읽지 않는다.

```cypher
-- L1: SA + 직계 자식 메타데이터만
MATCH (sa:SemanticAnchor {name: $sa_name})-[:DECOMPOSES_TO]->(l1)
RETURN sa.name, sa.description, sa.domain, sa.status,
       l1.name, l1.description, l1.depth
ORDER BY l1.name
```

**포함 항목:** SA name, description, domain, status, L1 Span 이름/설명
**제외 항목:** Span 트리 구조, Contract, 소스코드, 테스트 결과

### L2: 구조 (토큰 예산 ~5K)

선택된 브랜치의 Span 트리와 Contract 목록을 로드. 작업 대상 브랜치만 로드한다.

```cypher
-- L2: 선택된 브랜치의 Span 트리 + Contract 존재 여부
MATCH (root:AptSpan {name: $branch})-[:DECOMPOSES_TO*1..5]->(s)
OPTIONAL MATCH (s)-[:CRYSTALLIZES_TO]->(st)-[:HAS_CONTRACT]->(c)
RETURN s.name, s.depth, s.is_atomic, s.status,
       c.name AS contract, c.status AS contract_status
ORDER BY s.depth, s.name
```

**포함 항목:** Span 계층 구조, 각 Span의 상태, Contract 존재 여부
**제외 항목:** Contract 상세 필드, 소스코드, 테스트 결과

### L3: 상세 (토큰 예산 ~8K)

특정 AtomicSpan의 Contract 전문, acceptance criteria, 소스코드를 로드.

```cypher
-- L3: 특정 AtomicSpan 상세
MATCH (atom:AtomicSpan {name: $atom})-[:CRYSTALLIZES_TO]->(st)-[:HAS_CONTRACT]->(c)
OPTIONAL MATCH (st)-[:HAS_TASK]->(t)
OPTIONAL MATCH (c)-[:MATERIALIZES]->(src)
RETURN c.name, c.input_type, c.output_type,
       c.precondition, c.postcondition,
       c.acceptance_criteria, c.target_file,
       c.nfr_latency_p99_ms, c.nfr_memory_mb,
       c.nfr_accuracy_metric, c.nfr_execution_env,
       t.description, t.acceptance_criteria, t.impact_tests,
       src.file_path, src.lines, src.status
```

**포함 항목:** Contract 7대 필드, NFR, Task 상세, 소스코드 메타데이터
**제외 항목:** 다른 Span의 정보, KG 탐색 이력

---

## 2. Context Budget 할당 공식

depth별 토큰 예산을 SA 단계에서 미리 할당한다. Context Rot(토큰 증가 시 n^2으로 주의력 분산)을 방지.

| Span Depth | 토큰 예산 | 근거 |
|:----------:|:---------:|------|
| 0 (Root)   | 50,000    | 프로젝트 전체 개요. L1 메타 + L2 구조 |
| 1          | 50,000    | 주요 모듈. 넉넉한 컨텍스트 필요 |
| 2          | 20,000    | 서브모듈. 범위가 좁아짐 |
| 3+         | 8,000     | AtomicSpan. 단일 파일 500줄 구현에 적정 |

```cypher
-- SA에서 Context Budget 설정
MATCH (sa:SemanticAnchor {name: $sa_name})
SET sa.context_budget_total = 100000,
    sa.context_budget_per_span = 8000

-- Span 생성 시 depth 기반 자동 할당
MERGE (child:AptSpan {name: $name})
SET child.context_budget = CASE
  WHEN child.depth <= 1 THEN 50000
  WHEN child.depth = 2 THEN 20000
  ELSE 8000 END
```

**C26 참고:** Context Budget은 인지과학이 아닌 공학적 휴리스틱이다. 경험적으로 설정한 토큰 제한.

---

## 3. apt-progress.md 초기 포맷 템플릿

SA 완료 시 반드시 생성. 세션 연속성의 핵심 파일.

```markdown
# APT Progress: {project_name}

## Anchor: {sa_name}
## Domain: {domain}
## Status: active
## Created: {datetime}
## Last Updated: {datetime}
## Context Budget: total={total}K, per_span={per_span}K

---

### Completed Spans
(none yet)

### In Progress
- {current_span}: SA complete, ready for SP

### Blocked
(none)

### KG Stats
- SemanticAnchor: {sa_name}
- L1 Spans: {count}
- INFORMED_BY links: {count}

### Next Steps
1. SP Phase: {first_branch} 분해 시작
2. 각 L1 Span에 INFORMED_BY >= 5 확보

### Session Log
- [{datetime}] SA Phase: anchor {sa_name} created/reused
```

---

## 4. SA -> SP 핸드오프 체크리스트

SA에서 SP로 전환하기 전 **모든 항목**을 확인:

| # | 체크 항목 | 검증 방법 |
|---|----------|----------|
| 1 | SemanticAnchor가 KG에 존재 | `MATCH (sa:SemanticAnchor {name: $sa}) RETURN sa` |
| 2 | SA status = 'active' | `sa.status = 'active'` 확인 |
| 3 | Root Span이 SA에 연결됨 | `MATCH (sa)-[:HAS_ROOT]->(root) RETURN root` |
| 4 | Progressive Disclosure L1 로드됨 | apt-progress.md에 L1 Span 목록 기재 확인 |
| 5 | Context Budget 할당됨 | `sa.context_budget_total IS NOT NULL` |
| 6 | apt-progress.md 생성됨 | 파일 존재 확인 |
| 7 | 기존 앵커 중복 없음 | KG 탐색으로 유사 앵커 부재 확인 |
| 8 | Git commit 완료 | `apt-progress.md` 커밋됨 |

**Phase Transition Compaction:**
- **보존**: 앵커 이름, 설명, L1 Span 목록, Context Budget
- **제거**: KG 탐색 과정, 후보 비교, 의사결정 로그
- **새 컨텍스트**: 압축 요약 + 최근 5개 접근 파일로 SP 시작

---

## 5. SA 관련 에러 사례

### E-SA1: KG 중복 앵커

**Context:** KG 탐색 없이 새 앵커를 생성. 기존에 동일/유사 프로젝트 앵커가 이미 존재했음.
**Lesson:** 앵커 생성 전 반드시 KG 탐색. 이것이 SA의 가장 흔한 실수.
**Guard:** Step 1의 KG 탐색을 반드시 선행. MERGE 사용으로 중복 방지.

```cypher
-- 중복 앵커 탐지
MATCH (sa:SemanticAnchor)
WHERE sa.name CONTAINS $keyword OR sa.description CONTAINS $keyword
RETURN sa.name, sa.description, sa.status
```

### E-SA2: Progressive Disclosure 무시 (전체 KG 로드)

**Context:** L1/L2/L3 단계를 무시하고 KG 전체를 한번에 로드. 토큰 폭발로 Context Rot 발생.
**Lesson:** Context Budget은 공학적 필수사항. 단계별 로딩이 품질을 보장.
**Guard:** L1 → L2 → L3 순서 강제. 각 단계에서 토큰 사용량 확인.

### E-SA3: 앵커 없이 SP 진입

**Context:** SA Phase를 생략하고 바로 Span 분해 시작. 프로젝트 정체성 미확립.
**Lesson:** D9 GenerativeFlowOrdering. SA가 없으면 모든 후속 Phase의 기반이 없다.
**Guard:** SP 진입 시 SA 존재 검증 쿼리 실행.

```cypher
-- SP 진입 전 SA 존재 확인
MATCH (sa:SemanticAnchor {name: $project, status: 'active'})
RETURN sa.name
-- 결과 없으면 SA Phase 미완료
```

---

## 6. SA 관련 Validation Queries

### V-SA1: 고아 Root Span (SA 미연결)

```cypher
-- Root Span이 SA에 연결되지 않은 경우
MATCH (root:AptSpan)
WHERE root.depth = 0
  AND NOT ()-[:HAS_ROOT]->(root)
RETURN 'V_SA1_OrphanRoot' AS validation,
       root.name AS orphan_root
```

### V-SA2: SA 중복 (동일 프로젝트 이름)

```cypher
-- 같은 이름의 SA가 여러 개인 경우
MATCH (sa:SemanticAnchor)
WITH sa.name AS sa_name, count(sa) AS cnt
WHERE cnt > 1
RETURN 'V_SA2_DuplicateAnchor' AS validation,
       sa_name, cnt
```

### V-SA3: SA without Root Span

```cypher
-- Root Span이 없는 SA
MATCH (sa:SemanticAnchor {status: 'active'})
WHERE NOT (sa)-[:HAS_ROOT]->()
RETURN 'V_SA3_NoRoot' AS validation,
       sa.name AS anchor_without_root
```

### V-SA4: Context Budget 미할당

```cypher
-- Context Budget이 없는 SA
MATCH (sa:SemanticAnchor {status: 'active'})
WHERE sa.context_budget_total IS NULL
RETURN 'V_SA4_NoBudget' AS validation,
       sa.name AS anchor_without_budget
```

# Progressive Disclosure 3-Tier (Cross-Skill Shared)

> APT 모든 phase에서 사용하는 KG/문서 lazy-load 패턴. Context Rot(토큰 폭주 시 n² attention 분산) 방지의 공학 메커니즘.

---

## 3 tier 정의

### L1: 메타데이터 (토큰 예산 ~2K)

상위 정체성 + 자식 메타데이터만. 전체 트리 구조 / Contract / 코드 / 테스트 결과 제외.

```cypher
-- 예시: SemanticAnchor + 직계 L1 Span 메타
MATCH (sa:SemanticAnchor {name: $sa_name})-[:DECOMPOSES_TO]->(l1)
RETURN sa.name, sa.description, sa.domain, sa.status,
       l1.name, l1.description, l1.depth
ORDER BY l1.name
```

### L2: 구조 (토큰 예산 ~5K)

선택된 브랜치의 Span 트리 + Contract 존재 여부 (필드 미포함). 작업 대상 브랜치만 로드.

```cypher
-- 예시: 선택 브랜치 Span 트리 + Contract 존재 여부
MATCH (root:AptSpan {name: $branch})-[:DECOMPOSES_TO*1..5]->(s)
OPTIONAL MATCH (s)-[:CRYSTALLIZES_TO]->(st)-[:HAS_CONTRACT]->(c)
RETURN s.name, s.depth, s.is_atomic, s.status,
       c.name AS contract, c.status AS contract_status
ORDER BY s.depth, s.name
```

### L3: 상세 (토큰 예산 ~8K)

특정 AtomicSpan의 Contract 전문, acceptance criteria, 소스코드 메타. 한 번에 *한 atom*만 L3로.

```cypher
-- 예시: AtomicSpan + Contract 전문 + Task + 소스코드
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

---

## 적용 의무 (모든 phase 공통)

1. **순서 강제**: L1 → L2 → L3. 거꾸로 또는 건너뛰기 금지.
2. **L3 단일 atom**: 한 시점에 *한 AtomicSpan*만 L3로 로드. 여러 atom 동시 L3 = Context Rot 시작.
3. **재진입 시 압축**: 다른 atom L3로 전환 시 이전 L3 컨텍스트 압축 (요약만 유지).
4. **검증**: SA 단계에서 `apt-progress.md` L1 Span 목록 기재 확인 (P-SA4 check).

---

## phase별 변형

각 phase는 L1/L2/L3 매핑이 약간 다름:

| Phase | L1 | L2 | L3 |
|---|---|---|---|
| SA | SemanticAnchor + 직계 Span 메타 | 선택 브랜치 Span 트리 + Contract 존재 여부 | (SA 단계에선 보통 L3 미사용) |
| SP | 부모 Span + 직계 자식 메타 | 자식들의 INFORMED_BY/Layer/depth 분포 | 특정 자식의 C(S) 5 술어 평가 결과 |
| ST | AtomicSpan + Contract 존재 여부 | Contract draft 7 필드 + Task 윤곽 | Contract 전문 + acceptance criteria + NFR |
| SCW | Contract 헤더 + impact_tests 경로 | impact_tests baseline + 의존 모듈 | 소스코드 + 테스트 + KG ref comment |

phase별 자세한 cypher는 각 phase의 `references/` 내 phase-specific 파일 참조.

---

## anti-pattern

- **E-PD1: 전체 KG 한 번에 로드** — 토큰 폭발, Context Rot. SA에선 흔한 실수(E-SA2).
- **E-PD2: L3 다중 atom** — atom A의 L3 켜둔 채 atom B의 L3도 켬. 후속 평가 모두 오염.
- **E-PD3: L1 skip, L2 직행** — 정체성 미확립 상태에서 구조 로드. 잘못된 브랜치 선택.

# KG: APT_PD_canonical_pattern, lesson-context-rot-prevention-pd

# SP World Reference

> APT v11 SP Phase 상세 레퍼런스. SKILL.md가 "무엇을 하라"이면 이 문서는 "구체적으로 어떻게"를 제공한다.

---

## 1. C(S) 5개 술어 상세

### 평가 순서: v -> t -> i -> d -> s (cheap-first)

v10 이전에는 s(인간 검토)를 먼저 수행하여, 자동으로 걸러낼 수 있는 Span에도 4시간 SLA 인간 검토를 낭비했다 (E10 참조). v11에서는 비용이 낮은 자동 검사부터 수행.

| 순서 | 술어 | 비용 | 설명 |
|:----:|:----:|:----:|------|
| 1 | **v(S)** | ~0 (휴리스틱) | 구현 크기 추정만으로 판단 |
| 2 | **t(S)** | 낮음 (타입 분석) | 입출력 타입의 구체성 확인 |
| 3 | **i(S)** | 낮음 (assertion 스케치) | 테스트 가능한 postcondition 존재 확인 |
| 4 | **d(S)** | 낮음 (크기 추정) | 과잉 분해 여부 확인 |
| 5 | **s(S)** | 높음 (인간/에이전트 판단) | 자동(s_auto) + 오라클(s_oracle) |

**핵심:** v, t, i, d 모두 PASS해야 s 평가로 진행. 하나라도 FAIL이면 s_oracle 요청 없이 즉시 분해.

### v(S) — Implementation Feasibility (복잡도)

**판정 기준:** `estimated_lines > config.complexity_threshold (default 500)` 이면 FAIL.
**예시:**
- PASS: "사용자 인증 토큰 검증" — 추정 200줄, 단일 책임
- FAIL: "전체 API 게이트웨이" — 추정 2000줄, 다중 책임
**실패 시 분할 전략:** 기능 영역별로 분할. 예: 게이트웨이 → 라우팅 + 인증 + 레이트리밋 + 로깅

### t(S) — Type Expressibility (타입 표현 가능성)

**판정 기준:** `def f(x: ConcreteDTO) -> ConcreteDTO`를 작성할 수 있는가? 타입이 "data", "any", "object", "result", "info"이면 FAIL.
**예시:**
- PASS: `input: PointCloud(N x 3, float32) -> output: TransformMatrix(4x4, float64)`
- FAIL: `input: data -> output: result` (너무 추상적)
**실패 시 분할 전략:** 출력 타입 경계로 분할. 한 함수가 여러 타입을 반환하면 각각 별도 Span.

### i(S) — Test Feasibility (테스트 가능성)

**판정 기준:** `assert result.field == specific_value`를 작성할 수 있는가? 구체적 테스트 assertion이 불가능하면 FAIL.
**예시:**
- PASS: "JSON 파서" — `assert parse('{"a":1}')['a'] == 1`
- FAIL: "시스템 성능 개선" — 구체적 assertion 불가
**실패 시 분할 전략:** 구체적 예시로 명세를 날카롭게 만든다. 추상 목표를 측정 가능한 하위 목표로 분해.

### d(S) — Decomposition Diseconomy (과잉 분해 방지)

**판정 기준:** `estimated_lines < 100 AND parent exists` 이면 FAIL. 이미 충분히 작은 것을 더 쪼개면 오버헤드만 증가.
**예시:**
- PASS: 추정 250줄 — 적절한 크기
- FAIL: 추정 50줄 — 더 분해하면 20줄짜리 조각, 오버헤드 > 이득
**실패 시 분할 전략:** 분할하지 않음. 부모로 병합 상향(merge up). 이미 atomic.

### s(S) — Semantic Completeness

**s_auto (자동):**
- 용어 커버리지: S.description의 모든 도메인 용어에 대응하는 INFORMED_BY 링크 존재 확인
- 도메인 온톨로지 매칭: KG 내 기존 도메인 개념과의 라벨/관계 패턴 일치 확인
- 명명 규약: S.name이 프로젝트 패턴을 따르는지 확인

**s_oracle (인간/에이전트):**
- executor != reviewer 필수 (분리 의무)
- 질문: "이것이 올바른 분해인가? 이 Span이 응집적이고 완전한 의미 단위를 포착하는가?"
- SLA: `config.sigma_sla_hours` (기본 4시간)
- 타임아웃 시: 위임 체인 (Primary → Secondary → Human → Auto-REJECT)

**s_auto → s_oracle 흐름:**

```
s_auto PASS → s_oracle 요청
s_auto FAIL → 즉시 Step 3 (분해)
s_oracle APPROVED → AtomicSpan 라벨링
s_oracle REJECTED → Step 3 (분해)
```

`config.allow_agent_sigma = true` (dev 환경)이면 에이전트가 s_oracle 역할 가능. 단, executor와 다른 에이전트여야 함.

---

## 2. EXPLORES_VIA 패턴

### 3가지 전략

| 전략 | 의미 | 사용 시점 | Edge 속성 |
|------|------|----------|----------|
| **best_of_n** | N개 대안을 독립 실행, 벤치마크 후 승자 1개 선택 | 복수 알고리즘이 존재하고 경험적 비교 필요 | strategy, created_at |
| **ensemble** | N개 대안의 출력을 결합 (투표, 평균, 스태킹) | 조합이 개별보다 높은 정확도를 낼 때 | strategy, weight(0.0~1.0) |
| **fallback_chain** | 우선순위 순서로 시도, 첫 성공 사용 | 대안들의 신뢰도/비용이 다를 때 | strategy, priority(1=first) |

### Selection Span

탐색의 부모 Span이 소유하는 **전용 평가자**. DECOMPOSES_TO로 연결 (EXPLORES_VIA가 아님).

```
Parent (탐색 소유자)
  |
  +-- EXPLORES_VIA {strategy:'best_of_n'} --> Alt_A (AtomicSpan)
  +-- EXPLORES_VIA {strategy:'best_of_n'} --> Alt_B (AtomicSpan)
  +-- EXPLORES_VIA {strategy:'best_of_n'} --> Alt_C (AtomicSpan)
  |
  +-- DECOMPOSES_TO --> Selection_Span (AtomicSpan)
       |-- 모든 대안 벤치마크 실행
       |-- 정확도, 지연시간, NFR 준수 평가
       +-- 승자를 KG에 SELECTED 엣지로 기록
```

A3 (SiblingIndependence): 대안들은 상호 독립. Selection Span은 대안들의 출력에만 의존 (내부에 의존하지 않음).

### Confluence Detection

두 대안이 동등한 결과를 산출하면 **confluent** (합류).

```cypher
-- 벤치마크 후 두 대안의 결과가 허용 범위 내로 동등한 경우
MATCH (a1:AtomicSpan)<-[:EXPLORES_VIA]-(parent)-[:EXPLORES_VIA]->(a2:AtomicSpan)
WHERE a1 <> a2
  AND a1.benchmark_result IS NOT NULL
  AND a2.benchmark_result IS NOT NULL
  AND abs(a1.benchmark_accuracy - a2.benchmark_accuracy) < $tolerance
MERGE (a1)-[:CONFLUENT_WITH {
  metric: 'accuracy',
  delta: abs(a1.benchmark_accuracy - a2.benchmark_accuracy),
  detected_at: datetime()
}]->(a2)
```

**합류 감지 시:**
1. CONFLUENT_WITH 엣지 기록
2. Selection Span이 결정 근거에 합류 사실 기재
3. 향후 탐색에서 합류 대안 중 하나를 건너뛸 수 있음
4. 모든 대안이 합류하면 탐색이 단일 브랜치로 축소

---

## 3. RefinementGate 3 Checks

분해 후 자식 집합의 품질을 검증하는 게이트.

### Coverage (커버리지)

**질문:** 자식들이 부모의 의미를 완전히 커버하는가?
**실패 시:** 누락된 Span 추가. 부모의 설명에서 커버되지 않은 의미 영역을 식별하여 새 자식 생성.

### Consistency (일관성)

**질문:** 자식 간 모순이 없는가?
**실패 시:** 모순되는 자식의 설명을 수정. 동일 입력에 대해 상충하는 postcondition이 있으면 하나를 조정.

### Independence (독립성)

**질문:** 형제(sibling) 간 의존이 없는가?
**실패 시:** 의존 관계가 있는 형제를 재분해. 의존을 부모 레벨로 올리거나 구조 변경.

```cypher
-- Independence 검증 (반드시 0행 반환)
MATCH (p:AptSpan {name: $parent})-[:DECOMPOSES_TO]->(a),
      (p)-[:DECOMPOSES_TO]->(b)
WHERE a <> b AND (a)-[:DEPENDS_ON]->(b)
RETURN a.name AS dependent, b.name AS dependency
-- 결과가 있으면 A3 위반: 재분해 필요
```

---

## 4. Dense Linking (INFORMED_BY >= N)

### 유효한 링크 종류

| 링크 대상 | 예시 | 유효 이유 |
|----------|------|----------|
| 도메인 논문/문서 | `Research` 노드 | 알고리즘/기법 근거 |
| 기존 Span/Contract | 관련 모듈 노드 | 재사용/참조 |
| 도메인 개념 | `Concept` 노드 | 용어 정의/온톨로지 |
| 외부 API/라이브러리 | `Entity` 노드 | 의존성 명시 |
| 하드웨어 컨텍스트 | `HardwareContext` 노드 | 물리적 제약 |

**무효한 링크:** 자기 참조, 부모/자식 링크 (구조적 관계는 DECOMPOSES_TO), 관련 없는 도메인의 노드.

```cypher
-- Dense Linking: 최소 5개 INFORMED_BY
MATCH (s:AptSpan {name: $span})
MATCH (k) WHERE k.name CONTAINS $concept
MERGE (s)-[:INFORMED_BY {reason: $why, linked_at: datetime()}]->(k)
```

---

## 5. SP 4 Rules 상세

### Rule 1: SpanPlanningNature

Span은 **추상적 의미(meaning)**를 기술한다. 코드 아티팩트가 아니다.
- GOOD: "사용자 인증" (의미 단위)
- BAD: "auth.py 파일" (코드 아티팩트)
- BAD: "AuthService 클래스 구현" (구현 수준)

### Rule 2: 2-Layer Context Window

분해 시 로드 범위:
- **Layer 0:** S 자신 (description, links, status)
- **Layer 1:** S의 직계 자식 (이미 존재하는 경우)
- **로드 금지:** 손자, 사촌, 원거리 서브트리

전체 트리를 로드하지 않음 → 로컬 추론 강제 → Context Rot 방지.

### Rule 3: Spider Web Weaving

자식은 고립 생성되지 않는다. 각 자식은 다음으로부터 직조(woven):
- 부모 Span의 의미론
- INFORMED_BY 링크의 외부 지식 (논문, 문서, 도메인 모델)
- 형제 인식 (A3 독립성 유지)
- KG에 이미 존재하는 지식 (기존 Span, Contract, 패턴)

### Rule 4: N:N DAG

DECOMPOSES_TO와 EXPLORES_VIA 모두 다대다(N:N):
- 하나의 Span이 **여러 부모**를 가질 수 있음 (모듈 간 공유 관심사)
- 하나의 부모가 **여러 자식**을 가질 수 있음 (분해 브랜치)
- DAG이며 트리가 아님. **순환 탐지 필수** (A2 termination).

```cypher
-- 순환 탐지 (0행이면 정상)
MATCH path = (s:AptSpan)-[:DECOMPOSES_TO*2..10]->(s)
RETURN [n IN nodes(path) | n.name] AS cycle_nodes
LIMIT 1
```

---

## 6. Context Budget per Span

```cypher
-- Span 생성 시 depth 기반 예산 자동 할당
MERGE (child:AptSpan {name: $name})
SET child.context_budget = CASE
  WHEN child.depth = 1 THEN 50000
  WHEN child.depth = 2 THEN 20000
  ELSE 8000 END
```

AtomicSpan(L3+)은 8K 토큰 예산. 단일 파일 500줄 구현에 적정. 이를 초과하면 Context Rot 시작.

---

## 7. Span Boundary Enforcement

각 AtomicSpan에 `allowed_paths`와 `forbidden_patterns`를 명시. SCW Phase에서 pre-commit hook으로 검증.

```cypher
MATCH (atom:AtomicSpan {name: $atom})
SET atom.allowed_paths = $paths,           -- ['src/module_a/', 'tests/test_module_a.py']
    atom.forbidden_patterns = $patterns    -- ['import module_b', 'from module_c']
```

**allowed_paths:** 이 Span이 수정할 수 있는 파일/디렉토리
**forbidden_patterns:** 이 Span의 코드에서 금지된 import/패턴 (다른 모듈 침범 방지)

---

## 8. SP -> ST 핸드오프 Cypher

C(S) 5조건 + APPROVED_BY + links 전부 충족해야 핸드오프 가능.

```cypher
-- SP->ST Handoff: 모든 조건 검증
MATCH (span:AptSpan {name: $span_name})

-- 조건 1: AtomicSpan 라벨
WHERE span:AtomicSpan

-- 조건 2: s 승인 (executor != reviewer)
WITH span
MATCH (span)<-[approval:APPROVED_BY {criterion: 'sigma'}]-(reviewer:AptAgent)
WITH span, reviewer, approval
MATCH (span)<-[:EXECUTED_BY]-(executor:AptAgent)
WHERE executor.name <> reviewer.name

-- 조건 3: 링크 밀도
WITH span, reviewer, executor
OPTIONAL MATCH (span)-[informed:INFORMED_BY]->()
WITH span, reviewer, executor, count(informed) AS link_count
WHERE link_count >= $min_informed_by

-- 조건 4: 미해결 피드백 없음
WITH span, reviewer, executor, link_count
OPTIONAL MATCH (span)<-[:AFFECTS]-(fb:AptFeedback {resolved: false})
WHERE fb IS NULL

-- 조건 5: 아직 결정화되지 않음
WITH span, reviewer, executor, link_count
WHERE NOT EXISTS { MATCH (span)-[:CRYSTALLIZES_TO]->() }

RETURN span.name AS span,
       reviewer.name AS approved_by,
       executor.name AS executed_by,
       link_count AS links,
       true AS handoff_ready
-- 결과 없으면 핸드오프 차단. 어떤 조건이 실패했는지 확인 필요.
```

---

## 9. SP 관련 에러 사례

### E1 — PH3->PH5 직행 (ST 건너뛰기)

**Context:** Span 분해 후 Contract 없이 바로 코딩 진입. ST 단계를 건너뜀.
**Lesson:** Contract 없는 코딩 = vibe coding. 타입 불일치와 암묵적 가정이 통합 시점에 폭발.
**Guard:** D9 GenerativeFlowOrdering. Phase Detection 쿼리를 구현 전 실행.

```cypher
-- Guard: 구현 전 Contract 존재 확인
MATCH (span:AptSpan {name: $target})
OPTIONAL MATCH (span)-[:CRYSTALLIZES_TO]->(st)-[:HAS_CONTRACT]->(c)
WITH span, c
WHERE c IS NULL
RETURN 'BLOCKED: No Contract for ' + span.name AS error
```

### E10 — s-First Order Waste

**Context:** v10 이전 문제. s(인간 검토)를 먼저 수행하여 자동 검사로 거를 수 있는 것에도 인간 시간 낭비.
**Lesson:** 비용 낮은 자동 검사 우선 → 비싼 인간 검토 절약.
**Guard:** v11 평가 순서: v→t→i→d→s (cheap first).

### E-SP1 — INFORMED_BY 없는 분해 (blind decomposition)

**Context:** 외부 지식 연결 없이 "감"으로 분해. 도메인 지식 부재로 잘못된 구조.
**Lesson:** D4 DenseBeforeContract. 분해 전에 외부 지식 연결 필수.
**Guard:** STEP 1의 Link Density Check가 `links(S) >= config.min_informed_by`를 강제.

### E-SP2 — 단일 자식 분해 (BranchingInvariant 위반)

**Context:** Span을 1개 자식으로 "분해". 실제로는 이름 바꾸기일 뿐.
**Lesson:** A2 min_children >= 2. 1개 자식 = 분해가 아닌 리네이밍.
**Guard:** V3 쿼리로 자동 탐지.

### E-SP3 — 형제 간 DEPENDS_ON (A3 위반)

**Context:** 같은 부모의 자식 Span 간에 DEPENDS_ON 관계 생성.
**Lesson:** A3 SiblingIndependence. 형제 간 의존 = 분해 오류.
**Guard:** V2 쿼리 + STEP 7 Verify Sibling Independence.

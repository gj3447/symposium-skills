# SCW World Reference

> APT v11 SCW Phase 상세 레퍼런스. SKILL.md가 "무엇을 하라"이면 이 문서는 "구체적으로 어떻게"를 제공한다.

---

## 1. TDD Strange Loop + Hoare Analogy (~ not =)

### Strange Loop (Hofstadter)

TDD와 Hoare logic은 서로를 비추지만 어느 쪽도 다른 쪽으로 환원되지 않는다.

```
Contract ~ Hoare triple {P} f {Q}
    |                        ^
    | (specifies)            | (witnesses)
    v                        |
  Tests ~ partial refutation |
    |                        |
    | (drives)               |
    v                        |
  Code ~ constructive witness
```

루프: Contract가 테스트가 검사할 것을 명세 -> 테스트가 코드가 해야 할 것을 주도 -> 코드가 Contract의 만족 가능성을 증거 -> Contract는 테스트와 코드에 대한 이해로부터 작성됨. 고정된 시작점이 없는 자기 강화 순환.

### Analogy Table (~ not =)

| Hoare Logic | APT / TDD | 관계 |
|-------------|-----------|:----:|
| {P} precondition | contract.precondition | ~ |
| f program | SourceCodeNode 구현 | ~ |
| {Q} postcondition | contract.postcondition | ~ |
| 정확성 증명 | 모든 테스트 통과 | ~ |
| 보편 한정(universal) | 유한 테스트 케이스 | != |
| 형식 검증 | 경험적 증거 | != |

**왜 ~ 이고 = 이 아닌가:** Hoare logic은 P를 만족하는 **모든** 입력에 대한 **증명**을 제공. TDD는 테스트된 범위 내에서 반박에 실패한 **증거**를 제공. 통과한 테스트 스위트는 증명이 아니라 테스트된 도메인 내에서의 반증 부재. 이 구별은 근본적이며 생략되어서는 안 된다. APT는 Hoare 유비를 *구조적 안내*(Contract을 어떻게 생각할 것인가)로 사용하지, *정확성 보장*(Lean 4나 Coq 같은 형식 검증 도구가 필요)으로 사용하지 않는다.

---

## 2. FulfillmentGate 7 Checks

ContractMaterialized 수락 전 **모든 7개 검사** 통과 필수. 하나라도 실패하면 게이트 차단.

| # | Check | 상세 설명 |
|---|-------|----------|
| 1 | **All acceptance tests pass** | contract.acceptance_criteria에서 도출된 모든 테스트가 PASS. impact_tests 포함. 단일 FAIL도 차단. 테스트 건너뛰기(skip) 금지. |
| 2 | **Output type matches** | 함수/모듈의 실제 반환 타입이 contract.output_type과 정확히 일치. 동적 타입 언어는 테스트의 런타임 타입 검사로 검증. 구조적 서브타이핑은 문서화 시 허용. |
| 3 | **Pre/postconditions checked in code** | 구현에 명시적 사전조건 검증(assert, raise ValueError)과 사후조건 검증이 존재. 유효하지 않은 입력의 무시(silent ignore) 금지. contract.precondition/postcondition에 대응해야 함. |
| 4 | **KG reference comments present** | 소스 파일에 `# KG: TASK_{name}`과 `# KG: CONTRACT_{name}` 주석 존재. 코드에서 명세로의 추적성 보장. 누락 = 단절된 구현. |
| 5 | **Complexity within threshold** | `lines(source) <= config.complexity_threshold`. 빈 줄과 주석 제외. cyclomatic/Halstead 사용 시 해당 임계값 적용. 초과 시 Span이 충분히 원자적이지 않았음 -> PH3 재분해. |
| 6 | **Test-Contract alignment** | 테스트가 Contract에 명시된 postcondition을 실제로 검증하는지 확인. happy path만 테스트하는 것은 불충분. 자동: 테스트 assertion을 파싱하여 postcondition 술어와 매칭. 수동: 리뷰어가 테스트의 의미성 확인. 동어반복 테스트(tautological) = 실패. |
| 7 | **NFR assertions pass** | Contract의 nfr_* 필드가 설정되어 있으면 해당 벤치마크 통과 필수. latency는 N회 반복의 p99. memory는 peak. accuracy는 N회 반복의 mean. nfr_* 필드가 없으면 자동 PASS. |

---

## 3. TDAD 상세 (arXiv:2603.17973)

### 핵심 통찰

에이전트가 코드를 수정할 때, "전체 테스트 스위트 실행"이 아닌 **어떤 특정 테스트를 실행해야 하는지** 알아야 한다.

**방지하는 문제:**
- **Blind coding:** 무엇이 깨질 수 있는지 모르고 코드 변경
- **Regression amnesia:** 컨텍스트 압축 후 기존 테스트를 잊음
- **Test suite bloat:** 모든 변경마다 전체 스위트 실행은 낭비

### impact_tests 규칙

| # | 규칙 | 설명 |
|---|------|------|
| 1 | **구체성** | 각 항목은 정확한 파일 경로. glob(`tests/*.py`), 디렉토리(`tests/`), "run all tests" 금지 |
| 2 | **비어있지 않음** | 최소 1개 항목. impact_tests 없는 Task는 PH5 진입 불가 |
| 3 | **Baseline 의무** | 코드 작성 전 impact_tests 실행. 모두 PASS 필수. FAIL이면 기존 코드베이스가 이미 깨진 상태 -> 먼저 수정 |
| 4 | **회귀 탐지** | 구현 후 impact_tests 재실행. baseline에서 PASS였던 테스트가 FAIL이면 에이전트가 도입한 회귀 |
| 5 | **추적성** | 각 테스트 파일에 `# KG: CONTRACT_xxx` 주석으로 Contract 추적 |

### NEW_FILE 예외

`contract.target_file`이 아직 존재하지 않을 때:
- `impact_tests = ["NEW_FILE"]` 마커 설정
- Baseline 실행 **건너뜀** (테스트할 기존 코드 없음)
- RED phase는 **필수** -- 실패하는 테스트를 먼저 작성
- 구현 후 `["NEW_FILE"]`을 실제 테스트 경로로 교체:

```cypher
MATCH (task:SemanticTask {name: $task_name})
WHERE task.impact_tests = ['NEW_FILE']
SET task.impact_tests = [$actual_test_path]
```

---

## 4. EDD 상세 (Evidence-Driven Development)

### 5 Criteria

| # | Criterion | 설명 |
|---|-----------|------|
| 1 | **Threshold per test** | 모든 테스트에 명시적 pass/fail 임계값. "예외 없음"이 아닌 구체적 값. 결정적: 정확한 일치/허용오차(`abs(result - expected) < 1e-6`). 확률적: 통계적 경계("95% 신뢰도에서 accuracy >= 0.95"). 임계값 없는 테스트는 EDD 테스트가 아님. |
| 2 | **Repetition count** | 결정적 테스트: `repetitions = 1`. 확률적 테스트: `config.stochastic_repetitions`회 (기본 10). 반복 횟수는 통계적 유의성을 제공하도록 선택: p=0.95, n=10일 때 true accuracy 0.90이면 전부 통과 확률 35% -> 의미 있는 변별력. |
| 3 | **Baseline regression** | `regression(t) = baseline(t).pass_rate - current(t).pass_rate > config.regression_tolerance`. 결정적: tolerance=0.0, 확률적: tolerance=0.05. 회귀 발견 시 ContractMaterialized 차단. |
| 4 | **Cost tracking** | 모든 테스트 실행에 비용 기록: wall-clock time(초), 토큰 소비(LLM-in-the-loop), 리소스 사용(GPU-hours, API calls). AptTestRun 노드에 저장. 예산 집행, 효율 비교, 추세 감지(테스트가 점점 느려짐 = 기술 부채)에 활용. |
| 5 | **CI mandatory** | ContractMaterialized 이벤트가 CI 파이프라인 트리거. CI가 impact_tests를 독립 재실행. 결과를 AptTestRun 노드로 KG에 저장. CI와 에이전트 결과가 5% 이상 발산하면 Contract에 리뷰 플래그. "works on my machine" 방지 + 환경 동등성 보장. |

### Stochastic Repetition 통계적 근거

| True accuracy | P(all pass in 10 runs) | P(all pass in 20 runs) |
|:-------------:|:---------------------:|:---------------------:|
| 1.00 | 1.000 | 1.000 |
| 0.95 | 0.599 | 0.358 |
| 0.90 | 0.349 | 0.122 |
| 0.85 | 0.197 | 0.039 |
| 0.80 | 0.107 | 0.012 |

실용적으로 EDD는 all-pass가 아닌 **threshold 기반**:

```
pass_rate = count(PASS) / repetitions
ASSERT pass_rate >= threshold    // e.g., 0.9
confidence_interval = wilson_score(pass_rate, repetitions, alpha=0.05)
ASSERT confidence_interval.lower >= threshold - margin
```

### AptTestRun 노드 스키마

```cypher
CREATE (run:AptTestRun {
  name:              'TR_' + $contract + '_' + $run_id,
  contract:          $contract_name,
  test_file:         $test_file_path,
  environment:       $env,               -- 'agent_local' | 'ci_linux' | 'ci_gpu'
  trigger:           $trigger,           -- 'implementation' | 'regression' | 'ci_scheduled'
  timestamp:         datetime(),
  -- Results
  total_tests:       $total,
  passed:            $passed,
  failed:            $failed,
  skipped:           $skipped,
  pass_rate:         toFloat($passed) / $total,
  -- Stochastic (null for deterministic)
  repetitions:       $reps,
  mean_metric:       $mean,
  std_metric:        $std,
  ci_lower:          $ci_lower,          -- 95% CI lower bound
  ci_upper:          $ci_upper,
  -- Cost
  wall_time_seconds: $time,
  tokens_consumed:   $tokens,            -- null if no LLM
  gpu_hours:         $gpu,               -- null if no GPU
  -- Regression
  is_regression:     $is_regression,
  baseline_pass_rate: $baseline_rate,
  regression_delta:  $delta
})
WITH run
MATCH (ct:AptContract {name: $contract_name})
MERGE (ct)<-[:TESTS]-(run)
```

### CI 통합

```
ContractMaterialized event
  |
  v
CI Pipeline trigger (apt-edd.yml)
  |-- checkout: $branch
  |-- impact_tests 각각 실행 (pytest --json-report)
  |-- 결과를 AptTestRun으로 KG에 Kafka 경유 저장
  |-- Agent 결과와 CI 결과 비교
  |     |-- divergence > 5% -> Contract review flag
  |     +-- divergence <= 5% -> OK
  v
ContractTestedInCI event 발행
```

### CI Divergence Query

```cypher
MATCH (ct:AptContract)<-[:TESTS]-(agent_run:AptTestRun {environment: 'agent_local'})
MATCH (ct)<-[:TESTS]-(ci_run:AptTestRun {environment: 'ci_linux'})
WHERE agent_run.timestamp > datetime() - duration({hours: 24})
  AND ci_run.timestamp    > datetime() - duration({hours: 24})
  AND abs(agent_run.pass_rate - ci_run.pass_rate) > 0.05
RETURN ct.name AS contract,
       agent_run.pass_rate AS agent_rate,
       ci_run.pass_rate AS ci_rate,
       abs(agent_run.pass_rate - ci_run.pass_rate) AS divergence
ORDER BY divergence DESC
```

---

## 5. Gap Resolution (Thompson Sampling)

### 전체 루프

```
1. Gap 발견 -> AptFeedback 생성 (category: 'Missing')
2. 후보 생성 -> GapCandidate 노드
   - 70% exploitation (KG 내 기존 패턴에서 도출)
   - 30% exploration (신규 접근)
3. 실험 수행 -> 각 후보에 대해 소규모 PoC
4. 점수 업데이트 -> positive/negative 카운트
5. 선택 -> adopt 또는 reject 기준 충족 시 결정
```

### 규칙

| 규칙 | 설명 |
|------|------|
| **70/30 비율** | 후보 생성 시 70% KG 기존 패턴 (exploitation), 30% 신규 접근 (exploration) |
| **3x 금지** | 동일 후보 3회 이상 실험 금지. 데이터 충분 -> 판단 |
| **Adopt 기준** | positive >= 3 AND negative <= 1 -> 채택 |
| **Reject 기준** | negative >= 3 -> 폐기 |
| **중립** | 위 기준 미충족 -> 추가 실험 또는 인간 판단 위임 |

### Cypher

```cypher
-- 후보 생성
MERGE (gap:AptFeedback {name: $gap_name})
SET gap.category = 'Missing', gap.status = 'open'
WITH gap
MERGE (cand:GapCandidate {name: $candidate_name})
SET cand.approach = $approach,
    cand.source = $source_type,  -- 'exploitation' | 'exploration'
    cand.positive = 0, cand.negative = 0,
    cand.trials = 0, cand.status = 'pending'
MERGE (gap)-[:HAS_CANDIDATE]->(cand)

-- 점수 업데이트 (3x 금지 규칙 적용)
MATCH (cand:GapCandidate {name: $candidate_name})
WHERE cand.trials < 3
SET cand.trials = cand.trials + 1,
    cand.positive = CASE WHEN $result = 'positive'
                         THEN cand.positive + 1 ELSE cand.positive END,
    cand.negative = CASE WHEN $result = 'negative'
                         THEN cand.negative + 1 ELSE cand.negative END,
    cand.status = CASE
      WHEN cand.positive + (CASE WHEN $result='positive' THEN 1 ELSE 0 END) >= 3
           AND cand.negative + (CASE WHEN $result='negative' THEN 1 ELSE 0 END) <= 1
      THEN 'adopted'
      WHEN cand.negative + (CASE WHEN $result='negative' THEN 1 ELSE 0 END) >= 3
      THEN 'rejected'
      ELSE 'pending' END,
    cand.last_trial = datetime()

-- Thompson Sampling 선택 (Beta 분포 평균 근사)
MATCH (gap:AptFeedback {name: $gap_name})-[:HAS_CANDIDATE]->(cand)
WHERE cand.status = 'pending' AND cand.trials < 3
RETURN cand.name, cand.approach, cand.source,
       toFloat(cand.positive + 1) / (cand.positive + cand.negative + 2) AS thompson_score
ORDER BY thompson_score DESC
```

> **참고:** 실제 Thompson Sampling은 Beta(positive+1, negative+1) 분포에서 샘플링한다. Cypher에서는 평균값 근사를 사용하고, 실제 샘플링은 애플리케이션 코드에서 수행한다.

---

## 6. Session Startup Protocol (7단계)

매 SCW 세션 시작 시 반드시 수행:

| # | 단계 | 목적 |
|---|------|------|
| 1 | `pwd` 확인 | 작업 디렉토리 올바른지 확인 |
| 2 | `apt-progress.md` 읽기 | 이전 세션 상태 복원 |
| 3 | `git log --oneline -10` 확인 | 최근 커밋 이력으로 맥락 파악 |
| 4 | 미완성 Task 중 최고 우선순위 선택 (1개만) | 단일 Task에 집중 (multi-task = Context Rot) |
| 5 | 해당 Contract 로드 (Progressive Disclosure L3) | Contract 7대 필드 + NFR 확인 |
| 6 | impact_tests 실행 -> 기존 테스트 통과 확인 | TDAD baseline 확보 |
| 7 | 구현 시작 | RED phase부터 (테스트 먼저) |

---

## 7. PH6 Feedback 상세

### 6 Discovery Types

| # | Type | 설명 | Action | Target |
|---|------|------|--------|:------:|
| 1 | **missing_span** | 구현 중 전체 의미 관심사가 분해에서 누락된 것을 발견. 예: API 엔드포인트 구현 중 rate limiting이 어떤 Span에도 없음. 계획 갭, 명세 갭 아님. | AptFeedback 생성, 부모 Span에 링크, PH3에서 형제 Span으로 분해 | PH3 |
| 2 | **contract_gap** | Contract가 형식적으로 올바르지만 불완전. 유효한 입력 케이스를 postcondition이 커버하지 못함. 예: 빈 리스트 입력. Twin을 stale로 표시. | PH4로 돌아가 Contract 수정, acceptance_criteria 추가. Kafka: ContractAmended | PH4 |
| 3 | **type_mismatch** | 실제 데이터 흐름이 선언된 타입과 불일치. 예: `output: float`인데 실제는 `Optional[float]`. 하류 전파 필요: SEQUENCED_WITH 엣지를 따라 영향받는 모든 Contract 업데이트. | 원본 Contract 타입 수정, 다운스트림 전파, 각 영향 Contract 재검증. Kafka: ContractAmended for each | PH4 |
| 4 | **edge_case** | acceptance_criteria에 예상되지 않은 특정 입력 시나리오. contract_gap(구조적 누락)과 달리 특정 데이터 포인트. 예: "이메일 주소에 유니코드 문자". | acceptance_criteria에 추가, 테스트 작성, 실패 시 재구현. 재분해 불필요 | PH4 |
| 5 | **false_positive** | 테스트가 실패하지만 구현은 올바름. 테스트의 기대값이 잘못됨(도메인 오해). 예: 타임스탬프 비교 테스트에서 `created_at == expected` exact 대신 1초 이내 `abs(created_at - expected) < 1`. | 도메인 지식 기반 테스트 assertion 조정. INFORMED_BY 링크로 도메인 인사이트 기록. 이것은 명세 오류, 구현 오류 아님 | PH4 |
| 6 | **accuracy_drift** | 확률적 성능 메트릭이 시간/환경에 따라 저하. 예: dev에서 95% accuracy, prod에서 82%. Span의 의미 범위 재교정 필요. | PH3 수준에서 Span 범위 재평가. 알고리즘 근본 부적합? EXPLORES_VIA 대안? NFR 임계값 비현실적? 재분해 트리거 가능 | PH3 |

### 10 Categories

| # | Category | 설명 | Severity 기준 |
|---|----------|------|:------------:|
| 1 | **Bug** | 코드 결함. postcondition 위반 | P1-P2 |
| 2 | **Confusion** | 명세 모호성. 해석 분기 | P3 |
| 3 | **Missing** | 누락된 Span, Contract, 테스트 | P2-P3 |
| 4 | **Improvement** | 기능 개선 요청 (현재 동작은 정상) | P3-P4 |
| 5 | **Violation** | Axiom 또는 Principle 위반 | P1-P2 |
| 6 | **Conflict** | 두 Contract/Span 간 모순 | P2-P3 |
| 7 | **FalsePositive** | 검증이 정상을 위반으로 오탐. 검증 로직 수정 필요 | P3 |
| 8 | **FalseNegative** | 검증이 위반을 정상으로 미탐. 검증 로직 수정 필요 | P2 |
| 9 | **PerformanceDrift** | 성능 메트릭(정확도, 처리량 등) 기준선 이하 하락. NFR 재교정 + 재실험 | P2-P3 |
| 10 | **SLABreach** | SLA 초과. 응답 시간 또는 처리량 제약 위반 | P1-P2 |

### AptFeedback Cypher

```cypher
CREATE (fb:AptFeedback {
  name:           'FB_' + $project + '_' + $id,
  discovery_type: $type,          -- 6 types 중 하나
  category:       $category,      -- 10 categories 중 하나
  description:    $description,
  source_phase:   'PH5',
  target_phase:   $target,        -- 'PH3' or 'PH4'
  severity:       $severity,      -- 'blocking' | 'degraded' | 'cosmetic'
  status:         'open',
  created_at:     datetime(),
  created_by:     $agent
})
WITH fb
MATCH (span:AptSpan {name: $affected_span})
MERGE (fb)-[:AFFECTS]->(span)
```

**Kafka event:** `FeedbackCreated { feedback: fb.name, type, target_phase, affected_span }`

---

## 8. Anti-Patterns 9개

| # | Anti-Pattern | Signal | Guard | Example |
|---|-------------|--------|-------|---------|
| AP1 | **Gold Plating** | Contract에 없는 기능 추가. "있으면 좋을 것 같아서" 코드 증가 | FulfillmentGate: output_type 일치 검사. Contract 필드에 명시된 것만 구현 | `output_type: str`인데 `Dict[str, Any]` 반환 -> FulfillmentGate 실패 |
| AP2 | **Spec Amnesia** | 코딩 중 Contract 미재열람. 기억에 의존하여 postcondition 누락 | SCW 진입 시 Contract 재로딩 의무화. KG ref 주석으로 추적 | `postcondition: 'len(result) <= 100'` 잊고 무제한 구현 |
| AP3 | **Test Afterthought** | 코드 먼저, 테스트 나중 맞춤. RED 건너뜀 | TDAD RED 단계 FAIL 확인 필수. NEW_FILE도 RED mandatory | 구현 후 테스트가 항상 PASS -> trivial assert만 포함 |
| AP4 | **Silent Patch** | 버그 발견 후 KG 기록 없이 코드만 변경 | AptFeedback 생성 필수 + Kafka FeedbackCreated | 타입 불일치 -> Contract 수정 없이 코드만 변경 -> 나중에 다른 에이전트가 구 Contract 기준으로 코딩하여 충돌 |
| AP5 | **Monolith Creep** | 파일이 500줄 초과로 비대화 | v(복잡도) 게이트 + FulfillmentGate complexity 검사 | 유틸리티 함수 계속 추가 -> 800줄 -> SP 재분해 |
| AP6 | **Vibe Coding** | Contract 없이 "감"으로 코딩. 결정 근거가 KG에 없음 | D9 GenerativeFlowOrdering + Phase Detection 쿼리 | "일단 만들고 Contract 나중에" -> E1과 동일 결과 |
| AP7 | **Self-Approval** | executor = reviewer. "내가 보니까 괜찮다" | V15 쿼리 + Kafka consumer에서 `executor != reviewer` 검증 | 에이전트 A가 Span 작성 + s 승인 -> V15 탐지 -> 승인 무효화 |
| AP8 | **Trivial Tests** | 테스트가 postcondition 미검증. `assert True` 수준 | Test-Contract alignment gate. coverage >= threshold | `def test_parse(): assert parse_args is not None` -> postcondition 검증 안 함 |
| AP9 | **NFR Amnesia** | latency/memory/accuracy 검증 건너뜀. 프로덕션 성능 문제 | D10 NFR as First-Class + FulfillmentGate 7번째 검사 | `nfr_latency_p99_ms: 200` 설정인데 latency 테스트 없이 배포 -> p99 500ms |

---

## 9. KG Reference Comments 규칙

모든 소스 파일에 KG 추적 주석 필수:

```python
# KG: TASK_xxx           <- 이 파일이 구현하는 Task
# KG: CONTRACT_xxx       <- 준수하는 Contract

def my_function(input: InputType) -> OutputType:
    # KG: CONTRACT_xxx (input_type -> output_type)
    ...
```

**규칙:**
- 파일 최상단에 TASK와 CONTRACT 참조
- 핵심 함수 docstring 또는 주석에 Contract 타입 매핑 표기
- FulfillmentGate 4번째 검사에서 존재 확인
- 누락 시 = "단절된 구현" -> 코드에서 명세로의 추적 불가

---

## 10. Kafka Event Publishing

### ContractMaterialized

```json
{
  "event_type": "ContractMaterialized",
  "timestamp": "2026-03-25T14:30:00Z",
  "correlation_id": "uuid",
  "agent": "agent_scw_02",
  "branch": "feature/xxx",
  "payload": {
    "contract": "CT_xxx",
    "task": "TASK_xxx",
    "source_file": "src/xxx.py",
    "target_file": "src/xxx.py",
    "impact_tests": ["tests/test_xxx.py", "tests/test_xxx_convergence.py"],
    "baseline_results": {"tests/test_xxx.py": "PASS (12 tests, 0.3s)"},
    "post_results": {"tests/test_xxx.py": "PASS (18 tests, 0.5s)"},
    "new_tests_added": 6,
    "coverage": 0.87,
    "nfr_results": {
      "latency_p99_ms": 45.2,
      "latency_threshold_ms": 100,
      "accuracy_mean": 0.962,
      "accuracy_threshold": 0.95,
      "repetitions": 10
    },
    "lines": 187,
    "complexity_threshold": 500
  }
}
```

### FeedbackCreated

```json
{
  "event_type": "FeedbackCreated",
  "payload": {
    "feedback": "FB_xxx_001",
    "discovery_type": "contract_gap",
    "category": "Missing",
    "target_phase": "PH4",
    "affected_span": "ATOM_xxx",
    "severity": "blocking"
  }
}
```

---

## 11. SCW -> SP/ST 피드백 핸드오프

### Max Returns + 에스컬레이션

| 조건 | 행동 |
|------|------|
| `return_count <= config.max_returns_per_span` (기본 3) | 정상 피드백 루프: PH3 또는 PH4로 복귀 |
| `return_count > max_returns_per_span` | **인간 에스컬레이션 필수**. 자동 복귀 금지. |

**Severity 기준:**
- Bug/Violation: P1-P2
- Missing/Conflict: P2-P3
- 나머지: P3-P4

### 피드백 라우팅

```
discovery_type: missing_span | accuracy_drift
  -> PH3 (SP 재분해)
  -> 새 Span 생성 -> ST -> 돌아오기

discovery_type: contract_gap | type_mismatch | edge_case | false_positive
  -> PH4 (ST Contract 수정)
  -> Contract 수정 -> 테스트 재작성 -> 돌아오기
```

### 사용 규칙

1. **Silent Patch 금지** -- 코드 변경 시 반드시 AptFeedback 생성
2. **Max returns** -- 동일 Span에 `config.max_returns_per_span`(기본 3) 회 초과 -> 인간 에스컬레이션
3. **Severity 기준** -- Bug/Violation: P1-P2, Missing/Conflict: P2-P3, 나머지: P3-P4
4. **카테고리 정확성** -- FalsePositive/FalseNegative는 검증 시스템 자체의 문제. 검증 로직 수정 필요
5. **PerformanceDrift/SLABreach** -- NFR 관련. Contract의 nfr_* 필드 재교정 + 재실험 트리거

### 피드백 해결 Cypher

```cypher
MATCH (fb:AptFeedback {name: $title})
SET fb.status = 'resolved',
    fb.resolved_at = datetime(),
    fb.resolved_by = $agent,
    fb.resolution = $resolution
RETURN fb.name, fb.status, fb.resolution
```

---

## 12. Contract Lifecycle FSM (SCW 관점)

SCW에서 직접 관여하는 상태 전이:

```
Active --[FulfillmentGate 7 checks pass]--> Fulfilled
Active --[discovery during implementation]--> Amended
Fulfilled --[regression found]--> Amended
Amended --[amendment reviewed]--> Active (재진입)
```

**Kafka events:**
- `ContractMaterialized` (Active -> Fulfilled)
- `ContractAmended` (Active/Fulfilled -> Amended)
- `ContractActivated` (Amended -> Active)

### Fulfilled -> Amended 역전이 트리거

1. **Regression detected:** 다운스트림 Contract 변경이 이 Contract의 테스트를 깨뜨림. 자동 regression runner가 포착.
2. **New requirement:** FULFILLS_REQUIREMENT 링크로 새 요구사항 추가. 현재 구현이 만족하지 못하는 acceptance criteria 추가.
3. **Accuracy drift:** ML/비전 Contract에서 주기적 평가 결과 NFR 임계값 이하 메트릭 저하.
4. **Hardware change:** HardwareContext 노드 업데이트 (새 펌웨어, 새 모델). 현재 구현의 가정 무효화.

### FSM Invariants (SCW 관점)

- Draft -> Fulfilled 직행 금지 -- 반드시 Active를 거침 (리뷰 강제)
- 모든 전이는 Kafka 이벤트 생성 (silent 상태 변경 없음)
- Rejected/Archived는 터미널 상태 -- 나가는 전이 없음 (새 Contract 생성)

---
name: harness
version: 2
description: >
  하네스 방법론 — APT의 설계 철학. "구조가 에이전트를 제약한다."
  Invoke when: APT 구조 설계/검토, Phase 전환 규칙 점검, 에이전트 실패 원인 분석,
  아키텍처 레벨 의사결정, 4축(Inform/Constrain/Verify/Correct) 점검 시.
  Enforces: 4-Axis Model, Architecture-as-Harness, Quality Shift (code→spec),
  구조적 신뢰, 에이전트 실패 시 구조 개선 원칙.
  # KG: ATOM_Skill_harness
---

## 🔗 MIC Binding (SOLID-DIP)

**ROLE**: 철학 레이어 — MIC 설계 배경.
**USES slots**: 참조만 (모든 5 slots 설계 근거 제공)

```cypher
MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})-[:HAS_SLOT]->(s:MethodologySlot)
RETURN s.name, s.role
```

# KG: MIC_v1, lesson-apt-not-truly-jaebaeman-2026-04-14

---

# /harness — 하네스 방법론: 구조가 신뢰를 만든다

> **에이전트가 실패하면 에이전트를 고치지 마라. 구조를 고쳐라.**
> — Bockeler, "Architecture as Harness"

> 출처: `apt-docs/theories/05_harness_theory.md` (MinIO)

---

## 하네스란 무엇인가

Harness = 말에 씌우는 고삐. 말(에이전트)의 능력을 제거하지 않으면서 **방향을 제한**한다.

전통적 접근: 프롬프트 엔지니어링, 파인튜닝 → "에이전트를 더 똑똑하게"
하네스 접근: 구조적 제약, 자동 검증, 피드백 루프 → **"구조를 더 단단하게"**

**패러다임 전환**: Instruction-driven → **Architecture-driven reliability**

---

## 4-Axis Model (4축 모델)

하네스의 4개 축. APT의 모든 설계는 이 4축 중 하나 이상에 해당한다.

```
           Inform (정보 제공)
              ↓
        에이전트에게 충분한 맥락
              ↓
    ┌─────────┼─────────┐
    │         │         │
Constrain   [Agent]   Verify
(경계 제한)  (작업)    (검증)
    │         │         │
    └─────────┼─────────┘
              ↓
          Correct (교정)
              ↓
        피드백으로 개선
```

| 축 | 역할 | APT 구현체 | 없으면 |
|---|---|---|---|
| **Inform** | 에이전트에게 맥락 제공 | KG, docs, Progressive Disclosure | 맥락 없이 코딩 = Vibe Coding |
| **Constrain** | 해 공간의 경계 설정 | Span 분해, Contract 7필드, complexity_threshold | 무한 자유 = 무한 오류 |
| | v24: Gate Check Hook = Constrain축 물질화 | | |
| **Verify** | 결과물 자동 검증 | Taliban 9-lens, Ground Truth, TDD | 고무도장 승인 |
| **Correct** | 피드백으로 개선 | Fractal Feedback, AptFeedback, 프로메테우스 | 같은 실수 반복 |

---

## 4축 진단 프로토콜

에이전트가 실패했을 때, 4축 중 어디가 약한지 진단한다.

### Step 1: 증상 분류

| 증상 | 약한 축 | 처방 |
|------|---------|------|
| 엉뚱한 방향으로 구현 | **Inform** | KG 보강, docs 추가, 프로메테우스 발동 |
| 범위 초과 / Gold Plating | **Constrain** | Contract 경계 강화, Span 재분해 |
| 틀린 코드가 통과됨 | **Verify** | Taliban lens 추가, 테스트 강화 |
| 같은 버그 재발 | **Correct** | Feedback loop 점검, Lesson 기록 |

### Step 2: KG 조회 — 현재 4축 상태

```cypher
// 프로젝트의 4축 건강도 파악
MATCH (anchor:SemanticAnchor {name: $project})

// Inform: KG 노드 밀도
OPTIONAL MATCH (anchor)-[:HAS_SPAN*]->(s)
WITH anchor, count(s) as span_count

// Constrain: Contract 완성도
OPTIONAL MATCH (ct:AptContract) WHERE ct.name STARTS WITH 'CT_' + $project
WITH anchor, span_count, count(ct) as contract_count,
     sum(CASE WHEN ct.status = 'fulfilled' THEN 1 ELSE 0 END) as fulfilled

// Verify: Taliban 결과
OPTIONAL MATCH (vr:ValidationResult) WHERE vr.project = $project
WITH anchor, span_count, contract_count, fulfilled,
     count(vr) as validations,
     sum(CASE WHEN vr.verdict = 'REJECTED' THEN 1 ELSE 0 END) as rejections

// Correct: Feedback 처리율
OPTIONAL MATCH (fb:AptFeedback) WHERE fb.name STARTS WITH 'FB_' + $project
WITH span_count, contract_count, fulfilled, validations, rejections,
     count(fb) as feedbacks,
     sum(CASE WHEN fb.status = 'resolved' THEN 1 ELSE 0 END) as resolved_fb

RETURN span_count AS inform_density,
       contract_count AS constrain_total, fulfilled AS constrain_fulfilled,
       validations AS verify_total, rejections AS verify_rejections,
       feedbacks AS correct_total, resolved_fb AS correct_resolved
```

### Step 3: 처방 실행

| 약한 축 | 조치 |
|---------|------|
| Inform 부족 | `/prometheus` 발동 → 병렬 리서치 → KG 구축 |
| Constrain 부족 | `/apt-sp` 재분해 또는 `/apt-st` Contract 강화 |
| Verify 부족 | `/taliban` 발동 → 누락된 lens 식별 → 검증 강화 |
| Correct 부족 | AptFeedback 미처리 건 해소, Lesson 기록 확인 |

---

## Quality Shift 원칙

> 하네스 시대의 병목은 **코드 품질이 아니라 명세 품질**이다.

```
전통:     코드 작성 능력이 병목 → 더 잘 코딩하려 노력
하네스:   명세 작성 능력이 병목 → Contract를 더 정확하게
```

- 에이전트는 이미 코드를 잘 짠다 (LLM 능력)
- 문제는 **뭘 짜야 하는지 모르는 것** (명세 부재)
- 따라서 Contract의 7필드를 정밀하게 쓰는 것이 최우선

---

## Bockeler 원칙 체크리스트

에이전트 실패 시 아래 질문을 순서대로:

1. **구조가 이 실패를 방지할 수 있었나?** → YES면 구조를 고쳐라
2. **에이전트에게 충분한 정보가 있었나?** → NO면 Inform 축 보강
3. **해 공간이 충분히 좁았나?** → NO면 Constrain 축 강화
4. **검증이 이 오류를 잡았어야 했나?** → YES면 Verify 축 추가
5. **이전에 같은 문제가 있었나?** → YES면 Correct 축 실패

**절대 하지 말 것**: "에이전트 프롬프트를 더 길게 써보자" — 이건 하네스가 아니라 기도.

---

## 다른 방법론과의 관계

```
하네스 (설계 철학) ← APT 전체 구조의 이유
  ├── Inform 축  ← 프로메테우스가 담당 (지식 획득)
  ├── Constrain 축 ← Span + Contract (SP/ST)
  ├── Verify 축  ← 탈레반이 담당 (적대적 검증)
  ├── Correct 축 ← Fractal Feedback + Lesson
  └── 연결 보장  ← 롱기누스가 담당 (KG↔Code 관통)
```

---

## What NOT To Do

| 금지 | 이유 | 대안 |
|------|------|------|
| 프롬프트만 수정해서 해결 시도 | 구조 문제를 지시문으로 해결 불가 | 4축 진단 후 구조 개선 |
| 에이전트 탓만 하기 | "바보 에이전트" = 구조 실패 고백 | Bockeler 체크리스트 |
| 4축 중 하나만 강화 | 밸런스 깨짐 | 4축 균형 진단 |
| 검증 없이 신뢰 | 고무도장 = 구조 부재 | Taliban + Ground Truth |

---

*고삐 없는 말은 빠르지만 방향을 모른다. 하네스는 속도를 줄이지 않으면서 방향을 잡는다.*

---

## 🌱 재배맨 v2 (MIC Slot Reference — 로직 복제 금지)

> 이 스킬의 subagent 운용은 **MIC_v1.SubagentSeeder** slot을 통해 resolve된다.
> 아래는 thin resolver. 로직 복제 = drift 유발.

### Slot Resolve
```cypher
MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})-[:HAS_SLOT]->(s:MethodologySlot {name:'SubagentSeeder'})
RETURN s.currentConcrete, s.invocation, s.protocol
```

### 부모 Pre-fetch (v2 — MCP 우회)
```cypher
MATCH (l:Lesson)-[:HAS_RESEARCH]->(rf:ResearchFinding)
WHERE l.name CONTAINS $keyword RETURN rf.name, rf.domain, rf.oneLineSummary LIMIT 20
MATCH (ts:SubagentTaskSpec {skill:'harness'}) WHERE ts.status='READY'
RETURN ts.name, ts.role LIMIT 10
```

### WorkBuffer 연속성
```cypher
MATCH (wb:WorkBuffer {status:'CURRENT'}) RETURN wb
```

# KG: ATOM_재배맨_v2_harness, SA_methodology_v4_triple_upgrade

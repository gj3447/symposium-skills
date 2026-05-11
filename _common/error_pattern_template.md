# Error Pattern Template (Cross-Skill Shared)

> APT 모든 phase에서 `E-{PHASE}{N}` 에러 사례 기록 시 사용하는 3절 양식. KG `:ErrorPattern` 노드 정전.

---

## 3절 양식 (mandatory)

### Context (무엇이 일어났나)
실제 발견된 시나리오 1–2문장. 추상 표현 금지, 구체적 행동 명시.

### Lesson (왜 그게 문제인가)
근본 원리. 자주 KG의 `:Lesson` 노드 또는 axiom 인용.

### Guard (어떻게 방지하나)
다음에 안 일어나게 하는 자동/반자동 메커니즘. validation query, gate, hook 등.

---

## 작성 예시

### E-SA1: KG 중복 앵커

**Context:** KG 탐색 없이 새 앵커를 생성. 기존 동일/유사 프로젝트 앵커가 이미 존재.

**Lesson:** 앵커 생성 전 KG 탐색 필수. SA의 가장 흔한 실수. 단일 SA가 정체성 인덱스이므로 중복 = 향후 모든 phase가 두 갈래로 갈라짐.

**Guard:** SA Step 1의 KG 탐색을 반드시 선행. MERGE 사용으로 중복 방지. V-SA2 cypher로 사후 탐지:

```cypher
MATCH (sa:SemanticAnchor)
WHERE sa.name CONTAINS $keyword OR sa.description CONTAINS $keyword
RETURN sa.name, sa.description, sa.status
```

---

## Naming convention

```
E-{PHASE_PREFIX}{INDEX} — {short name}
```

| Phase | Prefix | 예시 |
|---|---|---|
| SA | `E-SA` | E-SA1 (KG 중복), E-SA2 (PD 무시), E-SA3 (앵커 없이 SP 진입) |
| SP | `E-SP` | E-SP1 (blind decomposition), E-SP2 (1-child), E-SP3 (형제 의존) |
| ST | `E-ST` | E-ST1 (Contract draft 폐기), E-ST2 (Twin Contract 누락) |
| SCW | `E-SCW` 또는 `AP{N}` | AP1 (Gold Plating), AP2 (Spec Amnesia), ... AP9 |
| _common | `E-PD/CB/PTC/V` | E-PD1 (전체 KG load), E-CB1 (하드코딩), E-PTC1 (전부 보존), E-V1 (정상 잡음) |

---

## KG 결정화

```cypher
MERGE (e:ErrorPattern:AbstractNode {name:'E-'+$prefix+toString($n)+'-'+$shortName})
SET e.phase = $phase,                -- 'SA' | 'SP' | 'ST' | 'SCW' | '_common'
    e.context = $context,
    e.lesson = $lesson,
    e.guard = $guard,
    e.severity = $severity,          -- 'P1' | 'P2' | 'P3' | 'P4'
    e.discoveryType = $discoveryType,-- (선택) PH6 6 discovery type 중 하나
    e.category = $category,          -- (선택) PH6 10 category 중 하나
    e.created_at = datetime(),
    e.created_by = $agent
WITH e
OPTIONAL MATCH (l:Lesson {name:$linked_lesson})
FOREACH (_ IN CASE WHEN l IS NOT NULL THEN [1] ELSE [] END | MERGE (e)-[:GROUNDED_IN_LESSON]->(l))
RETURN e
```

---

## phase별 ErrorPattern 위치

| Phase | references 파일 |
|---|---|
| SA | `apt-sa/references/sa_errors.md` |
| SP | `apt-sp/references/sp_errors.md` |
| ST | `apt-st/references/st_errors.md` (드물면 SKILL.md inline) |
| SCW | `apt-scw/references/anti_patterns.md` (AP1-AP9) |
| _common | 본 폴더의 각 개념 파일 끝 절 (e.g. `progressive_disclosure.md`의 anti-pattern 절) |

---

## anti-pattern (이 양식 자체)

- **E-EPT1: Lesson 없음** — Context와 Guard만. 왜 문제인지 모르면 Guard가 자의적.
- **E-EPT2: Guard 없음** — Context + Lesson만. 다음에 재발 가능.
- **E-EPT3: 추상 Context** — "잘못 분해함". 어떻게? 어떤 입력? Guard 설계 불가.
- **E-EPT4: KG 미결정화** — `:ErrorPattern` 노드 없이 prose만. 다른 phase에서 검색 불가.

# KG: APT_ErrorPattern_template_canonical, CONTRACT_AgentMistakeLog_v1_2026-04-27

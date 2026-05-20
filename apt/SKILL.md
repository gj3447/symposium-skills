---
name: apt
kg_ref: ATOM_Skill_apt_orchestrator
version: "27.1.0"
channel: stable
description: >
  APT v26.1 orchestrator — KG 정본 기반. Gate Check Hook 강제. SA→SP→ST→SCW 순환.
  하네스 4축 + 5대 무기(하네스/나생문/프로메테우스/롱기누스/재배맨) + D(S)/C(S) + Crystallization Frontier.
  v26.1: RFC1 (C(S) ↔ A3 axiom layer 분리 + Greek :ARCHIVED) + RFC2 (two-tier cleanup: local RGR in transitions + global Phase 6) + Apt_FourPlusOne motif.
  v26 A1: MIC slots 10 (ContractSchema/LensSet/MethodologyConfig). A3/A5: LensSet completeness + Cypher enforcement (3-lens shortcut 차단). A6: SKILL.md resolve-only.
  v22: Gate Check enforcement via Claude Code Hook.
  Naesengmoon --lens mathematical 5-round meta-verification 반영 (260✓→102✓ honest convergence).
  Every gate requires: adversarial critic + ground truth + human sigma_oracle + evidence-backed verdicts + post-gate reflection.
  HR11: Every APPROVED verdict MUST cite specific evidence (no RUBBER_STAMP).
  Naesengmoon LensSet pluggable: constitutional / mathematical (KG LensSet 노드 확장).
  피드백은 5대 무기 순환의 창발 속성 (독립 위상 아님).
  Essential ✗: Arrow of Time (order-dependent), Edge of Chaos, Gödel (never complete).
  Optional Lean 4 integration: `lake build` sorry=0 error=0 as ground truth.
  Invoke when: "start work on", "implement", "develop", "what phase am I in",
  "apt check", "validate apt", "auto mode", or any general development request.
  Enforces: phase detection, flow control, adversarial gates, validation V1-V29, feedback system, mandatory reflection.
  # KG: ATOM_Skill_apt_orchestrator, APT_v26_RFC_draft_2026-04-21, lesson-feedback-is-emergent-not-weapon-2026-04-16
---

## 🎛 v26 A6 Resolve-Only Directive

> 본 SKILL.md의 모든 magic number / lens count / contract field count는 KG MethodologySlot 조회로만 해결. Direct prose edit 금지 — KG 노드만 수정.

```cypher
// Config resolve (magic number 대체)
MATCH (cfg:MethodologyConfig {name:'MethodologyConfig_default_v26'}) RETURN cfg.{field}
// LensSet resolve (deprecated lens 차단)
MATCH (ls:LensSet {name:$lensName}) WHERE ls.deprecated <> true RETURN ls.lensCount, ls.minCritics
// ContractSchema resolve (ST phase)
MATCH (slot:MethodologySlot {name:'ContractSchema'})-[:RESOLVES_TO]->(schema) RETURN schema.fields
```

**Resolve targets**: `vibe_coding_sweet_min/max` · `vibe_coding_hard_max` · `lens_min_critics_constitutional` · `min_findings_per_lens` · `span_depth_max` · `context_budget_l1_avg`.

# KG: APT_v26_A6_2026-04-21, MethodologyConfig_default_v26, MIC_v1

---

## 🎛 Cross-Repo Working Pattern (2026-05-19)

> SYMPOSIUM (paper-layer KG 정전) ↔ bhgman_tool (apt-implementation-layer code) 측 layer split. APT skill 호출 시 작업 layer 측 명시:
> - **KG = single canonical truth** (Neo4j on Mac VM, dgx pod worker). Cross-repo session 측에서도 KG 측 단일 entry.
> - **File edit 측 절대경로** mandatory. `~/CD/SYMPOSIUM/...` (paper) ≠ `~/CD/bhgman_tool/...` (tool). Same-layer 비교: ruflo/LangGraph/CrewAI ↔ bhgman_tool only (paper-layer 비교 = category error).
> - **APT-development work** default layer = bhgman_tool. SYMPOSIUM/THEORY 측 paper crystallization (자료집).

# KG: feedback_layer_split_symposium_vs_bhgman_tool / reference_symposium_monorepo_mirror / reference_kg_infra_topology

---

## 🎛 v26.1 Addendum — RFC1 + RFC2 + Apt_FourPlusOne (2026-04-29)

> v26.1은 v26 prose에 손대지 않고 KG slot resolve로만 적용. 본문 한 줄도 직접 magic number 박지 않음 (A6 resolve-only 준수).

### v26.1-A. C(S) predicate ↔ A3 axiom layer 분리 (RFC1)

```cypher
// C(S) = self-containment (한 Span 내부 atomicity 검사)
MATCH (cs:DefinedTerm {name:'APT_Layer_CrystallizationFrontier'}) RETURN cs.description
// 5-predicate: 타입 표현 / 의미 완결 / 구현 / 테스트 / 분해 비경제성

// A3 = sibling-wellformedness (Span 간 관계 검사)
MATCH (a3:KnowledgeNode {name:'APT20_S2_LayerIndependence'}) RETURN a3.description

// Greek 5-predicate (deprecated)
MATCH (greek:KnowledgeNode {name:'APT19_A4_CrystallizationFrontier'})
WHERE 'ARCHIVED' IN labels(greek) RETURN '⚠️ deprecated, use APT_Layer_CrystallizationFrontier'
```

**중요**: C(S)는 *한 Span 내부* 검사 (5-predicate). 형제 Span 간 wellformedness는 *별도 axiom layer* (A3 SiblingIndependence). 한 노드에 섞지 말 것.

### v26.1-B. Two-tier cleanup (RFC2)

```cypher
MATCH (rfc:MethodologyRFC {name:'rfc-apt-two-tier-cleanup-2026-04-29'}) RETURN rfc.proposes
// Local RGR: 각 transition (SA→SP, SP→ST, ST→SCW) 끝에 mini-RGR 3-beat
// Global Phase 6: 4 phase 종료 후 cross-phase 누적 관측 + 4-tool ratchet
```

phase tree에서 transition 3곳에 mini-RGR marker 추가됨. Phase 6은 *유지* — 폐기 아님.

### v26.1-C. Apt_FourPlusOne meta-motif

```cypher
MATCH (m:AptMetaMotif {name:'Apt_FourPlusOne'})<-[:INSTANCE_OF_MOTIF]-(inst)
RETURN m.formal_signature, collect(inst.name) AS instances
// Framework self-similar: C(S) + 5-weapons + 4-phase 모두 4 worker + 1 meta 구조
```

**활용**: 새 컴포넌트 도입 시 4+1 fit 검토. 같은 layer 5번째 = anti-pattern. 5번째는 *다른 layer*여야 함.

# KG: rfc-apt-cs-axiom-visibility-drift-2026-04-29, rfc-apt-two-tier-cleanup-2026-04-29, Apt_FourPlusOne

### v26.1-D. APT essence — S-functor factorization (2026-05-14)

> APT 본질 정리: `F : MeaningSpace^∞ → SourceCode = F_SCW ∘ F_ST ∘ F_SP ∘ F_SA`.
> 4-phase 파이프라인은 *철학적 비유*가 아니라 **Mac Lane CWM II.3 의미의 functor 합성**이다.

```cypher
// Essence canonical
MATCH (e:AptEssence {name:'APT_essence_canonical_2026-05-14'})
RETURN e.factorization, e.lean_proof_path, e.theorem_count
// expected: factorization='F = F_SCW ∘ F_ST ∘ F_SP ∘ F_SA',
//           lean_proof_path='MIND/lean_formalization/APT_FunctorFactorization.lean',
//           theorem_count=12

// Sprint seed
MATCH (s:Span {name:'span-essence-S-functor-2026-05-14'}) RETURN s.status, s.outcome
```

**4 stage-functor** (각각 Aristotle αἰτία 매핑):

| Functor | 출발 | 도착 | Aristotle 원인 |
|---|---|---|---|
| `F_SA`  | MeaningSpace  | AnchorCtx       | Material (질료) |
| `F_SP`  | AnchorCtx     | SpanDecomp      | Formal (형상) |
| `F_ST`  | SpanDecomp    | ContractSchema  | Efficient (작용) |
| `F_SCW` | ContractSchema| SourceCode      | Final (목적) |

**핵심 정리** ([`MIND/lean_formalization/APT_FunctorFactorization.lean`](../../../MIND/lean_formalization/APT_FunctorFactorization.lean), 12 theorem / 0 sorry / Lean 4.29.1 PASS):
- T1 `F_total_well_typed` — `SmallFunctor MeaningSpace SourceCode` 잘 타입됨
- T2 `factorization_associative` — 합성 결합법칙 (obj_map level)
- T3 `factorization_matches_seed` — 정확히 `F_SCW ∘ F_ST ∘ F_SP ∘ F_SA` 와 일치
- T4 `F_total_obj_chain` — 모든 의미 운반체가 SA→SP→ST→SCW 4-stage 결정적 추적
- T5-T8 `F_{SA,SP,ST,SCW}_id` — 각 stage functoriality (id 보존)
- T9 `cardinality_monotonic_4stage` — `|◇P_0| ≥ |◇P_1| ≥ |◇P_2| ≥ |◇P_3| ≥ |◇P_4|` (Hegel Aufhebung)
- T10 `cardinality_endpoints_bound` — Meaning ≥ Code 추이성
- T11 `apt_essence_witnessed` — 6 본질 불변량 동시 witness
- T12 `essence_seed_equation` — essence 등식 `rfl`

**Deferred (TODO-1..6, ~1,030 lines Mathlib-backed sprint)**:
Free category Hom carriers / non-trivial functoriality / monoidal product /
first-principles cardinality drop / Curry-Howard 함자성 / Lakatos excess content.

Sister Lean: `APT_Cycle_Functor.lean` (phase-level, 9 thm — object map) +
`APT_FunctorFactorization.lean` (morphism-level, 12 thm — functor laws, NEW 2026-05-14).

# KG: APT_essence_canonical_2026-05-14, span-essence-S-functor-2026-05-14,
#     apt-philosophical-foundations-2026-05-11

---

## 🧊 Essence Metaphor — Progressive Crystallization (Stefan free-boundary, NOT Avrami stochastic)

> APT 의 본질은 **Progressive Crystallization** — 미정의 의미(amorphous design space)에서 결정화된 단위(AtomicSpan + Contract + Code)로의 *비가역 상전이*. 단, kinetics 측 정전 grounding 은 **Stefan free-boundary problem** 이지 Avrami 가 아니다. (PROM 16 P4.1 finding, 2026-05-14)

### 1. 비유 (metaphor layer — preserved)

Progressive Crystallization 비유는 유지. Span 분해 → C(S) 5-predicate 검증 → AtomicSpan 결정 → Contract 형식화 → SCW 코드 물질화. 미정의 영역에서 결정 영역으로의 *frontier 전진* 이 핵심 직관이며, 이 직관은 Avrami / Stefan / Mehl-Johnson 셋 모두 공유한다 (nucleation → solidification 공통 phenomenology).

### 2. Kinetics grounding — Stefan free-boundary (deterministic, canonical)

| 측면 | APT | Stefan (1891) / Caffarelli (1977) |
|------|-----|-----------------------------------|
| Moving boundary | Crystallization Frontier (AtomicSpan / non-Atomic 경계) | Free boundary Γ(t) (solid / liquid 계면) |
| Driving flux | C(S) 5-predicate 만족 압력 + 외부 knowledge (Prometheus) + adversarial verdict (Naesengmoon) | Temperature gradient ∇T / latent heat flux |
| Regularity | Atomic 격상 시 sibling-wellformed (A3) — discrete smoothness | Caffarelli 1977: Γ(t) 가 1-dimensional Hausdorff measure 측 smooth (higher-dimensional generalization) |
| Determinism | 주어진 SA + cfg → frontier evolution 일의적 | PDE 측 결정적 (initial+boundary condition fixed → unique weak solution) |

**Crystallization Frontier = Stefan moving boundary** (discrete lattice → continuum 변형 측 적용). Caffarelli 1977 regularity 결과는 frontier 가 임의 fractal 이 아닌 *smooth* (적절한 measure 의미) — 이것이 APT 측 "AtomicSpan 결정 후 sibling 간 wellformedness 보존" 의 수학적 거울.

### 3. Avrami 측 위치 — partial / metaphor only

Avrami (1939-1941, J Chem Phys 7-9) 측 KJMA equation $X(t) = 1 - \exp(-K t^n)$ 은 *stochastic Poisson nucleation* 모델이다. APT 는 nucleation 이 *결정적* (사용자 SA + cfg → SP 가 부모 Span 의 유일 자식 집합 결정) — Avrami 측 random nucleation rate 가정 위배. 따라서:

- **Avrami = metaphor 측 partial cite** (nucleation→growth phenomenology 공유)
- **Stefan + Caffarelli = kinetics 측 canonical grounding** (deterministic moving boundary)

P4.1 finding (PROM 16, 2026-05-14): Avrami ↔ APT 매핑 confidence 0.87 (metaphor) / 0.45 (kinetics). Kinetics 측 적합도가 낮은 이유 = stochastic 가정 mismatch. Stefan 측 매핑은 deterministic axis 측 0.92+ (estimated).

### 4. ✗ DEPRECATED — Annealing / Refactoring 매핑

P4.1 finding 측 0.45 약 매핑 "**refactoring = thermodynamic annealing**" 은 **폐기**. 이유:

1. Refactoring 은 thermodynamic equilibration *아님* — 외부 verdict (test/critic) driven, 내부 free-energy minimization 아님
2. Annealing 은 *reversible* (재가열 → 재결정), refactoring 은 *비가역* (git history 측 monotone, 정정 commit 으로만 진행)
3. Annealing temperature schedule 은 simulated annealing 측 알고리즘적 metaphor 로 빌릴 수 있으나, **APT cleanup phase 6 의 4-tool ratchet 은 annealing 이 아닌 monotone ratchet** (Lakatos progressive shift, 비가역)

→ **annealing-refactoring-metaphor 측 future SOURCES.md 인용 금지**. cleanup phase 본질 = monotone ratchet, not thermodynamic annealing.

### 5. 학문 인용

| Citation | Role |
|----------|------|
| Stefan J (1891) "Über die Theorie der Eisbildung..." Annalen der Physik 278:269-286 | Original Stefan problem formulation (one-phase moving boundary) |
| Caffarelli LA (1977) "The regularity of free boundaries in higher dimensions" Acta Mathematica 139:155-184 | Free boundary regularity (1-dim Hausdorff smoothness) — **canonical kinetics grounding** |
| Avrami M (1939) J Chem Phys 7:1103; (1940) 8:212; (1941) 9:177 | KJMA kinetics (Poisson nucleation) — **partial / metaphor only** |
| Mehl RF, Johnson WA (1939) Trans AIME 135:416 | Mehl-Johnson crystallography parallel formulation (partial cite) |
| PROM_16 P4.1 finding (2026-05-14) | Avrami 0.87 metaphor / 0.45 kinetics, Stefan canonical 격상 동인 |

# KG: stefan-free-boundary-grounding-2026-05-14, APT_essence_canonical_2026-05-14
# KG (cite partial): avrami-kjma-metaphor-partial-2026-05-14 (deprecated for kinetics, preserved for phenomenology)
# KG (deprecated): annealing-refactoring-metaphor-DEPRECATED-2026-05-14

---

## 🔗 MIC Binding (SOLID-DIP) — 재배맨 진짜 구조

> 본 skill의 5대 무기 참조는 **concrete 이름 대신 MethodologySlot 조회**로 호출.
> Treasure 교체 시 `MIC_v1` 노드만 수정 → 본문 무수정.

**IS slot**: Orchestrator (5대 무기 조율)
**USES slots**: Harness, ResearchProvider, AdversarialValidator, KgCodeBinder, SubagentSeeder
**참고**: MetaVerifier는 AdversarialValidator(Naesengmoon)의 --lens mathematical로 통합. FeedbackProvider는 창발 속성(슬롯 아님).

**동적 resolution**:
```cypher
MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})-[:HAS_SLOT]->(s:MethodologySlot)
RETURN s.name, s.currentConcrete, s.invocation
```

본문의 `Prometheus`/`Naesengmoon`/`Longinus`/`재배맨` 등은 MIC slot의 **현재 스냅샷**. 진짜 호출은 `s.invocation`.
88-Naesengmoon은 별도 concrete가 아니라 `Naesengmoon --lens mathematical`. MetaVerifier 슬롯은 Naesengmoon의 렌즈셋으로 통합됨.
피드백은 5대 무기 순환의 창발 속성 — FeedbackProvider 슬롯은 EMERGENT 상태.
# KG: lesson-feedback-is-emergent-not-weapon-2026-04-16, lesson-taliban-lens-pluggable-refactor-2026-04-16

# KG: MIC_v1, lesson-apt-not-truly-jaebaeman-2026-04-14

---

## 🛠 5무기 Phase Integration Matrix — Active Weapon Calls (NEW 2026-05-14)

> **APT 는 indirect MIC slot reference 만으로는 살아있지 않다.** 각 phase 가 *어느 무기*를 *어느 step*에서 *어떻게* 호출하는지 명시적이지 않으면 5무기는 dormant slot 으로 남는다. 본 섹션은 그 활성 호출망을 1:1 표화한 *integration matrix*. MIC slot indirect → 명시적 invocation pattern 으로 격상.

### A. Integration Matrix — Phase × Weapon × Step × Invocation

| Phase | Primary Weapons | Step in Phase | Invocation Pattern | Output |
|-------|----------------|---------------|--------------------|--------|
| **SA** (1/5) | **Prometheus** + **Longinus** | Step 1 KG 탐색 / Step 2 anchor 결정 / Step 3 5 core fields | `/prom <N> "<sa_topic>"` (지식 선행) + Longinus L1-L2 reverse binding (KG anchor → 기존 SemanticAnchor 후보) | `SemanticAnchor` 노드 + `ResearchFinding` N 개 (verified=true) + L1-L2 ReferenceSite |
| **SP** (2/5) | **재배맨** + **Naesengmoon** | Step 4 D(S) 재귀 분해 / Step 5 wave_index 할당 / Step 6 C(S) 5-predicate gate | `재배맨` SubagentTaskSpec seed per Span (parallel decomposition) + `/tlb <SPAN> --lens constitutional` per Crystallization Frontier 진입 후보 | `Span` DAG (모든 leaf = `AtomicSpan`) + `VerdictRecord` per gate |
| **ST** (3/5) | **Longinus** + **재배맨** | Step 7 Contract DTO 결정화 / Step 8 ReferenceSite 7-tuple binding / Step 9 1:1:1:1 (AtomicSpan : Contract : Task : Seed) | Longinus L3-L4 binding (Contract → AtomicSpan ReferenceSite) + 재배맨 per-AtomicSpan SubagentTaskSpec seed (TDD RED → GREEN test 4-tuple) | `Contract` (DbC 4-측면) + `SemanticTask` + `SubagentTaskSpec` (per AtomicSpan) + Longinus 7-tuple |
| **SCW** (4/5) | **재배맨** + **Naesengmoon** + **Longinus** | Step 10 wave dispatch (single-message N parallel) / Step 11 RED→GREEN→REFACTOR / Step 12 Code→KG ref comment / Step 13 FulfillmentGate | 재배맨 single-message parallel `Task` dispatch (max=`parallel_max_agents`) + Longinus L5-L7 forward binding (Code → KG ref `# KG: <node>` comment) + `/tlb` FulfillmentGate 7-check | `SourceCodeNode` (with `# KG:` refs) + `MATERIALIZES` edges + Naesengmoon `FulfillmentGate` verdict |
| **MetaReview** (5/5) | **Naesengmoon** + **Prometheus** | Step 14 의심 발견 / Step 15 Lesson 결정화 / Step 16 SKILL.md 패치 / Step 17 Naesengmoon Gate 자체재검증 | `/tlb <MetaReview output> --lens constitutional` (rubber-stamp 방지) + `/prom <small N> "<lesson_topic>"` (lesson distillation, 외부 정전 grounding) | `Lesson` node + SKILL.md MIC slot patch + `VerdictRecord` Naesengmoon gate APPROVED |
| **Cleanup** (6/5, RFC2) | **Harness** + **Naesengmoon** | Step 18 3-tier package audit / Step 19 4-tool ratchet / Step 20 folder-level CCP/ADP gate | Harness 3-tier (IDE-host / runtime / managed) 매핑 진단 + `/88-taliban <folder>` mathematical lens (CCP/CRP/REP/ADP/SDP/SAP folder-level audit) + `tach + complexipy + lizard + vulture + deptry` 4-tool ratchet | `CleanupVerdict` (PASS/NEEDS_REFACTOR/BLOCK) + Harness tier 라벨 + folder-level Lesson |

### B. Cypher Snippet — Weapon Invocation per Phase

```cypher
// SA phase: Prometheus 호출 (knowledge pre-fetch via MIC ResearchProvider slot)
MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})
      -[:HAS_SLOT]->(s:MethodologySlot {name:'ResearchProvider'})
RETURN s.currentConcrete AS weapon, s.invocation AS pattern
// expected: weapon='Prometheus', pattern='/prom <N> "<topic> — <subgoal>"'
// trigger: SA Step 1 (KG sparse: INFORMED_BY < density_min_informed_by) OR Step 3 (new SemanticAnchor 5 core fields 미충족)

// SA phase: Longinus 호출 (KG anchor binding via 7-Layer Reference slot)
MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})
      -[:HAS_SLOT]->(s:MethodologySlot {name:'KgCodeBinder'})
RETURN s.currentConcrete AS weapon, s.invocation AS pattern
// expected: weapon='Longinus', pattern='L1-L7 ReferenceSite 7-tuple binding'
// trigger: SA Step 2 (anchor 재사용/브랜치 결정 시 기존 SemanticAnchor 후보 reverse scan)

// SP phase: 재배맨 호출 (Span DAG decomposition seed via SubagentSeeder slot)
MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})
      -[:HAS_SLOT]->(s:MethodologySlot {name:'SubagentSeeder'})
RETURN s.currentConcrete AS weapon, s.invocation AS pattern
// expected: weapon='재배맨/JaebaeMan', pattern='SubagentTaskSpec UNWIND batch, parent Pre-fetch → Dispatch → Collect → Write'
// trigger: SP Step 4 (D(S) recursive decomposition — 자식 Span 후보 N 개 parallel research)

// SP phase: Naesengmoon 호출 (Crystallization Frontier 진입 gate via AdversarialValidator slot)
MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})
      -[:HAS_SLOT]->(s:MethodologySlot {name:'AdversarialValidator'})
MATCH (ls:LensSet {name:'constitutional'}) WHERE ls.deprecated <> true
RETURN s.currentConcrete AS weapon, s.invocation AS pattern, ls.lens_count AS lens_count
// expected: weapon='Naesengmoon', pattern='/tlb <SPAN_id> --lens constitutional'
// trigger: SP Step 6 (Span → AtomicSpan 격상 후보 C(S) 5-predicate gate 진입)

// ST phase: Longinus 호출 (Contract → ReferenceSite 7-tuple binding)
MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})
      -[:HAS_SLOT]->(s:MethodologySlot {name:'KgCodeBinder'})
RETURN s.currentConcrete AS weapon, s.invocation AS pattern
// trigger: ST Step 8 (Contract 결정화 직후 AtomicSpan 측 ReferenceSite 7-tuple 작성 — name/kind/source/target/cardinality/label/provenance)

// ST phase: 재배맨 호출 (per-AtomicSpan 1:1:1:1 Contract+Task+Seed)
// trigger: ST Step 9 (Crystallization Frontier 통과 후 AtomicSpan 마다 SubagentTaskSpec seed 자동 생성, TDD RED 작성용)

// SCW phase: 재배맨 wave dispatch (single-message N parallel Task call)
MATCH (cfg:MethodologyConfig {name:'MethodologyConfig_default_v26'})
RETURN cfg.parallel_max_agents AS max_parallel, cfg.parallel_strategy AS strategy
// trigger: SCW Step 10 (wave_index 같은 SubagentTaskSpec batch → single-message Task() dispatch)

// SCW phase: Longinus Code→KG ref comment (forward binding L5-L7)
// trigger: SCW Step 12 (GREEN 통과 후 코드 작성 시 모든 함수/클래스에 `# KG: <node_name>` 주석 강제)

// SCW phase: Naesengmoon FulfillmentGate 7-check
MATCH (ls:LensSet {name:'constitutional'}) RETURN ls.lens_count
// trigger: SCW Step 13 (cargo test PASS + 7-check: executor!=critic / LensSet completeness / prior VR APPROVED / Contract 4-측면 / 코드 KG ref / impact_tests / fat-file ratchet)

// MetaReview phase: Naesengmoon 자체재검증 + Prometheus lesson distillation
MATCH (s1:MethodologySlot {name:'AdversarialValidator'}),
      (s2:MethodologySlot {name:'ResearchProvider'})
RETURN s1.invocation AS taliban_call, s2.invocation AS prometheus_call
// trigger: MetaReview Step 17 (Lesson 결정화 후 Naesengmoon Gate 통과 + 외부 정전 grounding 측 Prometheus mini-run)

// Cleanup phase: Harness 3-tier + Naesengmoon folder-level audit
MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})
      -[:HAS_SLOT]->(s:MethodologySlot {name:'Harness'})
RETURN s.currentConcrete AS weapon, s.invocation AS pattern
// expected: weapon='Harness', pattern='3-tier instance routing (L_MC/L_RT/L_IDE)'
// trigger: Cleanup Step 18 (폴더 구조 ↔ Harness 3-tier 매핑 진단)

MATCH (ls:LensSet {name:'mathematical'}) WHERE ls.deprecated <> true RETURN ls.lens_count
// trigger: Cleanup Step 19-20 (88-taliban mathematical lens 측 folder-level CCP/ADP audit)
```

### C. KnowledgeHub Cross-Link (Active Hub Resolve)

> 본 matrix 측 각 weapon 측 정전 hub 노드는 KG 측 `hub-*` KnowledgeHub 노드. SKILL.md drift 시 hub 측 resolve 로 대체.

```cypher
// 5 weapon hubs (canonical entry points)
MATCH (h:KnowledgeHub) WHERE h.name STARTS WITH 'hub-'
  AND h.name IN [
    'hub-prometheus-research',
    'hub-jaebaeman-sop',
    'hub-taliban-immunity',
    'hub-longinus-reference',
    'hub-harness-3tier'
  ]
RETURN h.name AS hub, h.canonical_skill AS skill_path, h.essence AS essence_one_liner
ORDER BY h.name
```

| Hub | Skill path | Essence (one-liner) |
|-----|------------|---------------------|
| `hub-prometheus-research` | `SKILLS/prometheus/SKILL.md` | 지식-행동 spiral (Hegel reframe), N parallel subagent UNWIND batch |
| `hub-jaebaeman-sop` | `SKILLS/jaebaeman/SKILL.md` | Subagent Orchestration Protocol — KG 측 SubagentTaskSpec 씨앗 기반 |
| `hub-taliban-immunity` | `SKILLS/taliban/SKILL.md` | 적대적 검증 GAN-D, LensSet 플러거블 (constitutional/mathematical/solid) |
| `hub-longinus-reference` | `SKILLS/longinus/SKILL.md` | 7-Layer Reference Model + BX Lens Laws, KG ↔ Code 양방향 binding |
| `hub-harness-3tier` | `SKILLS/harness/SKILL.md` | Industry agent scaffolding 3-tier (IDE-host / runtime / managed) sibling family |

### D. Phase Transition mini-RGR — Weapon Call Trigger (RFC2 v26.1)

> Two-tier cleanup 측 *local* mini-RGR (RFC2) 도 5무기 측 호출 trigger 가 박혀있다. transition 측 RED/GREEN/REFACTOR 3-beat 각각 어느 무기 호출:

| Transition | RED beat | GREEN beat | REFACTOR beat |
|-----------|----------|-----------|---------------|
| SA → SP | (없음 — SA 결정화 직후) | Naesengmoon `--lens constitutional` (SA 5 core fields 완전성 gate) | 재배맨 (SP Span 첫 분해 SubagentTaskSpec seed) |
| SP → ST | Naesengmoon prior contract conflict 검사 | Naesengmoon Crystallization Frontier gate (모든 leaf=AtomicSpan) | Longinus 중복 ReferenceSite 통합 |
| ST → SCW | Naesengmoon prior code conflict 검사 (file move/delete plan) | 재배맨 wave dispatch GO/NO-GO | Harness 3-tier file placement audit (atomic-span dump 평면 누적 차단) |

### E. Anti-Pattern — Weapon Bypass Failure Modes

| Anti-pattern | Phase | 위반 무기 | 위반 결과 | 정정 |
|--------------|-------|-----------|-----------|------|
| KG-skip framing (R1-R5 미수행) | 임의 | Prometheus | 외부 정전 grounding 없는 가설 | `MIC_v1.ReasoningProtocol → KGFirstCheck_v1` 강제 |
| Same-model critic | Gate 전체 | Naesengmoon | Rubber-stamp 자기재검증 | HR3 (Critic model differs from design model) |
| No KG ref comment | SCW | Longinus | Code orphan, drift detect 불가 | SCW Step 12 강제 `# KG:` 주석 |
| Sequential Task dispatch | SCW | 재배맨 | wave-batch ≠ true parallel | single-message N Task() in one assistant turn |
| Folder flat dump | Cleanup | Harness | CCP/ADP 위반, 평면 누적 | 4-tool ratchet + 3-tier 매핑 진단 |
| Self-application | MetaReview | Naesengmoon | 무한 recursion (max_depth=1, delta=0) | `self_application_forbidden=true` 강제 |

# KG: hub-prometheus-research, hub-jaebaeman-sop, hub-taliban-immunity, hub-longinus-reference, hub-harness-3tier, MIC_v1, lesson-feedback-is-emergent-not-weapon-2026-04-16

---

## 🏛 Metaphysical Grounding — Aristotelian Hylomorphism (ὕλη / μορφή)

> **APT 의 vertical reduction = hylomorphic specification, NOT Platonic methexis (분유, μέθεξις).**
> 이전 prose 에 암묵적으로 깔려 있던 *transcendent participation* metaphor 를 Aristotelian *form-and-matter* (form impressed onto matter) 로 reframe. PROM_16 P1.4 finding (Plato methexis SUGGESTIVE_NOT_STRICT, confidence 0.68) 권고에 따른 grounding 교체.

### A. Why Aristotle, NOT Plato

| 측면 | Plato (methexis, 분유) | Aristotle (hylomorphism, 질료형상론) | APT 매핑 적합도 |
|------|------------------------|------------------------------------|---------------|
| Form 위치 | *Transcendent* — separate realm (κόσμος νοητός) | *Immanent* — form-IN-matter (synolon σύνολον) | APT form (Contract/Spec) 은 코드 옆에 살아있음 → Aristotle |
| Ontic vs epistemic | Form = ontic prior, copy is degraded | Form = matter의 organizing principle, no degradation | APT Contract 는 코드보다 "더 실재" 가 아님, 조직 원리 → Aristotle |
| 변화 모델 | Static participation (도) | Progressive impression (운동/δύναμις → ἐνέργεια) | APT phase transition 은 progressive → Aristotle |
| Gap 회피 | "Third Man" 무한 후퇴 (Parmenides 132a-b) | substance = matter+form 단일체 | APT 는 SA↔SCW gap 없음 → Aristotle |
| 변형 작용자 | Demiurge (외부) | Telos + craftsman (내재) | APT orchestrator = craftsman (immanent) → Aristotle |

**결론**: APT 는 *deliberate design* — form (intention/spec) 이 matter (code/artifacts) 에 progressively impressed. Plato 의 transcendent-immanent gap 없음. ⇒ **hylomorphism 이 정확한 metaphysical grounding**.

### B. APT Phase ↔ Hylomorphic Stages

```
SA  (form-pure intention)           ⇔  μορφή as εἶδος (pure form, before matter)
                                       SemanticAnchor = telos + objective + keyAssertion
                                       still abstract; no material substrate yet
        │ form begins to impress
        ▼
SP  (form articulates structure)    ⇔  εἶδος → δύναμις (form actualizing potency)
                                       Span DAG = formal-cause skeleton
                                       matter (codebase potential) responds via D(S) decomposition
        │ form crystallizes leaves
        ▼
ST  (form fully crystallized)       ⇔  μορφή as λόγος (rational structure)
                                       Contract = DbC (pre/post/inv/type) = 4 형상측면
                                       AtomicSpan = form ready to receive specific matter
        │ form impressed onto matter
        ▼
SCW (matter fully receives form)    ⇔  σύνολον (synolon) — concrete substance
                                       form (Contract) + matter (source code) = unified entity
                                       Aquinas ST I q.75 a.4: forma dat esse — form gives being
        │ ratchet/cleanup
        ▼
PH6 (formal cause achieves ἐνέργεια) ⇔ τελός (telos) reached, actuality (ἐνέργεια) realized
                                       Phase 6 Cleanup Gate = 4-tool ratchet (potency→act remainder)
```

**Vertical reduction = hylomorphic specification** (NOT Platonic participation). 매 phase 는 form 의 progressive impression — form 의 *layer 외부 transcendent copy* 가 아니라 *layer 내부 articulation*.

### C. Contract = Form (4 측면, DbC mapping)

Contract (SemanticTwin 의 핵심) 는 Aristotle's μορφή 의 4 측면을 그대로 implement (apt-st §C 참조):

| DbC field | Aristotle 측면 | 의미 |
|-----------|-------------|------|
| `input_type` / `output_type` | **εἶδος (eidos)** — formal cause | 무엇인가 (what-it-is, τὸ τί ἦν εἶναι) |
| `precondition` | **ὕλη-readiness** — material cause prerequisite | matter 가 form 을 받기 위해 만족해야 할 조건 |
| `postcondition` | **τελός (telos)** — final cause | form 이 matter 에 완전히 impressed 되었을 때의 상태 |
| `invariant` (semantic_meaning 의 결정화) | **οὐσία (ousia)** — substance, persistent identity | form-matter unity 가 시간 가로질러 유지하는 본질 |

→ Contract = "form" 의 4-face. 4 DbC fields 가 모두 채워져야 Contract = complete form. precondition 빈약 = matter prerequisite 불명 = form-receiving 실패.

### D. Vertical Reduction Operator (formal)

```
Define R : Phase_{n} → Phase_{n+1}  (reduction operator)
  R(SA)  = SP   : telos → formal-cause skeleton (form articulates)
  R(SP)  = ST   : skeleton → λόγος + DbC (form crystallizes)
  R(ST)  = SCW  : form → σύνολον (matter receives form)
  R(SCW) = PH6  : potency → ἐνέργεια (telos achieved)

Hylomorphic invariant (NOT participation):
  ∀n. form(Phase_n) is *constitutive of* matter(Phase_{n+1})
                  is NOT *participated in by* matter(Phase_{n+1})
```

cf. Plato `Phaedo` 100c-d: "the beautiful itself, by participation in which all other beautiful things are beautiful" — *participation* model. APT 는 *constitution* model. 차이: Plato 의 form 은 copy 와 외부 분리, Aristotle 의 form 은 matter 의 organizing principle (내부).

### E. Academic Citations

- **Aristotle, *Metaphysics* VII-IX** — Books Ζ (Zeta), Η (Eta), Θ (Theta). Ross, W. D. (trans.). *Aristotle's Metaphysics*. Oxford Classical Texts (revised text, 1924; Clarendon Aristotle Series commentary, 1971). Z.7 1032a12-15 (form-matter unity), Z.17 1041a6-b33 (substance as form-of-matter), H.6 1045a23-b23 (matter+form unity, no third entity needed), Θ.8 1049b5-1050a23 (δύναμις → ἐνέργεια).
- **Aquinas, *Summa Theologiae* I q.75-77** — *De homine* (form-and-matter applied to human substance). Especially q.75 a.4 ("Whether soul and man are the same"): *forma dat esse* (form gives being); q.76 a.1 ("Whether the intellectual principle is united to the body as its form"): substance = single form-matter composite. Blackfriars edition, vol. 11 (Latin/English).
- **PROM_16 P1.4 finding** (2026-05-14) — Plato methexis ↔ APT vertical reduction mapping evaluated as SUGGESTIVE_NOT_STRICT (confidence 0.68). Recommendation: replace with Aristotelian hylomorphism to avoid transcendent/immanent gap and ontic/epistemic gap. KG: `prom16-p14-methexis-suggestive-finding-2026-05-14`.
- **Cross-canon support** — APT v27 의 6-canon convergence framework 에 Aristotle 이 이미 hard-grounded 되어 있음 (iter 663-665 cross-comparison sprint). Hylomorphism 은 4 cause 중 formal + material cause 의 통합 operationalization — APT 측 사전 정착 grounding 의 explicit 부분.

# KG: aristotle-hylomorphism-grounding-2026-05-14, prom16-p14-methexis-suggestive-finding-2026-05-14, APT_essence_canonical_2026-05-14

---

## ⚙ Engineering Analogy Reframe — Compiler IR Passes (PARTIAL_STRUCTURAL_ISOMORPHISM, NOT identity)

> APT phase chain (SA→SP→ST→SCW→PH6) 과 compiler IR pass pipeline (Frontend→AST→HIR→MIR→LIR→Codegen) 사이의 매핑은 자주 등장하는 직관이지만 **identity 가 아니다**. PROM 16 P3.1 finding (2026-05-14): **PARTIAL_STRUCTURAL_ISOMORPHISM confidence 0.72** — 표면적 5-단계 pipeline 형태는 유사하나 5 fundamental difference 가 존재. *agent-centric planning cycle* 은 *product-centric compiler architecture* 와 **직교 (orthogonal)** 한다.

### 1. 공유되는 표면 구조 (why the analogy keeps surfacing)

| 측면 | APT | Compiler (e.g., LLVM, GCC, MLIR) |
|------|-----|----------------------------------|
| Phase chain | SA → SP → ST → SCW → PH6 | Frontend (Parse) → HIR → MIR → LIR → Codegen |
| Lowering | abstract intention → typed contract → code | source AST → SSA IR → machine code |
| Gate-keeping | adversarial Naesengmoon + C(S) predicate | type-check + lint + verifier passes |
| Multi-representation | Span DAG / Contract / AtomicSpan / Code | AST / HIR / MIR / LIR / asm |

→ 표면적으로는 "high-level → low-level progressive lowering" 동일 phenomenology. 그러나 핵심 5 차원이 모두 다르다.

### 2. 5 Fundamental Differences (NOT identity, P3.1)

| # | 측면 | APT | Compiler IR | Divergence 의미 |
|---|------|-----|-------------|----------------|
| D1 | **Direction** | **Bidirectional** — SCW 의 발견이 SA/SP 재구성 trigger (meta-review feedback loop, Naesengmoon verdict driven backflow) | **Unidirectional** — IR pass 는 monotone lowering (HIR→MIR backflow 없음, 한 방향 압축) | APT 는 *iterative dialogue*, compiler 는 *batch transform* |
| D2 | **Contract semantics** | **Design-by-Contract** — pre/post/invariant/type 4 측면 (Aristotelian 4-form face, Eiffel/Meyer 1992 lineage) | **Syntactic types** — 주로 nominal type system + SSA def-use, semantic invariant 부재 (LLVM `nsw`/`nuw` 같은 narrow flag 정도) | APT Contract = behavioral specification, compiler type = structural well-formedness |
| D3 | **SA 위치** | **SA 존재** — telos/objective/keyAssertion/C_S/contextBudget 의 *human intention* 선행 phase | **SA 부재** — 입력은 이미 작성된 source file 그 자체, telos 외부화 (개발자 머릿속) | APT 는 *intent-rooted*, compiler 는 *artifact-rooted* (telos 는 입력 외부) |
| D4 | **TDD loop** | **SCW human-in-the-loop TDD** — RED→GREEN→REFACTOR + human verdict (sigma_oracle HR2) | **Automated batch** — pass 는 deterministic 함수, human verdict 없음 (CI 외부에서 별도 검증) | APT 는 *socio-technical*, compiler 는 *purely technical* |
| D5 | **Centric** | **Agent-centric** — orchestrator/critic/researcher 의 *역할 분리* + adversarial dialectic 이 phase 전이의 동력 | **Product-centric** — IR 자체가 주체, pass 는 transform function (Frances Allen 1970 control flow analysis 유산) | APT 는 *agent process*, compiler 는 *value transformation* |

### 3. Why the orthogonality matters

5 차원 모두 다르다는 사실은 매핑이 "약함 (weak)" 이 아니라 **카테고리 자체가 다름 (orthogonal categories)** 을 의미한다:

- Compiler IR pipeline = **product** (artifact transformation, batch, unidirectional, syntactic, automated, product-centric)
- APT phase chain = **process** (agent dialectic, iterative, bidirectional, semantic, human-in-the-loop, agent-centric)

→ "APT 는 compiler 다" 는 *카테고리 오류* (category error). "APT 가 compiler 와 비슷한 *형태* 를 가진다" 정도가 정확. 0.72 confidence 는 표면 형태 측 partial isomorphism 이지 **deep equivalence 아님**.

### 4. 사용 가이드라인

- ✓ **허용**: phase pipeline phenomenology 측 직관 보조 (high→low progressive lowering 의미 전달용 metaphor)
- ✓ **허용**: AST/MIR 같은 multi-representation 측 architectural inspiration cite
- ✗ **금지**: APT Contract ↔ compiler type 의 1:1 identity 주장 (D2 위배 — Contract 는 behavioral, type 은 syntactic)
- ✗ **금지**: APT phase 전이 ↔ IR lowering pass 의 functional equivalence 주장 (D1+D4+D5 위배 — direction/loop/centric 모두 다름)
- ✗ **금지**: SCW ↔ Codegen 1:1 매핑 (D3 SA 부재 + D4 TDD loop 위배)

**비교 anchor**: Stefan free-boundary (kinetics canonical 0.92+) vs Avrami (metaphor partial 0.87/0.45) 의 caveat 패턴과 동일 — Compiler IR 은 *partial structural metaphor* (0.72) 측 분류, deep canonical grounding 아님.

### 5. 학문 인용

| Citation | Role |
|----------|------|
| Aho AV, Lam MS, Sethi R, Ullman JD (2006) *Compilers: Principles, Techniques, and Tools* (Dragon Book, 2nd ed.) Addison-Wesley | Frontend→IR→Codegen canonical pipeline reference |
| Lattner C, Adve V (2004) "LLVM: A compilation framework for lifelong program analysis & transformation" CGO | SSA IR, pass infrastructure (modern reference) |
| Lattner C et al. (2021) "MLIR: Scaling Compiler Infrastructure for Domain Specific Computation" CGO | Multi-level IR (HIR/MIR/LIR analogue) |
| Meyer B (1992) "Applying Design by Contract" IEEE Computer 25(10):40-51 | DbC 4-측면 (pre/post/invariant/type) — APT Contract 측 정확 grounding, compiler type 과 구별점 (D2) |
| Allen FE (1970) "Control flow analysis" SIGPLAN Notices 5(7):1-19 | Product-centric IR analysis 시조 (D5 product vs agent 구분 source) |
| PROM_16 P3.1 finding (2026-05-14) — `rf-prom16-apt-essence-P3-S1-compiler-ir-passes-2026-05-14` | PARTIAL_STRUCTURAL_ISOMORPHISM 0.72 verdict, 5 D1-D5 차원 enumeration |

# KG: compiler-ir-partial-isomorphism-reframe-2026-05-14, rf-prom16-apt-essence-P3-S1-compiler-ir-passes-2026-05-14, APT_essence_canonical_2026-05-14

---

## 🧪 Cross-Disciplinary Groundings (Caveats) — Analogy/Intuition Pumps, NOT physical/biological claims

> APT 본질 metaphor pool 에는 *물리학/생물학* 측 매력적인 매핑이 여럿 있으나, PROM 16 P4.2 + P4.3 finding (2026-05-14) 측 검증 결과 **analogy/intuition pump 분류** — physical/biological reality claim 으로 cite 금지. Stefan canonical grounding (P4.1) 과는 위치가 다름.

### A. QM Decoherence (P4.2) — ANALOGY_PHYSICAL_CAVEAT, confidence 0.78

**Mapping**: SP 측 Span superposition (여러 decomposition 후보 공존) → ST 측 Crystallization Frontier 통과 → SCW 측 single code realization. "관측 (Naesengmoon verdict) 이 superposition 을 collapse 시킨다" 는 직관.

**Status**: **Analogy/intuition pump only** (0.78 phenomenological similarity, 0 physical claim).

**Why caveat**:

1. **No actual quantum amplitudes** — APT Span 후보는 *epistemic* uncertainty (지식 부족), QM superposition 은 *ontic* (Hilbert space 측 실재) — Heisenberg/Born interpretation 측 구별 (epistemic vs ontic state, Spekkens 2007 toy theory 측 명확화).
2. **No unitarity** — APT phase 전이는 비가역 (git monotone), QM 은 unitary (reversible until measurement) — D2 thermodynamic arrow vs reversible dynamics.
3. **No interference** — APT 는 후보 간 interference pattern 없음, QM 은 amplitude superposition + Born rule.
4. **Measurement problem 부재** — APT 는 명시적 verdict (Naesengmoon gate), QM 은 measurement problem (Bell 1990, Maudlin 1995) 미해결.
5. **Probabilistic vs deterministic** — QM 측 Born rule 은 stochastic, APT 측 verdict 는 deterministic (rubric + evidence based).

**대체 grounding 권장**:

- **Lawvere fixed point theorem** (Lawvere 1969) — diagonalization 측 *수학적* superposition→collapse 형식화. APT 측 self-referential closure (orchestrator self-application forbidden, max_depth=1, delta=0) 의 정확 grounding. KG: 이미 `selfreference-positive-fixed-point-meta-infinity-2026-03-26` 적재.
- **Type theory** (Martin-Löf 1984, Univalent Foundations) — dependent type 측 evidence-bearing proposition 으로 "관측" 직관 형식화. Curry-Howard correspondence 측 verdict ↔ proof term 매핑.

**사용 가이드라인**:

- ✓ **허용**: pedagogical intuition pump ("SP 측 후보 공존이 QM superposition 같다") — 청자가 QM 친숙할 때 빠른 이해
- ✗ **금지**: "APT 는 QM 적 process 다" 류 physical claim
- ✗ **금지**: Bell inequality / EPR 등 QM 측 고유 phenomenon 의 APT 측 mirror claim
- ✗ **금지**: decoherence rate / decoherence time 같은 quantitative QM 측 변수의 APT 매핑

### B. Embryology Gastrulation (P4.3) — STRONG_HOMOMORPHISM_WITH_DISANALOGIES, confidence 0.65-0.70

**Mapping**: SA (blastula 측 미분화 전체) → SP (gastrulation 측 germ layer 분화) → ST (organogenesis 측 contract 결정) → SCW (tissue 측 코드 물질화). Progressive differentiation 측 위상 동형 (homomorphism).

**Status**: **Strong abstract homomorphism + 5 critical disanalogies** (0.65-0.70 abstract topology only).

**5 Critical Disanalogies**:

1. **Causality direction** — Embryology 는 *genetic program* (DNA → morphogen gradient → cell fate, bottom-up self-organization, Turing 1952 reaction-diffusion). APT 는 *intentional design* (SA telos → SP decomposition, top-down deliberate). 인과 방향 정반대.
2. **Materiality** — Embryology 는 *물리적 cell substrate* (자율 분열, 자원 소비, metabolism). APT 는 *informational symbol substrate* (Contract/Span/Code text). Cell ≠ symbol.
3. **Reversibility** — Embryology 측 cell fate 는 *대부분 비가역* (gastrulation 이후 germ layer 고정, Waddington epigenetic landscape 1957). APT 측 phase backflow 는 *허용* (meta-review feedback loop, Naesengmoon verdict → SP 재구성). Embryology 보다 *덜* 비가역.
4. **Finiteness** — Embryology 측 cell count 는 *물리적 한계* (인간 ~10^13 cells, 유한 정확). APT 측 Span DAG 는 *논리적 무한* (재귀 분해 깊이 제한 없음, MethodologyConfig.max_recursion_depth 만 외부 cap). Cardinality 측 카테고리 다름.
5. **Scale** — Embryology 는 *주어진* timescale (인간 임신 9 개월, 종 특이 고정). APT 는 *human pacing* (vibe_coding_sweet 200-500 line, cycle time 가변). 시간 scale 외부 vs 내부.

**Status 의미**: 5 disanalogy 에도 불구 *abstract topology* (progressive differentiation, layer-by-layer commitment, irreversibility 측 일부 공유) 측 0.65-0.70 homomorphism 유지. 따라서 *abstract topology* 측 cite 만 허용.

**사용 가이드라인**:

- ✓ **허용**: "progressive differentiation" 직관 측 abstract topology cite (germ layer 분화 ↔ Span 분해 측 topology 측 mirror)
- ✓ **허용**: Waddington epigenetic landscape 측 *수학적* 형상 (basin of attraction, Thom 1972 catastrophe theory) 비유 — 단 topology only
- ✗ **금지**: 인과 방향 동일 주장 (D1 위배 — genetic vs intentional 정반대)
- ✗ **금지**: cell ↔ Span 1:1 identity (D2 materiality 위배)
- ✗ **금지**: Hox gene / morphogen gradient 측 quantitative parameter 의 APT 매핑
- ✗ **금지**: embryology 측 timescale 측 APT 매핑 (D5 scale 위배)

### C. 카테고리 분류 표 — Canonical vs Metaphor vs Caveat

| Source | Confidence | Category | Cite role | KG |
|--------|------------|----------|-----------|-----|
| **Aristotelian Hylomorphism** (Meta VII-IX) | 0.92+ | **CANONICAL_METAPHYSICAL** | Vertical reduction grounding (form/matter) | `aristotle-hylomorphism-grounding-2026-05-14` |
| **Stefan free-boundary** (Stefan 1891, Caffarelli 1977) | 0.92+ | **CANONICAL_KINETICS** | Crystallization Frontier kinetics grounding | `stefan-free-boundary-grounding-2026-05-14` |
| **Avrami KJMA** (1939-41) | 0.87 / 0.45 | METAPHOR_PARTIAL | nucleation→growth phenomenology only | `avrami-kjma-metaphor-partial-2026-05-14` |
| **Compiler IR passes** (LLVM, MLIR, Dragon) | 0.72 | **PARTIAL_STRUCTURAL_ISOMORPHISM** | Phase chain phenomenology only (5 difference) | `compiler-ir-partial-isomorphism-reframe-2026-05-14` |
| **QM decoherence** (Heisenberg, Born) | 0.78 | **ANALOGY_PHYSICAL_CAVEAT** | Intuition pump only (no physical claim) | `qm-decoherence-analogy-caveat-2026-05-14` |
| **Embryology gastrulation** (Waddington, Turing) | 0.65-0.70 | **STRONG_HOMOMORPHISM_WITH_DISANALOGIES** | Abstract topology only (5 disanalogy) | `embryology-gastrulation-homomorphism-caveat-2026-05-14` |
| **Annealing/Refactoring** | 0.45 | ✗ **DEPRECATED** | Cite 금지 (monotone ratchet, not thermodynamic) | `annealing-refactoring-metaphor-DEPRECATED-2026-05-14` |

### D. 학문 인용

| Citation | Role |
|----------|------|
| Spekkens RW (2007) "Evidence for the epistemic view of quantum states: A toy theory" Phys Rev A 75:032110 | Epistemic vs ontic QM state distinction (QM caveat D1 source) |
| Bell JS (1990) "Against 'measurement'" Phys World 3(8):33-40 | Measurement problem 미해결 (QM caveat D4) |
| Lawvere FW (1969) "Diagonal arguments and cartesian closed categories" Lecture Notes Math 92:134-145 | QM 대체 grounding (Lawvere fixed point — self-reference 측 수학 형식화) |
| Martin-Löf P (1984) *Intuitionistic Type Theory* Bibliopolis | Type theory 측 evidence-bearing proposition (QM "관측" 대체 grounding) |
| Turing AM (1952) "The chemical basis of morphogenesis" Phil Trans R Soc B 237:37-72 | Reaction-diffusion morphogenesis (embryology D1 causality bottom-up source) |
| Waddington CH (1957) *The Strategy of the Genes* Allen & Unwin | Epigenetic landscape (embryology D3 irreversibility source) |
| Thom R (1972) *Stabilité structurelle et morphogénèse* Benjamin | Catastrophe theory (embryology abstract topology 허용 grounding) |
| PROM_16 P4.2 finding (2026-05-14) — `rf-prom16-apt-essence-P4-S2-qm-decoherence-2026-05-14` | QM decoherence 0.78 ANALOGY_PHYSICAL_CAVEAT verdict |
| PROM_16 P4.3 finding (2026-05-14) — `rf-prom16-apt-essence-P4-S3-embryology-gastrulation-2026-05-14` | Embryology gastrulation 0.65-0.70 STRONG_HOMOMORPHISM_WITH_DISANALOGIES verdict |

# KG: qm-decoherence-analogy-caveat-2026-05-14, embryology-gastrulation-homomorphism-caveat-2026-05-14
# KG: rf-prom16-apt-essence-P4-S2-qm-decoherence-2026-05-14, rf-prom16-apt-essence-P4-S3-embryology-gastrulation-2026-05-14
# KG: APT_essence_canonical_2026-05-14

---

# APT v21 Orchestrator -- Anti-Rubber-Stamp Adversarial Validation

Master coordinator for APT development with MANDATORY adversarial validation at every gate.
No gate may be passed without: (1) adversarial critic review, (2) ground truth verification,
(3) human sigma_oracle approval, (4) evidence-backed verdicts (HR11), (5) post-gate reflection.
These are HARD requirements -- not guidelines.

```
SA --> SP --[adversarial]--> ST --[adversarial]--> SCW --[adversarial + test]--> PH6
            |                     |                       |
       Critic attacks        Critic attacks          Critic + cargo test
            |                     |                       |
       KG log + fix          KG log + fix            KG log + fix
            |                     |                       |
       sigma_oracle (HUMAN)  sigma_oracle (HUMAN)    sigma_oracle (HUMAN)
```

---

## 0. HARD RULES (v21 -- cannot be overridden)

These rules are BLOCKING. If any is violated, the orchestrator MUST halt and refuse to proceed.

| # | Rule | Enforcement |
|---|------|-------------|
| HR1 | **Adversarial round at EVERY gate** | No gate passes without AdversarialRound() completing |
| HR2 | **sigma_oracle is ALWAYS human** | `allow_agent_sigma: false` -- agent cannot self-approve |
| HR3 | **Critic model differs from design model** | Same-model critique is BLOCKED (exception: Lite Mode with full D22.3 template) |
| HR4 | **Minimum `cfg.adversarial_min_findings_per_round` findings per round** | If critic returns less: re-run with stronger prompt (Section 7.2) |
| HR5 | **KG density check before decomposition** | INFORMED_BY < `cfg.density_min_informed_by` or source_types < `cfg.density_min_source_types`: BLOCK and run KAL |
| HR6 | **Ground truth before gate pass** | SCW: cargo test MUST pass. SP/ST: WebSearch evidence cited. |
| HR7 | **Every gate transition logged to KG** | AptDecisionLog node created. No silent transitions. |
| HR8 | **Every adversarial finding logged to KG** | AptFeedback node created per finding. |
| HR9 | **No human response to sigma_oracle = BLOCK** | Do not proceed. Ask again. Never assume approval. |
| HR10 | **Every skip/override requires explicit human reason** | Logged with justification. Agent cannot generate reason. |
| HR11 | **Every APPROVED verdict must cite specific evidence** | Theorem name, test result, or KG query. No evidence = RUBBER_STAMP violation, auto-downgrade to NEEDS_REVIEW. |
| HR12 | **2-Tier Naesengmoon: never mix tiers** | Tier 1 (`LensSet.constitutional`) for artifacts, Tier 2 (`LensSet.mathematical`) for methodology meta-verification only. Cross-tier application BLOCKED (`cfg.taliban_mixing_tiers='BLOCKED'`). lens_count는 LensSet 노드 조회. |
| HR13 | **Essential ✗ are design constraints, not bugs** | Arrow of Time (order-dependent), Edge of Chaos (structured complexity), Gödel (never complete). Do not "fix" these. |
| HR14 | **Mandatory post-gate reflection** | After every gate: identify weakness exposed, log as AptFeedback, confirm next gate checks for it. No reflection = INCOMPLETE_GATE. |
| HR15 | **Lean ground truth (optional per project)** | If enabled: `lake build` must produce sorry=0, error=0, warning=0. Add `lean: "lake build"` to config to activate. |
| HR16 | **SA-가려진 경로에 SCW 없이 편집 금지** | SemanticAnchor 또는 SPAN_*_ROOT가 이미 존재하는 파일/디렉터리(예: landing-site, 333-platform, metahumotonic-web)에 Write/Edit 호출 시 BLOCK — AtomicSpan+Contract+Task 체인 없이 직접 편집 = executor=reviewer 위반(D20). Pre-edit 확인: `MATCH (sa:SemanticAnchor)-[:COVERS_PATH*0..]->(p) WHERE $target_path STARTS WITH p.path RETURN sa` → 매치 존재 시 `/apt-sp` 진입 강제. # KG: lesson-apt-scw-skipped-ritual-css-2026-04-17, lesson-apt-vr-self-fulfilled-executor-reviewer-2026-04-16 |

---

## 1. Configuration (v26 A6 — KG slot resolve, NOT prose)

> **Magic number 박지 마세요.** 모든 설정값은 `MethodologyConfig_default_v26` 노드에서 resolve. SKILL.md 본문에 숫자 박는 순간 KG와 drift 발생 → Naesengmoon reject.

```cypher
// Single source of truth — read at gate entry, not at SKILL.md parse time
MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})
      -[:HAS_SLOT]->(s:MethodologySlot {name:'MethodologyConfig'})
MATCH (cfg:MethodologyConfig {name: s.currentConcrete})
RETURN cfg
```

**Field map** (legacy yaml → cfg field name on `MethodologyConfig_default_v26`, 67 fields total):

| 영역 | cfg 필드 |
|------|---------|
| Adversarial | `adversarial_min_findings_per_round`, `adversarial_max_rounds_per_gate`, `adversarial_critic_model`, `adversarial_design_model`, `adversarial_blocker_auto_return`, `adversarial_re_attack_on_insufficient`, `gates_requiring_adversarial` |
| Approval | `allow_agent_sigma`, `sigma_sla_hours` |
| Ground truth | `ground_truth_required`, `ground_truth_sp_st_evidence`, `ground_truth_cmd_{test,build,lint,wasm,lean}` |
| Density (D4/D21) | `density_min_informed_by`, `density_min_source_types`, `density_foundation_composite_ratio` |
| Logging | `kg_decision_log`, `kg_feedback_log`, `kg_skip_log` |
| Parallel | `parallel_enabled`, `parallel_max_agents`, `parallel_strategy`, `parallel_integration_gate_required` |
| Reflection (HR14) | `reflection_mandatory`, `reflection_template` |
| Verdict (HR11) | `verdict_require_evidence`, `verdict_rubber_stamp_action` |
| Naesengmoon tiers (HR12) | LensSet 노드의 `lens_count` 조회 + `taliban_mixing_tiers` |
| Vibe coding (D5) | `vibe_coding_{min_lines,sweet_min,sweet_max,hard_max}`, `decomposition_diseconomy_min_lines` |
| Lens min critics | `lens_min_critics_{constitutional,constitutional_sp_focused,longinus,mathematical,solid}` |
| Context budget | `context_budget_{total,overhead,l1_avg,l2_avg,sa_default}` |
| Span | `span_depth_max`, `max_subagents_per_cycle` |
| Stale lock (V17) | `stale_lock_max_hours` |
| Essential failures (HR13) | `essential_arrow_of_time`, `essential_edge_of_chaos`, `essential_godel` |
| Mode | `auto_mode` |

**LensSet count** (tier1/tier2)는 `MATCH (l:LensSet {name:$set}) RETURN l.lens_count` 로 조회. SKILL.md 본문의 `9`/`88`/`113` 등 숫자는 *snapshot at write time*이며 권위 아님.

> 본 섹션 아래 v21 절차 본문에 등장하는 정수(예: "minimum 3 findings", "<=500 lines")는 모두 위 cfg 필드의 표시값일 뿐. **수정 시 cfg 노드만 갱신** — prose 직접 편집 금지 (HR-A6).

# KG: APT_v26_A6_2026-04-21, MethodologyConfig_default_v26 (67 fields, v26_a6_extension 2026-04-25)

---

## 2. Phase Detection Algorithm

Before any action, determine the current phase by querying the KG.

### 2.1 Per-Branch Phase Detection

```cypher
// Phase Detection -- per branch, not global
MATCH (span:AptSpan {name: $target_span})
OPTIONAL MATCH (span)-[:CRYSTALLIZES_TO]->(st:SemanticTwin)
OPTIONAL MATCH (st)-[:HAS_CONTRACT]->(c:AptContract)
OPTIONAL MATCH (c)-[:MATERIALIZES]->(src:SourceCodeNode)
RETURN span.name,
  CASE
    WHEN src IS NOT NULL THEN 'PH5/PH6: SCW (code exists, use /apt-scw for feedback)'
    WHEN c IS NOT NULL THEN 'PH5: SCW (contract ready, use /apt-scw to implement)'
    WHEN st IS NOT NULL THEN 'PH4: ST (twin exists but no contract, use /apt-st)'
    WHEN span:AtomicSpan THEN 'PH4: ST (atomic, ready to crystallize, use /apt-st)'
    ELSE 'PH3: SP (needs decomposition, use /apt-sp)'
  END AS current_phase
```

### 2.2 SA Existence Check

```cypher
MATCH (sa:SemanticAnchor {name: $project})
RETURN sa.name, sa.domain, sa.status
```

If no SA exists, start with `/apt-sa`.

### 2.3 Check Adversarial History for Span

```cypher
// v17: Check if adversarial rounds were completed for this span
MATCH (span:AptSpan {name: $target_span})
OPTIONAL MATCH (span)<-[:TARGETS]-(dl:AptDecisionLog)
WHERE dl.gate_type IN ['C_S_sigma', 'RefinementGate', 'FulfillmentGate']
RETURN span.name,
  collect(dl.gate_type) AS completed_gates,
  collect(dl.decision) AS decisions,
  collect(dl.adversarial_verdict) AS verdicts
```

---

## 3. Flow Control with Adversarial Gates

Phases are NOT sequential steps for the whole project. Each **branch** progresses independently.
At any moment, branch A may be in PH3, branch B in PH4, branch C in PH5.

### 3.1 Master Flow

```
User Request
    |
    v
[/apt] Phase Detection (per branch)
    |
    +-- No SA exists -----------------> /apt-sa (PH1+PH2: bootstrap)
    |                                        |
    |                           SA created   v
    |                                   /apt-sp (PH3: decompose)
    |
    +-- Branch not decomposed ---------> /apt-sp (PH3)
    |       |
    |       +-- [GATE: KG Density Check (D21)] -- BLOCK if fails
    |       +-- [GATE: C(S) predicate check] (5-predicate self-containment)
    |       +-- [GATE: A3 SiblingIndependence] (sibling wellformedness, RFC1 v26.1)
    |       +-- [GATE: Adversarial Round (C_S_sigma)]
    |       +-- [GATE: sigma_oracle (HUMAN)] -- BLOCK until human responds
    |       |
    |       v
    +-- [TRANSITION SP→ST: mini-RGR] (RFC2 v26.1 local cleanup)
    |       +-- RED: prior contract와 conflict 검사
    |       +-- GREEN: contract 결정화 GO/NO-GO
    |       +-- REFACTOR: 중복 contract 통합/제거
    |       v
    +-- Branch has AtomicSpan ---------> /apt-st (PH4)
    |       |
    |       +-- [GATE: Adversarial Round (RefinementGate)]
    |       +-- [GATE: sigma_oracle (HUMAN)] -- BLOCK until human responds
    |       |
    |       v
    +-- [TRANSITION ST→SCW: mini-RGR] (RFC2 v26.1 local cleanup)
    |       +-- RED: 작성할 file이 prior code와 conflict 검사
    |       +-- GREEN: file 작성 GO/NO-GO
    |       +-- REFACTOR: file move/delete/merge — atomic-span dump 평면 누적 차단
    |       v
    +-- Branch has Contract -----------> /apt-scw (PH5)
    |       |
    |       +-- [GATE: cargo test / ground truth]
    |       +-- [GATE: Adversarial Round (FulfillmentGate)]
    |       +-- [GATE: sigma_oracle (HUMAN)] -- BLOCK until human responds
    |       |
    |       v
    +-- Branch has code ---------------> /apt-scw (PH6 feedback)
    |       |
    |       +-- Discovery? ------------> back to /apt-sp or /apt-st
    |       |
    |       v
    +-- SCW fulfilled -----------------> /apt-cleanup (PHASE 6 Cleanup Gate)  ← NEW (PROM 16 F8)
    |       |
    |       +-- [GATE: 4-tool ratchet] tach=0, fat_ratchet, vulture_delta, complexipy_ratchet
    |       +-- [GATE: refactor:feature commit ratio ≥ 0.2]
    |       +-- [GATE: pass_count ≥ 5/7] PASS | NEEDS_REFACTOR | BLOCK
    |       |
    |       v
    +-- Cleanup PASS ------------------> /apt-meta-review (Phase 5 — methodology meta-improve)
```

> **Phase 6 (Cleanup Gate) NEW (2026-04-29)** — TDD REFACTOR phase 의 cycle-level 거울. SOLID class-level 만으로는 못 잡는 *folder-level* CCP/ADP 위반을 4-tool ratchet (tach/complexipy/lizard/vulture/deptry) + commit ratio 로 enforce. atomic-span shipping 평면 누적 정정 메커니즘. Spec: [`/apt-cleanup`](../apt-cleanup/SKILL.md). KG: `lesson-apt-phase6-cleanup-missing-2026-04-28`, `lesson-solid-class-level-vs-package-level-mismatch-2026-04-29`.

> **v26.1 RFC2 — two-tier cleanup**: Phase 6은 **global cross-phase view** (4 phase 누적 관측). Local cleanup은 *transition mini-RGR* 3곳 (SA→SP / SP→ST / ST→SCW)에 분리 배치. 두 tier 책임 분리 — Phase 6 폐기 아님, **추가**. KG: `rfc-apt-two-tier-cleanup-2026-04-29`.

## Your role
You are the CRITIC, not the designer. Your job is to FIND FLAWS, not to approve.
A review with zero findings is a FAILED review -- it means you didn't look hard enough.

## Rules
1. You MUST produce at least 3 findings. No exceptions.
2. Each finding must be SPECIFIC and FALSIFIABLE -- not vague concerns.
3. At least 1 finding must challenge a CORE ASSUMPTION, not just surface issues.
4. You must check for these failure modes:
   - Missing edge cases (null, empty, overflow, concurrent access)
   - Incorrect assumptions about dependencies or APIs
   - Violations of APT axioms (A1-A4) or design principles (D1-D24)
   - Untestable or ambiguous postconditions
   - Performance cliffs under realistic load
5. If you genuinely find no issues after thorough review, you must document
   your review methodology (what you checked) as evidence of diligence,
   and still produce 3 findings at NITPICK level minimum.

## Anti-rubber-stamp checklist (you MUST address each):
- [ ] Did I check the PRECONDITIONS, not just the happy path?
- [ ] Did I verify the OUTPUT TYPE is concrete and sufficient?
- [ ] Did I look for what is MISSING, not just what is present?
- [ ] Did I consider CONCURRENT/PARALLEL execution scenarios?
- [ ] Did I check consistency with SIBLING spans/contracts?
- [ ] Did I verify INFORMED_BY sources are actually relevant?
- [ ] Did I check for violations of SINGLE FILE PROJECTION (D5)?
- [ ] Did I consider what happens when this FAILS at runtime?
- [ ] Did I verify the test sketch actually TESTS the postcondition?
- [ ] Did I check if this duplicates or conflicts with EXISTING code?

## Artifact under review
{artifact_content}

## Context
{relevant_kg_context}

## Output format
Produce findings as structured YAML, then a verdict.

### Findings

finding:
  id: "F-{gate}-{n}"
  severity: "BLOCKER" | "PERFORMANCE" | "DESIGN_DEBT" | "NITPICK"
  category: "correctness" | "completeness" | "consistency" | "efficiency" | "maintainability"
  claim: "What is wrong (specific, falsifiable)"
  evidence: "Why this is wrong (reference to code/spec/external source)"
  suggestion: "How to fix (concrete, actionable)"
  ground_truth_testable: true | false

### Verdict: REJECT | CONDITIONAL_PASS | PASS
  REJECT:           >= 1 BLOCKER finding
  CONDITIONAL_PASS: 0 BLOCKER, >= 1 PERFORMANCE finding
  PASS:             0 BLOCKER, 0 PERFORMANCE (only DESIGN_DEBT + NITPICK)
```

---

## 27. Reference Files

| File | Content | When to Read |
|------|---------|-------------|
| `references/apt_core.md` | SS1-SS9: Sets, Functions, Predicates, Relations, Axioms, Dual Guidance, Design Principles, KAL Config | Understanding foundations |
| `references/apt_infra.md` | SS23-SS30: Kafka Events, KG-Git Sync, MERGE-Only, Indexes, HA, Observability, Incident Response, CI/CD | Infrastructure setup |
| `references/apt_reference.md` | SS31-SS40: V1-V17 Queries, Traceability, Gap Resolution, Theory, Errors, Anti-Patterns, Feedback, Tutorials | Validation details |

---

### Lazy-load reference files (PROM 16 F6.1 — Progressive Disclosure)

본 SKILL.md 는 *core flow* 만 보유. Deep detail 은 아래 lazy-load 파일 — 해당 phase/gate 진입 시에만 Read.

| File | Sections (originally in SKILL.md) | Read when |
|---|---|---|
| [`references/phases.md`](references/phases.md) | § 4 Adversarial Round / § 5 KG Density / § 6 Ground Truth / § 11 Phase Transition Guards | Phase 진입 시 |
| [`references/gates.md`](references/gates.md) | § 3.2 Gate Sequence / § 12 Gate Evidence / § 23 Approval Gates | Gate 통과 판정 시 |
| [`references/adversarial.md`](references/adversarial.md) | § 7 Anti-Bypass / § 15 Mode Collapse Detection | Adversarial check 시 |
| [`references/kg_logging.md`](references/kg_logging.md) | § 8 KG Logging / § 14 Feedback System | KG write / feedback 발생 시 |
| [`references/error_handling.md`](references/error_handling.md) | § 9 Error Handling / § 13 Parallel Execution | Error / parallel dispatch 시 |
| [`references/validation.md`](references/validation.md) | § 10 V1-V29 / § 24 Events / § 25 Clarifications / § 26 Invariants | Validation 실행 시 |
| [`references/theory.md`](references/theory.md) | § 17 Diffusion / § 18 GAN-Context / § 19 Mold Flow / § 28 Theoretical Foundations / § 29 Version History | Theoretical reasoning 시 |
| [`references/quick_ref.md`](references/quick_ref.md) | § 16 Auto Mode / § 20 Decision Tree / § 21 When to Use / § 22 Core Concepts | Quick lookup 시 |
| [`references/_legacy/`](references/_legacy/) | apt_core.md / apt_infra.md / apt_reference.md (stale, NOT synced) | (참고만) |


## 30. ENFORCEMENT CHECKLIST (for orchestrator self-check)

Before allowing ANY gate passage, the orchestrator MUST verify:

```
[ ] 1. Adversarial critic invoked (not skipped)
[ ] 2. Critic model differs from design model (or Lite Mode with full template)
[ ] 3. Critic produced >= 3 findings (or escalated prompt ran)
[ ] 4. Ground truth commands executed (cargo test for SCW, WebSearch for SP/ST)
[ ] 5. All ground-truth-testable findings verified
[ ] 6. sigma_oracle is HUMAN (allow_agent_sigma: false)
[ ] 7. HUMAN has responded (not assumed, not skipped)
[ ] 8. AptDecisionLog created in KG
[ ] 9. All AptFeedback nodes created for findings
[ ] 10. No BLOCKER findings unresolved (or overridden with human reason)
```

If ANY checkbox fails: BLOCK. Do not proceed. Fix the issue first.

---

*End of APT v17 Orchestrator SKILL.md*
*This is the authoritative skill file. v16 and earlier are superseded.*

---

## MIC Binding Disclaimer

> 이 SKILL.md에서 "Prometheus", "Naesengmoon", "88-Naesengmoon", "Longinus", "재배맨" 등의
> concrete 이름은 MIC_v1 MethodologySlot의 **현재 바인딩(currentConcrete)**이다.
> Slot이 다른 concrete로 교체되면 이 파일의 이름도 drift한다.
> 정본 해석: `MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})-[:HAS_SLOT]->(s) RETURN s.name, s.currentConcrete`
> 유틸리티: `03_SCRIPTS/db/resolve_mic_slot.cypher`
> # KG: lesson-skill-mic-slot-ref-weak-2026-04-15

---

## History

> Per-skill history archived 2026-05-20 (Longinus L4 byte-budget split). 89 lines → `references/history_archive_2026-05-20.md`.
> Triggered by `VR_APT_ensemble_5lens_v2_filelineCited_2026-05-20` 248KB overflow challenge.
> Live view: see archive file + `git log -- apt/SKILL.md`.

## 🎛 v27 Addendum — HR13 Adversarial Gate Cypher Enforcement (2026-05-19)

> A6 resolve-only 준수. Prose 측 magic number 미박입 — KG `:ValidationGate` 측 enforcement_cypher field 측 단일 정전. PreToolUse hook 측 shadow rollout (warn-only) 측 BLOCK 격상은 1-sprint audit 후.

```cypher
// HR13 LensSet completeness + adversarial verdict gate (per AptDecisionLog)
MATCH (vg:ValidationGate {name:'gate-hr13-adversarial-cypher-2026-05-19'})
RETURN vg.enforcement_cypher, vg.violation_action

// AptDecisionLog v2 schema (required fields)
MATCH (sch:Schema {name:'schema-aptdecisionlog-v2-adversarial-gate-2026-05-19'})
RETURN sch.required_fields, sch.gate_type_enum, sch.adversarial_verdict_enum
```

PreToolUse hook: `~/.claude/hooks/pre_tool_apt_phase_gate_check.py` (matcher `mcp__neo4j__write_neo4j_cypher`, MODE=SHADOW_OBSERVE → BLOCK after audit).

# KG: gate-hr13-adversarial-cypher-2026-05-19 / schema-aptdecisionlog-v2-adversarial-gate-2026-05-19 / sprint-apt-hr1-enforcement-gate-cypher-2026-05-19 / lesson-sprint-apt-hr1-misnomer-actually-hr13-lensset-2026-05-19

### v27-B. RFC2 Contract Substitution Mode Gate (2026-05-19)

> SP→ST mini-RGR 측 contract substitution criteria 측 `rigor_level` 5-tier enum 측 mapping. Binary `fast_path/full_cycle` 측 deprecated (학술 정전 5-tier 측 honor).

```cypher
MATCH (sch:Schema {name:'schema-contract-substitution-mode-rfc2-2026-05-19'})
RETURN sch.tier_mapping, sch.contract_artifact_kinds, sch.substitution_criteria

MATCH (vg:ValidationGate {name:'gate-contract-substitution-rfc2-2026-05-19'})
RETURN vg.enforcement_cypher
```

Tier mapping: `conjecture/heuristic → informal_allowed (docstring|test_signature)` · `semi-rigorous → mixed` · `rigorous → typed_pydantic_dto mandatory` · `proven → typed_pydantic_dto + lake build sorry=0`.

# KG: gate-contract-substitution-rfc2-2026-05-19 / schema-contract-substitution-mode-rfc2-2026-05-19 / sprint-apt-st-informal-contract-rgr-cfg-gate-2026-05-19 / lesson-sprint-rfc2-binary-fast-vs-full-actually-rigor-level-5tier-2026-05-19

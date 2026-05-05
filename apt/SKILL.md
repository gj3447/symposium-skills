---
name: apt
kg_ref: ATOM_Skill_apt_orchestrator
version: "27.1.0"
channel: stable
description: >
  APT v26.1 orchestrator — KG 정본 기반. Gate Check Hook 강제. SA→SP→ST→SCW 순환.
  v5~v21 역사 반영. 하네스 4축 + 5대 무기(하네스/탈레반/프로메테우스/롱기누스/재배맨) + D(S)/C(S) + Crystallization Frontier.
  v26.1: RFC1 (C(S) ↔ A3 axiom layer 분리 명시 + Greek :ARCHIVED) + RFC2 (two-tier cleanup: local RGR in transitions + global Phase 6) + Apt_FourPlusOne motif 인식.
  # KG: ATOM_Skill_apt_orchestrator, APT_v26_RFC_draft_2026-04-21 (A1-A6 pluggable MIC slots 7→10)
  # KG: APT_v25_RFC_draft_2026-04-17 (error_variants extension, SharedType→shared=true, meta-validation)
  # KG: rfc-apt-cs-axiom-visibility-drift-2026-04-29, rfc-apt-two-tier-cleanup-2026-04-29, Apt_FourPlusOne
  v26 A1: MIC slots 10 (ContractSchema/LensSet/MethodologyConfig 추가). v26 A3/A5: Gate Check Hook LensSet completeness + Cypher enforcement (3-lens shortcut 차단). v26 A6: SKILL.md resolve-only — 본문 리라이트는 별도 스프린트 (ATOM_APT_v26_Gate_Hook_Lens_Enforcement_2026-04-21).
  v22: Gate Check enforcement via Claude Code Hook.
  Incorporates Taliban --lens mathematical 5-round meta-verification feedback (260✓→102✓ honest convergence).
  Every gate requires: adversarial critic + ground truth + human sigma_oracle + evidence-backed verdicts + post-gate reflection.
  HR11: Every APPROVED verdict MUST cite specific evidence. Approvals without evidence = RUBBER_STAMP violation.
  Taliban 렌즈셋 플러거블: --lens constitutional(기본, 산출물 검증) / --lens mathematical(메타 검증). LensSet KG 노드로 확장.
  피드백은 5대 무기 순환의 창발 속성 (독립 위상 아님). # KG: lesson-feedback-is-emergent-not-weapon-2026-04-16
  Essential ✗: Arrow of Time (order-dependent), Edge of Chaos (structured complexity), Gödel (never complete).
  Optional Lean 4 integration: `lake build` sorry=0 error=0 as ground truth.
  Invoke when: "start work on", "implement", "develop", "what phase am I in",
  "apt check", "validate apt", "auto mode", or any general development request.
  Enforces: phase detection, flow control, adversarial gates, validation V1-V29, feedback system, mandatory reflection.
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

---

## 🔗 MIC Binding (SOLID-DIP) — 재배맨 진짜 구조

> 본 skill의 5대 무기 참조는 **concrete 이름 대신 MethodologySlot 조회**로 호출.
> Treasure 교체 시 `MIC_v1` 노드만 수정 → 본문 무수정.

**IS slot**: Orchestrator (5대 무기 조율)
**USES slots**: Harness, ResearchProvider, AdversarialValidator, KgCodeBinder, SubagentSeeder
**참고**: MetaVerifier는 AdversarialValidator(Taliban)의 --lens mathematical로 통합. FeedbackProvider는 창발 속성(슬롯 아님).

**동적 resolution**:
```cypher
MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})-[:HAS_SLOT]->(s:MethodologySlot)
RETURN s.name, s.currentConcrete, s.invocation
```

본문의 `Prometheus`/`Taliban`/`Longinus`/`재배맨` 등은 MIC slot의 **현재 스냅샷**. 진짜 호출은 `s.invocation`.
88-Taliban은 별도 concrete가 아니라 `Taliban --lens mathematical`. MetaVerifier 슬롯은 Taliban의 렌즈셋으로 통합됨.
피드백은 5대 무기 순환의 창발 속성 — FeedbackProvider 슬롯은 EMERGENT 상태.
# KG: lesson-feedback-is-emergent-not-weapon-2026-04-16, lesson-taliban-lens-pluggable-refactor-2026-04-16

# KG: MIC_v1, lesson-apt-not-truly-jaebaeman-2026-04-14

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
| HR12 | **2-Tier Taliban: never mix tiers** | Tier 1 (`LensSet.constitutional`) for artifacts, Tier 2 (`LensSet.mathematical`) for methodology meta-verification only. Cross-tier application BLOCKED (`cfg.taliban_mixing_tiers='BLOCKED'`). lens_count는 LensSet 노드 조회. |
| HR13 | **Essential ✗ are design constraints, not bugs** | Arrow of Time (order-dependent), Edge of Chaos (structured complexity), Gödel (never complete). Do not "fix" these. |
| HR14 | **Mandatory post-gate reflection** | After every gate: identify weakness exposed, log as AptFeedback, confirm next gate checks for it. No reflection = INCOMPLETE_GATE. |
| HR15 | **Lean ground truth (optional per project)** | If enabled: `lake build` must produce sorry=0, error=0, warning=0. Add `lean: "lake build"` to config to activate. |
| HR16 | **SA-가려진 경로에 SCW 없이 편집 금지** | SemanticAnchor 또는 SPAN_*_ROOT가 이미 존재하는 파일/디렉터리(예: landing-site, 333-platform, metahumotonic-web)에 Write/Edit 호출 시 BLOCK — AtomicSpan+Contract+Task 체인 없이 직접 편집 = executor=reviewer 위반(D20). Pre-edit 확인: `MATCH (sa:SemanticAnchor)-[:COVERS_PATH*0..]->(p) WHERE $target_path STARTS WITH p.path RETURN sa` → 매치 존재 시 `/apt-sp` 진입 강제. # KG: lesson-apt-scw-skipped-ritual-css-2026-04-17, lesson-apt-vr-self-fulfilled-executor-reviewer-2026-04-16 |

---

## 1. Configuration (v26 A6 — KG slot resolve, NOT prose)

> **Magic number 박지 마세요.** 모든 설정값은 `MethodologyConfig_default_v26` 노드에서 resolve. SKILL.md 본문에 숫자 박는 순간 KG와 drift 발생 → Taliban reject.

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
| Taliban tiers (HR12) | LensSet 노드의 `lens_count` 조회 + `taliban_mixing_tiers` |
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

> 이 SKILL.md에서 "Prometheus", "Taliban", "88-Taliban", "Longinus", "재배맨" 등의
> concrete 이름은 MIC_v1 MethodologySlot의 **현재 바인딩(currentConcrete)**이다.
> Slot이 다른 concrete로 교체되면 이 파일의 이름도 drift한다.
> 정본 해석: `MATCH (mic:MethodologyIntegrationContract {name:'MIC_v1'})-[:HAS_SLOT]->(s) RETURN s.name, s.currentConcrete`
> 유틸리티: `03_SCRIPTS/db/resolve_mic_slot.cypher`
> # KG: lesson-skill-mic-slot-ref-weak-2026-04-15

---

## History

> Repo-level changes: [`/CHANGELOG.md`](../CHANGELOG.md). Per-commit: `git log -- apt/SKILL.md`.
> 학문 grounding: [`/PROM_16_SKILL_VERSIONING_REPORT.md`](../PROM_16_SKILL_VERSIONING_REPORT.md) (Lehman SCM 8 laws / Hyrum's Law).

| Version | Date | Summary | KG Ref |
|---|---|---|---|
| **v27** | 2026-04-30 | RFC bundle ACCEPTED: **A6 path A** pre-prompt resolver hook (Python + python-frontmatter + Jinja2 SandboxedEnv + KG Cypher) / **A6.1** magic selective externalization (5 core KG slot + 3 prose 유지, `magic_number_table.md` canonical) / **A7** Gate Hook 4-layer fail-closed (Resilience4j 500ms timeout + Redis state + JFrog audit log + auto fallback + break-glass allowlist + 점진 강제) / **A8** N-ary hypergraph GDSL (Neo4j DispatchHyperedge naming convention 정형화 → TypeDB PERA POC, Contract MLIR-dialect AST + Liquid Haskell refined types + IPLD/VFS folder-abstract). Frontmatter `version: "27.0.0"` bumped. Body migration in dedicated sprints (resolver 3w / N-ary 4+6w / gate 4w / magic 1+2w). | `lesson-prom16-apt-v26-unresolved-4-issues-2026-04-30`, `rfc-apt-v26-A6-resolver-path-A-pre-prompt-hook-2026-04-30`, `rfc-apt-v26-A6.1-magic-selective-externalization-2026-04-30`, `rfc-apt-v27-A7-gate-hook-fail-closed-4-layer-2026-04-30`, `rfc-apt-v27-A8-narray-hypergraph-gdsl-2026-04-30`, `sv-apt-v27.0.0` (+sa/sp/scw 패밀리) |
| **v26.1** | 2026-04-29 | RFC1 (C(S) ↔ A3 axiom layer 분리, Greek :ARCHIVED) + RFC2 (two-tier cleanup: local RGR + global Phase 6) + Apt_FourPlusOne motif | `rfc-apt-cs-axiom-visibility-drift-2026-04-29`, `rfc-apt-two-tier-cleanup-2026-04-29` |
| **v26** | 2026-04-21~25 | A6 resolve-only directive, MIC slot 7→10 (ContractSchema/LensSet/MethodologyConfig 추가), Gate Hook LensSet completeness Cypher enforcement (3-lens shortcut 차단) | `APT_v26_RFC_draft_2026-04-21`, `ATOM_APT_v26_Gate_Hook_Lens_Enforcement_2026-04-21`, `lesson-apt-v26-a6-skill-resolve-only-2026-04-25` |
| **v25** | 2026-04-17 | Contract 7-field + error_variants extension, SharedType→Contract.shared=true, meta-validation protocol, apt-progress.md 템플릿 | `APT_v25_RFC_draft_2026-04-17`, `lesson-apt-v25-skill-version-drift-2026-04-21` |
| **v24** | 2026-04-15 전후 | Contract v2 7-field, Lean 4 `lake build` integration (sorry=0 ground truth) | — |
| **v22** | 2026-04 초 | Gate Check enforcement via Claude Code Hook, Taliban --lens mathematical 5-round meta-verification (260✓→102✓ honest convergence), HR11 evidence-backed verdicts | `lesson-feedback-is-emergent-not-weapon-2026-04-16` |
| **v17** | (older) | Marker "End of APT v17 Orchestrator SKILL.md" 본문 fossil | — |
| **v5~v20** | timestream | Historical evolution. MinIO archive: `bhgman/apt-docs/v{N}/` | `APT_v5..APT_v20` (16 AptVersion nodes) |

→ KG SkillVersion query: `MATCH (sv:SkillVersion {skill_name:'apt'}) RETURN sv ORDER BY sv.version DESC`

### Architectural changes (post-v26)

| Change | Date | Source | Detail |
|---|---|---|---|
| **Progressive Disclosure refactor** | 2026-04-29 | PROM 16 F6.1 | SKILL.md 1804 → 381 lines (slim core) + 8 lazy-load `references/*.md` (phases/gates/adversarial/kg_logging/error_handling/validation/theory/quick_ref). Stale legacy refs → `references/_legacy/`. Anthropic engineering blog "Equipping agents" P-D 3-level grounding. |
| **`## History` section + SemVer migration** | 2026-04-29 | PROM 16 F2/F3 | frontmatter `version: 26` → `"26.0.0"`. SkillVersion KG node `sv-apt-v26.0.0`. |

# KG history: ATOM_Skill_apt_orchestrator (binding root) / lesson-prom16-skill-versioning-academic-2026-04-29 / lesson-prom16-skillver-progressive-disclosure-drift-2026-04-29

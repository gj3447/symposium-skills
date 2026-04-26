---
name: apt
kg_ref: ATOM_Skill_apt_orchestrator
version: 26
channel: stable
description: >
  APT v26 orchestrator — KG 정본 기반. Gate Check Hook 강제. SA→SP→ST→SCW 순환.
  v5~v21 역사 반영. 하네스 4축 + 5대 무기(하네스/탈레반/프로메테우스/롱기누스/재배맨) + D(S)/C(S) + Crystallization Frontier.
  # KG: ATOM_Skill_apt_orchestrator, APT_v26_RFC_draft_2026-04-21 (A1-A6 pluggable MIC slots 7→10)
  # KG: APT_v25_RFC_draft_2026-04-17 (error_variants extension, SharedType→shared=true, meta-validation)
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
    |       +-- [GATE: C(S) predicate check]
    |       +-- [GATE: Adversarial Round (C_S_sigma)]
    |       +-- [GATE: sigma_oracle (HUMAN)] -- BLOCK until human responds
    |       |
    |       v
    +-- Branch has AtomicSpan ---------> /apt-st (PH4)
    |       |
    |       +-- [GATE: Adversarial Round (RefinementGate)]
    |       +-- [GATE: sigma_oracle (HUMAN)] -- BLOCK until human responds
    |       |
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
```

### 3.2 Gate Sequence at Each Transition

Every transition follows this EXACT sequence. No steps may be skipped.

#### PH3 (SP Decomposition) Gate Sequence:

```
1. KG Density Check (D21)
   - Query INFORMED_BY count
   - If < 5: BLOCK --> run KAL
   - Check source type diversity
   - If < 3 types: BLOCK --> diversify via KAL
   - Check foundation:composite ratio
   - If < 2:1: BLOCK --> acquire more foundational sources

2. C(S) Predicate Evaluation (cheap rejection first)
   - v (complexity <= 500 lines)
   - tau (concrete I/O types)
   - iota (testable assertions)
   - delta (decomposition diseconomy)
   - sigma_auto (automated check)

3. Adversarial Round (C_S_sigma)
   - Spawn adversarial-critic agent (sonnet model)
   - Critic receives: decomposition plan, INFORMED_BY links, span context
   - Critic MUST produce >= 3 findings
   - If < 3 findings: re-run with STRONGER prompt (see Section 7.2)
   - Each finding logged as AptFeedback node in KG
   - WebSearch evidence MUST be cited for each design decision

4. Ground Truth Verification
   - KAL link density verified (automated)
   - Architecture pattern WebSearch completed
   - tau banned-type check executed

5. sigma_oracle (HUMAN)
   - Present to human: proposal + critic findings + ground truth results
   - BLOCK until human responds
   - Human decides: APPROVE | RETURN(reason) | ESCALATE
   - Decision logged as AptDecisionLog node in KG

6. Log to KG
   - Create AptDecisionLog node with full audit trail
   - Link to span, critic findings, ground truth results
```

#### PH4 (ST Crystallization) Gate Sequence:

```
1. Contract Completeness Check
   - input_type defined
   - output_type defined
   - acceptance_tests defined
   - postconditions falsifiable

2. Adversarial Round (RefinementGate)
   - Spawn adversarial-critic agent (sonnet model)
   - Critic receives: contract draft, task description, test sketch
   - Critic MUST produce >= 3 findings
   - If < 3 findings: re-run with STRONGER prompt
   - Each finding logged as AptFeedback node in KG
   - WebSearch evidence MUST be cited for design decisions

3. Ground Truth Verification
   - tau_check 5/5 passes
   - Postcondition falsifiability test passes
   - WebSearch for API compatibility, prior art

4. sigma_oracle (HUMAN)
   - Present to human: contract + critic findings + ground truth
   - BLOCK until human responds
   - Decision logged as AptDecisionLog node in KG

5. Log to KG
```

#### PH5 (SCW Implementation) Gate Sequence:

```
1. Implementation Completion
   - Code written following TDD (RED -> GREEN -> REFACTOR)
   - MATERIALIZES relationship created

2. Ground Truth Verification (MANDATORY -- runs FIRST)
   - cargo test: MUST pass (all tests green)
   - cargo build --release: MUST compile
   - cargo clippy -- -D warnings: MUST pass
   - If any fail: BLOCK -- fix before proceeding

3. Adversarial Round (FulfillmentGate)
   - Spawn adversarial-critic agent (sonnet model)
   - Critic receives: implemented code, contract, test results, coverage
   - Critic MUST produce >= 3 findings
   - If < 3 findings: re-run with STRONGER prompt
   - Each finding logged as AptFeedback node in KG
   - Ground-truth-testable findings get auto-verified (D23)

4. FulfillmentGate 13/13 Check
   - Checks 1-11: unchanged from v14
   - Check 12: Adversarial Critic review PASS -- no unresolved BLOCKERs
   - Check 13: Ground truth primacy verified -- all factual claims validated

5. sigma_oracle (HUMAN)
   - Present to human: code + test results + critic findings + coverage
   - BLOCK until human responds
   - Decision logged as AptDecisionLog node in KG

6. Log to KG
```

---

## 4. Adversarial Round Protocol (D20 -- MANDATORY)

### 4.1 The Four Stages

Every adversarial round follows these four stages. None may be skipped.

```
AdversarialRound(artifact, gate_name):

  Stage A -- PROPOSE:
    Design Agent presents artifact for gate passage.
    Artifact = {decomposition plan | contract draft | implemented code}.

  Stage B -- ATTACK:
    Critic Agent (adversarial-critic agent, sonnet model) reviews artifact.
    Critic MUST produce minimum 3 findings (HARD requirement).
    Each finding classified: BLOCKER | PERFORMANCE | DESIGN_DEBT | NITPICK.
    Critic also runs:
      - WebSearch for counter-evidence (compatibility, prior art, known issues)
      - KG knowledge contradiction check
    IF findings < 3:
      Re-run with stronger prompt (see Section 7.2)
      IF still < 3 after re-run: log anomaly, proceed with what we have

  Stage C -- GROUND TRUTH:
    Execute objective validation appropriate to gate:
      C_S_sigma:       KAL link count, tau banned-type check, v complexity check
      RefinementGate:  tau_check 5/5, postcondition falsifiability test
      FulfillmentGate: cargo test, cargo clippy, coverage measurement
    Ground truth results are AUTHORITATIVE (D23).
    If ground truth contradicts critic finding: finding DISMISSED.
    If ground truth confirms critic finding: finding UPGRADED to BLOCKER.

  Stage D -- DECIDE:
    sigma_oracle (HUMAN -- always) receives:
      1. Design Agent's proposal
      2. Critic Agent's findings (with severity classifications)
      3. Ground truth results (pass/fail, coverage numbers)
    sigma_oracle decides: APPROVE | RETURN(with reason) | ESCALATE
    BLOCK until human responds. Do NOT proceed without human decision.

  AFTER DECISION:
    Log AdversarialRoundCompleted event
    Create AptDecisionLog node in KG
    Create AptFeedback nodes for each finding
```

### 4.2 How to Spawn the Adversarial Critic

The adversarial-critic is defined as a Claude agent at:
`.claude/agents/adversarial-critic.md`

To invoke the critic, use the agent subcommand or tool with the following context:

```
Invoke adversarial-critic agent with:
  - model: sonnet (MUST differ from design agent model)
  - input: the artifact being reviewed
  - context: relevant KG nodes, sibling spans, parent contract
  - gate_name: which gate this is for
  - instructions: follow D22.3 Adversarial Critic Prompt Template
```

The critic agent's system prompt enforces:
- Minimum 3 findings
- Severity classification (BLOCKER/PERFORMANCE/DESIGN_DEBT/NITPICK)
- Evidence for each finding (URL or reasoning)
- At least 1 alternative approach
- WebSearch for counter-evidence

### 4.3 Gate-Specific Adversarial Application

| Gate | What Critic Attacks | Ground Truth Source | When |
|------|--------------------|--------------------|------|
| C_S_sigma | Decomposition completeness, missing concerns, over/under-splitting | KAL link density, architecture pattern check, WebSearch | Before sigma_oracle in SP |
| RefinementGate | Contract ambiguity, untestable postconditions, missing edge cases | tau_check 5/5, eval-optimizer metrics, WebSearch | After Crystallize(), before PH5 entry |
| FulfillmentGate | Code correctness, missed requirements, regression risk, API misuse | `cargo test`, `cargo clippy`, compiler output, coverage | After implementation, before DONE |

### 4.4 Adversarial Critic Prompt Template (D22.3)

When invoking the adversarial-critic agent, ensure this template is part of the context:

```markdown
# Adversarial Critic Review

You are reviewing a {artifact_type} for APT gate passage: {gate_name}.

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

## 5. KG Density Check (D21 -- MANDATORY)

### 5.1 When to Run

BEFORE any SP decomposition begins. This is a prerequisite, not a post-check.

### 5.2 Three Requirements

| # | Requirement | Threshold | On Fail |
|---|------------|-----------|---------|
| 1 | Min INFORMED_BY links | >= 5 | BLOCK --> run KAL to acquire knowledge |
| 2 | Min source type diversity | >= 3 distinct types | BLOCK --> diversify via targeted KAL |
| 3 | Foundation:composite ratio | >= 2:1 | BLOCK --> acquire more foundational sources |

### 5.3 Source Types (Enumerated)

```
paper          - Academic paper, arXiv, journal
implementation - Existing codebase, library source
documentation  - Official docs, API reference, man pages
experiment     - Empirical test results, benchmarks, PoC outcomes
expert         - Domain expert knowledge, design rationale
specification  - RFC, W3C spec, language spec, protocol spec
prior_art      - Similar projects, case studies
```

### 5.4 Foundation vs. Composite Classification

```python
def classify_knowledge_node(node: dict) -> str:
    """Classify a KnowledgeNode as 'foundation' or 'composite'.

    Foundation: directly observed/measured/read from primary source.
    Composite: derived from combining multiple foundation nodes.
    """
    if node.get("derived_from") and len(node["derived_from"]) > 0:
        return "composite"
    if node.get("source_type") in ("paper", "specification", "experiment", "implementation"):
        return "foundation"
    if node.get("is_synthesis", False):
        return "composite"
    return "foundation"  # default to foundation for simple knowledge
```

### 5.5 Density Check Query

```cypher
// V27 (v15/v17): Foundational Density -- source type diversity + foundation ratio
MATCH (s:AptSpan {name: $target_span})-[:INFORMED_BY]->(k:KnowledgeNode)
WITH s,
  count(k) AS total_links,
  count(DISTINCT k.source_type) AS source_type_count,
  count(CASE WHEN k.classification = 'foundation' THEN 1 END) AS foundation_count,
  count(CASE WHEN k.classification = 'composite' THEN 1 END) AS composite_count
RETURN s.name AS span,
  total_links,
  source_type_count,
  foundation_count,
  composite_count,
  total_links >= 5 AS link_count_pass,
  source_type_count >= 3 AS diversity_pass,
  CASE WHEN composite_count = 0 THEN true
       ELSE foundation_count >= 2 * composite_count END AS ratio_pass
```

### 5.6 Density Check Procedure

```
PROCEDURE DensityCheck(span_name):
  1. Run density check query (Section 5.5)
  2. IF total_links < 5:
       LOG "BLOCKED: INFORMED_BY count {total_links} < 5"
       RUN KAL(span_name) -- broad search
       GOTO step 1
  3. IF source_type_count < 3:
       missing_types = REQUIRED_TYPES - existing_types
       LOG "BLOCKED: only {source_types} present, need 3+ types"
       RUN KAL(span_name, target_types=missing_types) -- targeted search
       GOTO step 1
  4. IF foundation_count < 2 * composite_count:
       LOG "BLOCKED: foundation:composite = {f}:{c}, need >= 2:1"
       RUN KAL(span_name, target_classification="foundation") -- foundational search
       GOTO step 1
  5. LOG "DENSITY CHECK PASSED"
  6. Create AptDecisionLog node:
       gate_type = "DensityCheck"
       decision = "PASS"
       evidence = {total_links, source_type_count, foundation_count, composite_count}
  7. RETURN PASS
```

### 5.7 KAL Search Triggers (7 Types)

| # | Condition | Search Type | Result |
|---|-----------|-------------|--------|
| 1 | links(S) < 5 | Broad KG search | Find related concepts, research, entities |
| 2 | C(S) v-fail (too complex) | Targeted: decomposition patterns | Find similar modules that were successfully split |
| 3 | C(S) t-fail (vague types) | Targeted: type definitions | Find concrete DTOs, schemas, API specs |
| 4 | C(S) i-fail (untestable) | Targeted: test examples | Find similar test patterns, assertion templates |
| 5 | C(S) d-fail (too small) | N/A | No search needed (merge upward) |
| 6 | C(S) s-fail (semantic gap) | Domain-specific search | Find domain papers, ontologies, standards |
| 7 | Manual trigger | User-specified | Custom query against KG or web |

### 5.8 KnowledgeNode Creation from KAL

```cypher
MERGE (k:KnowledgeNode {name: $name})
SET k.source = $source,
    k.source_type = $source_type,
    k.classification = $classification,
    k.content_summary = $summary,
    k.url = $url,
    k.confidence = $confidence,
    k.searched_at = datetime(),
    k.search_trigger = $trigger

WITH k
MATCH (s:AptSpan {name: $span_name})
MERGE (s)-[:INFORMED_BY {
  reason: $why,
  source: $search_source,
  linked_at: datetime(),
  auto_acquired: true
}]->(k)
```

### 5.9 Density Check in Lite Mode (JSON)

```python
def density_check(span: dict, config: dict) -> dict:
    """v17: Check foundational density requirements."""
    knowledge = span.get("informed_by", [])
    total = len(knowledge)
    source_types = set(k.get("source_type", "unknown") for k in knowledge)
    foundation = [k for k in knowledge if classify_knowledge_node(k) == "foundation"]
    composite = [k for k in knowledge if classify_knowledge_node(k) == "composite"]

    return {
        "total_links": total,
        "min_links_pass": total >= config.get("min_informed_by", 5),
        "source_types": list(source_types),
        "source_diversity_pass": len(source_types) >= 3,
        "foundation_count": len(foundation),
        "composite_count": len(composite),
        "ratio_pass": len(composite) == 0 or len(foundation) >= 2 * len(composite),
        "all_pass": (total >= config.get("min_informed_by", 5)
                     and len(source_types) >= 3
                     and (len(composite) == 0 or len(foundation) >= 2 * len(composite))),
    }
```

---

## 6. Ground Truth Primacy (D23 -- MANDATORY)

### 6.1 Authority Hierarchy

```
For FACTUAL claims (does code compile? do tests pass? is this API compatible?):

  AUTHORITATIVE (cannot be overridden by opinion):
    1. Compiler output (cargo build, rustc, gcc, tsc)
    2. Test execution results (cargo test, pytest, jest)
    3. Runtime behavior (browser execution, WASM execution)
    4. External evidence (WebSearch for API docs, compatibility tables)

  ADVISORY (informs decisions but cannot override authoritative sources):
    5. Critic Agent findings
    6. Design Agent claims

  LEAST AUTHORITATIVE for factual matters:
    7. Human intuition ("I think this should work")

For DESIGN/ARCHITECTURAL decisions:
  Human judgment (sigma_oracle) remains supreme.
  D23 does NOT apply to design decisions.
```

### 6.2 Ground Truth Override Rule

```
GroundTruthOverride(finding, ground_truth_result):
  IF finding.ground_truth_testable == true:
    test_result = RUN ground_truth_command(finding)
    IF test_result CONTRADICTS finding:
      finding.status = "OVERRIDDEN_BY_GROUND_TRUTH"
      finding.severity = "DISMISSED"
      LOG "Finding {finding.id} dismissed: ground truth contradicts critic"
    ELIF test_result CONFIRMS finding:
      finding.status = "CONFIRMED_BY_GROUND_TRUTH"
      IF finding.severity != BLOCKER:
        finding.severity = BLOCKER   # upgrade
      LOG "Finding {finding.id} upgraded to BLOCKER: ground truth confirms"
```

### 6.3 Per-Gate Ground Truth Requirements

| Gate | Ground Truth Required | Command / Method |
|------|----------------------|------------------|
| C_S_sigma (SP) | WebSearch evidence for each design decision | WebSearch + cite URL |
| C_S_sigma (SP) | KAL link density verified | Density check query |
| RefinementGate (ST) | WebSearch evidence for API choices | WebSearch + cite URL |
| RefinementGate (ST) | tau_check 5/5 passes | Automated type check |
| FulfillmentGate (SCW) | `cargo test` passes | `cargo test 2>&1` |
| FulfillmentGate (SCW) | `cargo build --release` compiles | `cargo build --release 2>&1` |
| FulfillmentGate (SCW) | `cargo clippy` clean | `cargo clippy -- -D warnings 2>&1` |
| FulfillmentGate (SCW) | Coverage measured | Coverage tool output |

### 6.4 Practical Application

| Claim Type | Ground Truth Source | Example |
|-----------|-------------------|---------|
| "This code compiles" | `cargo build 2>&1` | Compiler error on line 42 = AUTHORITATIVE |
| "Tests pass" | `cargo test 2>&1` | 3 tests fail = AUTHORITATIVE |
| "This API exists in version X" | WebSearch + official docs | Deprecated in v3 = AUTHORITATIVE |
| "This will be fast enough" | Benchmark execution | p99=500ms vs 100ms target = AUTHORITATIVE |
| "This is the right architecture" | NOT ground-truth-testable | sigma_oracle decides |
| "This decomposition is complete" | NOT ground-truth-testable | sigma_oracle decides |

### 6.5 FulfillmentGate Ground Truth Check (v17)

```python
def fulfillment_check_13_ground_truth(findings: list, test_results: dict) -> bool:
    """v17: Verify all ground-truth-testable claims have been validated.

    Returns False if any factual claim relies solely on agent opinion
    when a ground truth test was available but not run.
    """
    for finding in findings:
        if finding.get("ground_truth_testable") and not finding.get("ground_truth_result"):
            return False  # testable claim without actual test = FAIL
    # Also verify: test suite actually ran (not just claimed to pass)
    if not test_results.get("executed"):
        return False
    return True
```

---

## 7. Anti-Bypass Mechanisms

### 7.1 Detection Rules

| # | Bypass Attempt | Detection | Response |
|---|---------------|-----------|----------|
| 1 | Critic returns < 3 findings | Count check | Re-run with stronger prompt (Section 7.2) |
| 2 | Same model for design and critique | Model comparison | BLOCK -- switch critic model |
| 3 | No human response to sigma_oracle | Response check | BLOCK and re-ask. Never assume approval. |
| 4 | Agent tries to auto-approve sigma | Config check | BLOCKED by allow_agent_sigma: false |
| 5 | Gate transition without adversarial round | KG audit (V28) | BLOCK -- run adversarial round |
| 6 | Ground-truth-testable claim not tested | KG audit (V29) | BLOCK -- run ground truth command |
| 7 | Critic produces only NITPICK findings 5+ times | Severity distribution | Rotate critic model + alert |
| 8 | Design agent ignores PERFORMANCE findings | Diff comparison | Escalate to sigma_oracle |
| 9 | All findings dismissed by ground truth 3+ times | Override history | Review critic prompt for hallucination |
| 10 | sigma_oracle approves without reviewing findings | Cannot detect automatically | Include findings summary in approval prompt |

### 7.2 Stronger Prompt for Insufficient Findings

When the critic returns fewer than 3 findings, re-invoke with this escalated prompt:

```markdown
# ESCALATED ADVERSARIAL REVIEW

Your previous review produced only {N} findings. The minimum is 3.
This is NOT acceptable. You MUST find at least 3 issues.

Mandatory deep-dive checklist:
1. Re-read EVERY line of the artifact. What could go wrong at runtime?
2. What happens with EMPTY input? NULL input? MAXIMUM-SIZE input?
3. What concurrent access patterns could cause race conditions?
4. What happens if a DEPENDENCY changes its API?
5. What error handling is MISSING?
6. What SECURITY implications exist?
7. What PERFORMANCE characteristics are unverified?
8. Does this violate ANY APT axiom (A1-A4)?
9. Is every postcondition ACTUALLY TESTABLE with concrete assertions?
10. What would a HOSTILE code reviewer say about this?

You MUST produce at least 3 findings. If you still cannot, produce 3 NITPICK
findings with documented evidence of thorough review methodology.
```

### 7.3 Model Separation Enforcement

| Design Agent | Acceptable Critic | Rationale |
|-------------|------------------|-----------|
| opus | sonnet or haiku | Different weights = different biases |
| sonnet | haiku or opus | Cross-tier critique |
| Any model | Same model, different temperature | INSUFFICIENT -- same weights |
| Any model | Same model, different prompt only | INSUFFICIENT -- framing contagion |

**v17 enforcement**: Before spawning critic, check that critic_model != design_model.
If they match, BLOCK and log error.

**Lite Mode exception**: When only one model is available, the same model MAY serve as
critic but MUST use the full D22.3 template AND all anti-rubber-stamp techniques are
MANDATORY. This exception must be logged as AptDecisionLog with reason.

### 7.4 Anti-Rubber-Stamp Techniques (10)

| # | Technique | Mechanism | Detects |
|---|-----------|-----------|---------|
| 1 | Model separation | Different model weights | Confirmation bias contagion |
| 2 | Minimum finding count | Hard minimum of 3 | Lazy approval |
| 3 | Core assumption challenge | 1+ finding must target core assumption | Surface-only critique |
| 4 | Anti-checklist | 10-item checklist critic must address | Incomplete review |
| 5 | Falsifiability requirement | Every finding must be testable/verifiable | Vague handwaving |
| 6 | Ground truth cross-check | ground_truth_testable findings auto-verified | Phantom bugs |
| 7 | Severity distribution audit | >80% NITPICK across 5+ rounds = flag | Nitpick-only rubber-stamp |
| 8 | Historical finding rate | Track findings-per-round; alert if always 3 | Gaming the minimum |
| 9 | Blind review | Critic does not see previous sigma_oracle decisions | Anchoring to authority |
| 10 | Rotation | Critic model rotated after 5+ consecutive rounds | Adaptation/overfitting |

---

## 8. KG Logging Procedures (MANDATORY)

### 8.1 AptDecisionLog Node (Every Gate Transition)

```cypher
CREATE (dl:AptDecisionLog {
  id: randomUUID(),
  gate_type: $gate_type,
  span_name: $span_name,
  decision: $decision,
  decided_by: $decided_by,
  decided_at: datetime(),
  adversarial_verdict: $adversarial_verdict,
  adversarial_findings_count: $findings_count,
  adversarial_blockers: $blocker_count,
  ground_truth_pass: $ground_truth_pass,
  ground_truth_details: $ground_truth_details,
  evidence_summary: $evidence_summary,
  override_reason: $override_reason
})
WITH dl
MATCH (s:AptSpan {name: $span_name})
MERGE (dl)-[:TARGETS]->(s)
RETURN dl.id, dl.gate_type, dl.decision
```

**gate_type values**: `DensityCheck`, `C_S_sigma`, `RefinementGate`, `FulfillmentGate`, `IntegrationGate`

**decision values**: `PASS`, `RETURN`, `ESCALATE`, `BLOCKED`, `OVERRIDE`

### 8.2 AptFeedback Node (Every Adversarial Finding)

```cypher
MERGE (fb:AptFeedback {name: $finding_id})
SET fb.category = $category,
    fb.severity = $severity,
    fb.status = 'open',
    fb.description = $claim,
    fb.evidence = $evidence,
    fb.suggestion = $suggestion,
    fb.ground_truth_testable = $ground_truth_testable,
    fb.ground_truth_result = $ground_truth_result,
    fb.gate_type = $gate_type,
    fb.critic_model = $critic_model,
    fb.created_at = datetime(),
    fb.created_by = 'adversarial-critic',
    fb.target_span = $target_span,
    fb.target_contract = $target_contract
WITH fb
OPTIONAL MATCH (s:AptSpan {name: $target_span})
FOREACH (_ IN CASE WHEN s IS NOT NULL THEN [1] ELSE [] END |
  MERGE (fb)-[:TARGETS]->(s)
)
RETURN fb.name, fb.severity, fb.status
```

### 8.3 Override/Skip Log (When Human Explicitly Allows)

```cypher
CREATE (ol:AptDecisionLog {
  id: randomUUID(),
  gate_type: $gate_type,
  span_name: $span_name,
  decision: 'OVERRIDE',
  decided_by: 'human',
  decided_at: datetime(),
  override_reason: $human_provided_reason,
  overridden_rule: $rule_id,
  adversarial_verdict: $original_verdict,
  adversarial_findings_count: $findings_count,
  adversarial_blockers: $blocker_count
})
WITH ol
MATCH (s:AptSpan {name: $span_name})
MERGE (ol)-[:TARGETS]->(s)
RETURN ol.id, ol.decision, ol.override_reason
```

**CRITICAL**: The `override_reason` MUST come from the human. The agent MUST NOT generate
a reason on behalf of the human. If the human says "skip", ask "Why?" and log their answer.

### 8.4 Query Open Feedback

```cypher
MATCH (fb:AptFeedback)
WHERE fb.status = 'open'
RETURN fb.category AS category,
       fb.severity AS severity,
       count(fb) AS open_count,
       collect(fb.name) AS items
ORDER BY
  CASE fb.severity
    WHEN 'BLOCKER' THEN 0
    WHEN 'PERFORMANCE' THEN 1
    WHEN 'DESIGN_DEBT' THEN 2
    WHEN 'NITPICK' THEN 3
  END
```

### 8.5 Query Decision Audit Trail

```cypher
// Full audit trail for a span
MATCH (dl:AptDecisionLog)-[:TARGETS]->(s:AptSpan {name: $span_name})
RETURN dl.gate_type, dl.decision, dl.decided_by, dl.decided_at,
       dl.adversarial_verdict, dl.adversarial_findings_count,
       dl.adversarial_blockers, dl.ground_truth_pass,
       dl.override_reason
ORDER BY dl.decided_at ASC
```

### 8.6 Resolve Feedback

```cypher
MATCH (fb:AptFeedback {name: $finding_id})
SET fb.status = 'resolved',
    fb.resolved_at = datetime(),
    fb.resolved_by = $agent,
    fb.resolution = $resolution
RETURN fb.name, fb.status, fb.resolution
```

### 8.7 Adversarial Round Trajectory Record (for KG persistence)

```python
# v17 trajectory record -- saved to KG after each adversarial round
trajectory_record = {
    "gate": "FulfillmentGate",
    "span_name": "SpanName",
    "critic_model": "sonnet",
    "design_model": "opus",
    "findings_count": 4,
    "blockers": 1,
    "performance": 1,
    "design_debt": 1,
    "nitpick": 1,
    "ground_truth_overrides": 0,
    "verdict": "REJECT",
    "resolution": "fixed blocker, re-passed",
    "ground_truth_results": {
        "cargo_test": "PASS (12/12)",
        "cargo_clippy": "PASS (0 warnings)",
        "coverage": 0.87
    },
    "sigma_oracle_decision": "APPROVE",
    "sigma_oracle_is_human": True,
    "timestamp": "2026-03-26T12:00:00Z"
}
```

---

## 9. Error Handling

### 9.1 When Critic Disagrees with Design Agent

```
IF critic verdict = REJECT (>= 1 BLOCKER):
  1. Design agent reviews BLOCKER findings
  2. For ground_truth_testable findings: run ground truth command
     - If ground truth CONFIRMS: fix the issue, re-submit
     - If ground truth CONTRADICTS: finding dismissed (log override)
  3. For non-testable findings: present to sigma_oracle with both perspectives
  4. sigma_oracle decides: fix it | dismiss with reason | escalate
  5. Log decision as AptDecisionLog

IF critic verdict = CONDITIONAL_PASS (PERFORMANCE findings):
  1. Design agent reviews PERFORMANCE findings
  2. Run benchmarks if applicable
  3. sigma_oracle decides: fix now | accept with tech debt | escalate
  4. Log decision

IF critic verdict = PASS (only DESIGN_DEBT + NITPICK):
  1. Log findings as tech debt
  2. Proceed to sigma_oracle for final approval
  3. sigma_oracle may still RETURN for any reason
```

### 9.2 When Ground Truth Fails

```
IF cargo test fails:
  1. BLOCK gate immediately
  2. Fix the failing tests
  3. Re-run cargo test
  4. Only proceed when ALL tests pass
  5. Re-run adversarial round (critic sees updated code)

IF cargo build fails:
  1. BLOCK gate immediately
  2. Fix compilation errors
  3. Re-run from step 1

IF WebSearch contradicts design decision:
  1. Log the contradiction as AptFeedback (severity: BLOCKER)
  2. Present to sigma_oracle with evidence
  3. sigma_oracle decides: change approach | accept with justification
```

### 9.3 When sigma_oracle Does Not Respond

```
IF sigma_oracle prompt sent and no response in current context:
  1. DO NOT PROCEED
  2. DO NOT auto-approve
  3. Re-state the question clearly
  4. List what needs approval:
     - The proposal summary
     - Critic findings (count + severities)
     - Ground truth results
  5. Wait for human response
  6. If conversation continues on different topic: remind about pending approval
```

### 9.4 When Adversarial Round Reaches Max Iterations

```
IF adversarial_rounds >= max_adversarial_rounds (3):
  1. Log all findings from all rounds
  2. Escalate to sigma_oracle with full history
  3. sigma_oracle decides:
     - APPROVE with remaining findings as accepted debt
     - RETURN to earlier phase (SP/ST)
     - ABORT the span entirely
  4. Log decision with all context
```

### 9.5 When KAL Cannot Satisfy Density Requirements

```
IF KAL runs 3+ times and density still not met:
  1. Log current state (what types are missing, what ratio is)
  2. Present to sigma_oracle:
     "Density requirements not met after 3 KAL iterations.
      Current: {count} links, {types} source types, {ratio} ratio.
      Required: 5 links, 3 types, 2:1 ratio.
      Options: (a) override with justification, (b) manual knowledge entry, (c) abort span"
  3. sigma_oracle decides
  4. Log decision as AptDecisionLog with override_reason if applicable
```

### 9.6 When Critic and Design Agent Both Wrong (Meta-Failure)

```
IF sigma_oracle detects both agents converged on wrong approach:
  1. sigma_oracle provides correction
  2. Log as AptFeedback category="FalseNegative" (validation missed real issue)
  3. Reset to earlier phase if needed
  4. Record in KG for future training (KG as persistent weight space -- D24)
  5. Consider rotating both models for next round
```

---

## 10. Validation Commands (V1-V29)

### 10.1 Axiom Checks (P1 -- Critical)

| V# | Target | What It Checks |
|----|--------|---------------|
| V1 | A1: ContractOnlyAtST | Contract owner is SemanticTwin |
| V2 | A3: SiblingIndependence | No DEPENDS_ON between siblings |
| V5 | A4: FrontierUniqueness | CRYSTALLIZES_TO is sole SP->ST bridge |
| V6 | Cycle Detection | No cycles in DECOMPOSES_TO |
| V15 | Self-Approval | executor != reviewer |

### 10.2 Structural Checks (P2-P3)

| V# | Target | What It Checks | Severity |
|----|--------|---------------|:--------:|
| V3 | A2: BranchingFactor | Non-atomic Spans have >= 2 children | P2 |
| V4 | A2: Termination | All leaves are AtomicSpan | P3 |
| V7 | Injective CRYSTALLIZES_TO | 1 AtomicSpan -> 1 Twin | P2 |
| V8 | Functional HAS_CONTRACT | 1 Twin -> 1 Contract | P2 |
| V9 | Label Disjointness | No forbidden label combos | P2 |
| V10 | Duplicate Twin Names | Twin names are unique | P2 |
| V11 | Null Status | All core nodes have status | P3 |
| V12 | Orphan Contract | All Contracts owned by a Twin | P3 |
| V13 | Chain Completeness | atoms = twins = contracts | P2 |
| V14 | Hub Integrity | CrystallizationEvent has atom role | P3 |
| V16 | Sparse Links | INFORMED_BY >= 5 | P4 |
| V17 | Stale Lock | No locks held > 1 hour | P3 |

### 10.3 Parallel Execution Checks (P1-P3)

| V# | Target | What It Checks | Severity |
|----|--------|---------------|:--------:|
| V18 | Duplicate SharedType | No duplicate SharedType nodes | P1 |
| V19 | Orphan SharedType | All SharedTypes referenced | P3 |
| V20 | Producer without consumer | Every OUTPUTS_TYPE has matching INPUTS_TYPE | P2 |

### 10.4 Adversarial Validation Checks (v17 -- P1)

| V# | Target | What It Checks | Severity |
|----|--------|---------------|:--------:|
| V27 | Foundational Density | source_types >= 3, foundation:composite >= 2:1 | P1 |
| V28 | Adversarial Round Completion | Every gate passage has an adversarial round | P1 |
| V29 | Ground Truth Primacy | No unresolved ground-truth-testable findings | P1 |

### 10.5 V28: Adversarial Round Completion Query

```cypher
// V28: Every gate passage must have an adversarial round
MATCH (s:AptSpan)
WHERE s.status IN ['crystallized', 'fulfilled']
  AND NOT EXISTS {
    MATCH (s)<-[:TARGETS]-(dl:AptDecisionLog)
    WHERE dl.gate_type IN ['C_S_sigma', 'RefinementGate', 'FulfillmentGate']
      AND dl.adversarial_verdict IS NOT NULL
  }
RETURN s.name AS span_missing_adversarial,
  s.status AS current_status,
  "v17 VIOLATION: gate passed without adversarial round" AS reason
```

### 10.6 V29: Ground Truth Primacy Query

```cypher
// V29: No unresolved ground-truth-testable findings
MATCH (fb:AptFeedback)
WHERE fb.ground_truth_testable = true
  AND fb.ground_truth_result IS NULL
  AND fb.status <> 'resolved'
  AND fb.severity IN ['BLOCKER', 'PERFORMANCE']
RETURN fb.name AS finding,
  fb.gate_type AS gate,
  fb.description AS untested_claim,
  "v17 VIOLATION: ground-truth-testable finding not verified" AS reason
```

### 10.7 Quick Health Check

Run V1, V2, V5, V6, V15, V28, V29 (all P1 severity). These are the minimum checks.

Full query definitions for V1-V20: see `references/apt_reference.md` (SS31).

---

## 11. Phase Transition Guards

### 11.1 Before /apt-sa

No prerequisite. This is the entry point for new projects.

### 11.2 Before /apt-sp

```cypher
MATCH (sa:SemanticAnchor {name: $project}) RETURN sa.name
MATCH (span:AptSpan {name: $target}) RETURN span.name, labels(span)
```

**v17 ADDITION**: Run Density Check (Section 5) BEFORE decomposition begins.

### 11.3 Before /apt-st (C(S) gate)

All 5 crystallization criteria must pass. Evaluation order: cheap rejection first.

| Order | Symbol | Criterion | Gate | On Fail |
|:-----:|:------:|-----------|:----:|---------|
| 1st | v | Complexity <= 500 lines | auto | Split -- too large |
| 2nd | tau | Type Expressibility -- concrete I/O types | auto | Split by type boundary |
| 3rd | iota | Test Feasibility -- concrete assertions | auto | Sharpen with examples |
| 4th | delta | Decomposition Diseconomy -- further split < 100 lines? | auto | Merge upward |
| 5th | sigma | Semantic Completeness | **HUMAN** | sigma_auto first, then sigma_oracle |

**v17 ADDITION**: Between sigma_auto pass and sigma_oracle, run:
1. Adversarial Round (C_S_sigma) -- Section 4
2. Ground Truth verification -- Section 6
3. sigma_oracle receives: proposal + critic findings + ground truth

```cypher
MATCH (span:AptSpan {name: $target})
RETURN span:AtomicSpan AS is_atomic
// If not atomic, all 5 predicates must be verified before proceeding to /apt-st
```

### 11.4 Before /apt-scw (Contract completeness gate)

```cypher
MATCH (st:SemanticTwin {name: $target})-[:HAS_CONTRACT]->(c:AptContract)
RETURN c.name,
  c.input_type IS NOT NULL AS has_input,
  c.output_type IS NOT NULL AS has_output,
  c.acceptance_tests IS NOT NULL AS has_tests,
  c.status AS status
// ALL must be present. If any is missing -> return to /apt-st
```

**v17 ADDITION**: Verify RefinementGate adversarial round completed:
```cypher
MATCH (s:AptSpan {name: $span_name})<-[:TARGETS]-(dl:AptDecisionLog)
WHERE dl.gate_type = 'RefinementGate'
  AND dl.adversarial_verdict IS NOT NULL
  AND dl.decision = 'PASS'
RETURN dl.id, dl.decided_at
```

### 11.5 After /apt-scw (Materialization verification)

```cypher
MATCH (c:AptContract {name: $ct})-[:MATERIALIZES]->(src:SourceCodeNode)
RETURN src.file_path, src.status, src.lines
// src must exist and status = 'implemented'
```

**v17 ADDITION**: Verify FulfillmentGate adversarial round completed AND cargo test passed:
```cypher
MATCH (s:AptSpan {name: $span_name})<-[:TARGETS]-(dl:AptDecisionLog)
WHERE dl.gate_type = 'FulfillmentGate'
  AND dl.adversarial_verdict IS NOT NULL
  AND dl.ground_truth_pass = true
  AND dl.decision = 'PASS'
RETURN dl.id, dl.decided_at
```

---

## 12. Gate Evidence Table (v17)

```
Gate Evidence Table (v17):
+---------------+--------------------------------------------------------------+
| Transition    | Required Evidence                                            |
+---------------+--------------------------------------------------------------+
| -> PH3 (SP)  | SA exists AND root span created                              |
| SP internal   | KAL complete AND INFORMED_BY >= 5                            |
|               | v17: source_types >= 3 AND foundation:composite >= 2:1       |
|               | v17: DensityCheck logged in KG                               |
+---------------+--------------------------------------------------------------+
| -> PH4 (ST)  | C(S) auto pass AND sigma_oracle approved                     |
|               | v17: AdversarialRound(C_S_sigma) -- no BLOCKERs             |
|               | v17: WebSearch evidence cited for design decisions           |
|               | v17: sigma_oracle is HUMAN (allow_agent_sigma: false)        |
|               | v17: AptDecisionLog created in KG                            |
+---------------+--------------------------------------------------------------+
| -> PH5 (SCW) | tau_check 5/5 AND impact_tests defined                       |
|               | v17: AdversarialRound(RefinementGate) -- no BLOCKERs        |
|               | v17: WebSearch evidence for API choices                      |
|               | v17: sigma_oracle is HUMAN                                   |
|               | v17: AptDecisionLog created in KG                            |
+---------------+--------------------------------------------------------------+
| PH5 -> DONE  | FulfillmentGate 13/13 AND coverage AND NFR                   |
|               | v17: cargo test PASS (MANDATORY before anything else)        |
|               | v17: cargo clippy PASS                                       |
|               | v17: AdversarialRound(FulfillmentGate) completed             |
|               | v17: Ground truth primacy verified (all claims tested)       |
|               | v17: sigma_oracle is HUMAN                                   |
|               | v17: AptDecisionLog created in KG                            |
+---------------+--------------------------------------------------------------+
| -> PH6       | AptFeedback created (category + severity)                    |
+---------------+--------------------------------------------------------------+
```

---

## 13. Parallel Execution (D12)

### 13.1 Five Rules

| Rule | Description |
|------|-------------|
| SameLayer | Same parent's children = all parallel (A3 guarantees independence) |
| ParentChild | Parent decomposition complete -> then children. Vertical = sequential. |
| CrossBranch | Independent branches may be in different phases simultaneously. |
| AtomicIndependent | Sibling becomes AtomicSpan -> proceeds to PH4 independently. |
| LayerGateFirst | All children created -> RefinementGate -> then descend. |

### 13.2 SharedType (D14-D16)

Parent Span defines boundary types shared between children BEFORE children enter ST.

```
(Parent)--DEFINES_SHARED_TYPE-->(World:SharedType)<--OUTPUTS_TYPE--(CT_WorldGen)
                                       ^
                              INPUTS_TYPE
                                       |
                                (CT_Renderer)
```

- One type = one node (D14). MERGE only.
- Parent defines first (D15). Children reference only.
- SEQUENCED_WITH auto-derived (D16). From OUTPUTS_TYPE -> INPUTS_TYPE pairs.

### 13.3 Visibility Scope (D13)

| Phase | Can See | Cannot See |
|-------|---------|-----------|
| SP decomposition | Parent description + sibling names | Sibling internals, other branches |
| ST crystallization | Self + parent + SharedType | Sibling Contract internals |
| SCW implementation | Self Contract + target_file | Sibling source code |
| Integration | Sibling input/output_type | Sibling internal logic |

### 13.4 Layer Gates

| Gate | When | On Fail |
|------|------|---------|
| LayerDecomposition | After all children created | Delete children + re-decompose |
| CrystallizationEntry | Before PH4 entry | Remove AtomicSpan + back to PH3 |
| ContractComplete | Before PH5 entry | Contract draft + /apt-st |
| Fulfillment | After PH5 implementation | Re-implement / back to PH4/PH3 |
| Integration | After all siblings complete | Contract modification or re-decompose |

**v17**: Each layer gate ALSO requires adversarial round completion (V28).

### 13.5 Parallel Validation (V18-V20)

| V# | Target | Severity |
|----|--------|:--------:|
| V18 | Duplicate SharedType | P1 |
| V19 | Orphan SharedType (no references) | P3 |
| V20 | Producer without consumer | P2 |

---

## 14. Feedback System

### 14.1 Categories (10)

| # | Category | When to Use |
|---|----------|-------------|
| 1 | Bug | Code defect, postcondition violation |
| 2 | Confusion | Spec ambiguity, interpretation divergence |
| 3 | Missing | Missing Span, Contract, or test |
| 4 | Improvement | Feature enhancement request |
| 5 | Violation | Axiom or Principle violation detected |
| 6 | Conflict | Contradiction between Contracts or Spans |
| 7 | FalsePositive | Validation flagged normal as violation |
| 8 | FalseNegative | Validation missed a real violation |
| 9 | PerformanceDrift | Performance metric below baseline |
| 10 | SLABreach | SLA exceeded |

### 14.2 Record Feedback

```cypher
MERGE (fb:AptFeedback {name: $title})
SET fb.category = $category,
    fb.severity = $severity,
    fb.status = 'open',
    fb.description = $description,
    fb.created_at = datetime(),
    fb.created_by = $agent,
    fb.target_span = $target_span,
    fb.target_contract = $target_contract
WITH fb
OPTIONAL MATCH (s:AptSpan {name: $target_span})
FOREACH (_ IN CASE WHEN s IS NOT NULL THEN [1] ELSE [] END |
  MERGE (fb)-[:TARGETS]->(s)
)
RETURN fb.name, fb.status
```

Record feedback **immediately** when you discover a problem. Even minor confusion
accumulates into major APT violations.

### 14.3 Anti-Pattern: Adversarial Theater (v17)

| # | Anti-Pattern | Symptom | Detection | Prevention |
|---|-------------|---------|-----------|------------|
| 18 | Adversarial Theater | Critic produces exactly 3 NITPICK findings every round | Severity distribution audit, historical finding rate | Model rotation, sigma_oracle meta-review |

---

## 15. Mode Collapse Detection (D24)

### 15.1 Detection Signals

| Signal | Threshold | Action |
|--------|-----------|--------|
| Exactly 3 findings (minimum) for 5+ consecutive rounds | 5 rounds | Alert: critic may be rubber-stamping |
| Same NITPICK-only verdict for 3+ consecutive rounds | 3 rounds | Rotate critic model |
| Design agent does not modify artifact after PERFORMANCE findings | 2 rounds | Escalate to sigma_oracle |
| All findings dismissed by ground truth override | 3 rounds | Review critic prompt for hallucination |
| sigma_oracle approves without reading critic findings | 1 occurrence | Alert (meta-discriminator failure) |

### 15.2 The Human as Meta-Discriminator

sigma_oracle remains essential even with automated adversarial rounds. The adversarial system
can itself fail (both agents converge on a shared blind spot). The human detects meta-level
failures that no amount of automated adversarial rounds can catch.

This is why `allow_agent_sigma: false` is LOCKED in v17.

### 15.3 Context Window as Shared Weight Space

```
Session-scoped:  Context Window  <-->  GAN weights during one training run
Persistent:      Knowledge Graph  <-->  GAN weights saved to checkpoint

AdversarialRound findings --> KG:AptFeedback nodes
  = saving validated knowledge (like checkpoint saving)

Next session loads KG findings --> context
  = loading pretrained weights for continued training
```

---

## 16. Auto Mode (Restricted in v17)

Auto Mode is available but with MANDATORY adversarial gates at every transition.
sigma_oracle is STILL HUMAN even in auto mode -- the agent handles KAL, decomposition,
and ground truth automatically, but BLOCKS at each sigma_oracle checkpoint.

### 16.1 Auto Mode Algorithm (v17 Modified)

```
ALGORITHM AutoMode_v17(project_name, description):
  // PH1-PH2: SA
  INVOKE /apt-sa with {project_name, description}
  WAIT for SA + RootSpan creation

  // PH3-PH6: Loop until all spans materialized
  WHILE true:
    unfinished = QUERY all non-materialized AtomicSpans
    IF unfinished is empty: BREAK

    FOR EACH span IN unfinished (parallel, max 4):
      phase = detect_phase(span)

      IF phase = 'PH3':
        // v17: Density check FIRST
        density = DensityCheck(span)
        IF NOT density.pass: AUTO_KAL(span)  // automatic
        // Decompose
        INVOKE /apt-sp with {span}
        // v17: Adversarial round (automatic)
        critic = AdversarialRound(decomposition, "C_S_sigma")
        // v17: BLOCK for human sigma_oracle
        PRESENT {proposal, critic.findings, ground_truth} to HUMAN
        WAIT for HUMAN response  // CANNOT SKIP

      ELIF phase = 'PH4':
        INVOKE /apt-st with {span}
        // v17: Adversarial round
        critic = AdversarialRound(contract, "RefinementGate")
        PRESENT to HUMAN
        WAIT for HUMAN response

      ELIF phase = 'PH5':
        INVOKE /apt-scw with {span}
        // v17: Ground truth FIRST
        RUN cargo test -- MUST PASS
        // v17: Adversarial round
        critic = AdversarialRound(code, "FulfillmentGate")
        PRESENT to HUMAN
        WAIT for HUMAN response

      ELIF phase = 'PH6':
        feedback = get_feedback(span)
        IF feedback.returns < max_returns_per_span:
          route_feedback(feedback)
        ELSE:
          PAUSE "Max returns reached. Human review needed."

    // Validate after each round
    violations = RUN V1-V6 + V28 + V29
    IF violations > 0: PAUSE "Violation detected."

  // Final validation
  RUN V1-V29 (full health check)
  RETURN "All spans materialized. Project complete."
```

### 16.2 When to Use Auto Mode

| Scenario | Auto Mode? | Why |
|----------|:----------:|-----|
| Simple project (CRUD, CLI) | Maybe | Human sigma still required at every gate |
| Tutorial / Hello World | Maybe | Lower risk but gates still enforced |
| Complex domain project | No | Manual control recommended |
| Production-critical | No | Full manual mode essential |

### 16.3 Guardrails

- V1-V6 + V28 + V29 axiom checks after every round
- max_returns_per_span prevents infinite feedback loops
- sigma_auto still runs even in auto mode
- PAUSE on axiom violation -> human must resolve before continuing
- sigma_oracle is ALWAYS HUMAN even in auto mode (HR2)

---

## 17. Diffusion Analogy

| Diffusion | APT | Role |
|-----------|-----|------|
| prompt/conditioning | SA | Initial identity |
| noise -> coarse structure | SP | Abstract -> Span decomposition |
| coarse -> fine detail | ST | Span -> Contract specification |
| fine -> pixel-level | SCW | Contract -> Code (TDD) |
| U-Net | /apt orchestrator | Drives the denoising loop |
| denoising step | Phase transition | Each step reduces ambiguity |
| discriminator | adversarial-critic | Validates each denoising step (v17) |

---

## 18. GAN-Context Analogy (D24 -- Theoretical Foundation)

### 18.1 The Mapping

| GAN Concept | Agent Analog | Key Difference |
|------------|-------------|----------------|
| Generator | Design Agent | Produces code/architecture |
| Discriminator | Critic Agent | Evaluates quality |
| Weight space | Context Window + KG | Ephemeral + persistent |
| Training iteration | Adversarial round (D20) | 2-3 rounds vs thousands |
| Loss function | Ground truth: compiler, tests (D23) | Binary pass/fail |
| Mode collapse | Rushing through gates, self-approving | Detected by human |
| Overfitting | Confirmation bias / echo chamber | Fix: model separation (D22) |
| Gradient backprop | Context filling with critique text | Discrete chunks vs continuous |
| Nash equilibrium | Consensus or human decision | sigma_oracle breaks tie |
| Regularization | Anti-rubber-stamp techniques (D22.4) | Structural constraints |

### 18.2 KG as Persistent Weight Space

Adversarial round outcomes are recorded in KG (AptDecisionLog, AptFeedback nodes).
Next session loads relevant KG context = loading pretrained weights for continued training.

---

## 19. Mold Flow Diagram

```
Governance Mold -STARTS_WITH-> Intent Mold -NEXT-> Boundary Mold -NEXT-> Execution Mold -NEXT-> Assurance Mold
     |                |              |              |              |
     | Hook Engine     | Span Planner | Contract Reg | Work Queue   | Eval Harness
     | Agent Profile   | Req Graph    | Twin Registry| Subagent Rtr | Adversarial Gate (v17)
     |                |              |              | Runtime Trace|
     |                |              |              |              |
     +--- /apt -------+-- /apt-sp ---+-- /apt-st --+-- /apt-scw --+

     Memory Mold -CROSS_CUTS-> (all phases)
     | Memory Tier Manager / Reflection Memory / Checkpoint Ledger

     Adversarial Layer (v17) -CROSS_CUTS-> (SP, ST, SCW gates)
     | Critic Agent / Ground Truth / KG Logging / Anti-Bypass
```

---

## 20. Quick Reference -- Decision Tree

```
"I need to..."
    |
    +-- "...start a new project"
    |       -> /apt-sa (create SemanticAnchor, bootstrap context)
    |
    +-- "...break down a feature"
    |       -> /apt-sp (density check -> decompose -> adversarial -> sigma_oracle)
    |
    +-- "...write a contract/spec"
    |       -> /apt-st (crystallize -> adversarial -> sigma_oracle)
    |
    +-- "...implement code"
    |       -> /apt-scw (TDD -> cargo test -> adversarial -> sigma_oracle)
    |
    +-- "...check APT compliance"
    |       -> /apt (run V1-V29 including V28/V29 adversarial checks)
    |
    +-- "...find what phase I'm in"
    |       -> /apt (phase detection query, Section 2)
    |
    +-- "...report a problem"
    |       -> /apt (feedback system, Section 14)
    |
    +-- "...see adversarial history"
    |       -> /apt (decision audit trail query, Section 8.5)
    |
    +-- "...override a gate"
    |       -> HUMAN must provide reason. Logged as AptDecisionLog (Section 8.3)
    |
    +-- "...understand the methodology"
    |       -> Read references/apt_core.md
    |
    +-- "...check infrastructure setup"
    |       -> Read references/apt_infra.md
    |
    +-- "...see validation details"
            -> Read references/apt_reference.md
```

---

## 21. When to Use Each Skill

| Situation | Skill | Why |
|-----------|-------|-----|
| New project / no SA | `/apt-sa` | Bootstrap identity first |
| "Implement feature X" (unknown phase) | `/apt` -> detect phase -> delegate | Don't assume phase |
| "Plan the architecture for Y" | `/apt-sp` directly | Clearly SP work |
| "Write the contract for Z" | `/apt-st` directly | Clearly ST work |
| "Code the function for W" | `/apt-scw` directly | Clearly SCW work |
| "Check APT compliance" | `/apt` validation | Run V1-V29 |
| "Where does this feature go?" | `/apt` + KG query | Phase detection |
| "Audit the KG" | `/apt` validation | Full health check |
| "What phase am I in?" | `/apt` phase detection | Per-branch detection |
| "Review adversarial history" | `/apt` + Section 8.5 query | Decision audit trail |

---

## 22. Core Concepts Summary

### 22.1 Axioms (violation = not APT)

- **A1: ContractOnlyAtST** -- Contracts owned only by SemanticTwin
- **A2: RecursiveDecomposition + Termination** -- min 2 children, all paths end at AtomicSpan
- **A3: SiblingIndependence** -- no DEPENDS_ON between siblings
- **A4: CrystallizationFrontierUniqueness** -- CRYSTALLIZES_TO is the sole SP->ST bridge

### 22.2 Key Design Principles (D1-D24)

| Principle | Description |
|-----------|-------------|
| D1 | HyperedgeHub -- CrystallizationEvent as bipartite incidence hub |
| D3 | TaskAsScaffolding -- Task (NL) != Contract (formal spec) |
| D4 | DenseBeforeContract -- links(S) >= 5 before crystallization |
| D5 | SingleFileProjection -- AtomicSpan -> 1 file <= 500 lines |
| D9 | GenerativeFlowOrdering -- SA->SP->ST->SCW forward; reverse for Bottom-Up Ascent |
| D10 | NFR as First-Class -- latency, memory, accuracy in Contract nfr_* fields |
| D11 | KnowledgeAcquisitionLoop -- auto-search KG + web before decomposition |
| D12 | ParallelExecution -- sibling parallel, parent-child sequential |
| D14 | OneTypeOneNode -- one SharedType = one KG node |
| D15 | ParentDefinesInterfaceTypes -- parent defines boundary types before children ST |
| D16 | SequencingFromSharedType -- SEQUENCED_WITH auto-derived from types |
| D17 | SA as Index -- SA connected to everything, retroactive OK |
| **D20** | **AdversarialValidation -- every gate includes adversarial round** |
| **D21** | **FoundationalDensityPrinciple -- source diversity + foundation:composite ratio** |
| **D22** | **AdversarialCriticAgent -- model separation + anti-rubber-stamp** |
| **D23** | **GroundTruthPrimacy -- compiler > agent > intuition for facts** |
| **D24** | **GAN-ContextAnalogy -- theoretical foundation for adversarial layer** |

### 22.3 Crystallization Predicate C(S)

C(S) = v AND tau AND iota AND delta AND sigma (ALL must pass, cheap rejection first)

### 22.4 KG Reference Convention

All code files MUST include:
```
# KG: TASK_xxx -- links to SemanticTask node
# KG: CT_xxx -- links to AptContract node
```

---

## 23. Approval Gates Table (v17)

| Gate | Who | SLA | On Timeout |
|------|-----|-----|------------|
| sigma_auto (v,tau,iota,delta) | automated | instant | N/A |
| sigma_oracle | **HUMAN (LOCKED)** | 0 (immediate) | BLOCK -- re-ask |
| Adversarial Critic | automated (sonnet) | <= 60s per round | ESCALATE -- critic timeout = gate blocked |
| Ground truth (compiler/test) | automated | <= 300s | BLOCK -- ground truth must complete |
| DensityCheck | automated | <= 30s | BLOCK -- KAL must complete |

---

## 24. Events (v17)

| Event | Payload | When |
|-------|---------|------|
| SpanDecomposed | `{span, children, executor}` | After SP decomposition |
| CrystallizationCompleted | `{atom, twin, contract, hub}` | After ST crystallization |
| FulfillmentCompleted | `{contract, source, tests}` | After SCW implementation |
| FeedbackCreated | `{feedback, category, severity}` | When feedback recorded |
| **AdversarialRoundCompleted** | `{gate, span, critic_model, findings_count, blockers, verdict, ground_truth_pass}` | After each adversarial round |
| **GroundTruthOverride** | `{finding_id, gate, original_severity, ground_truth_result, action}` | When ground truth contradicts/confirms critic |
| **GateDecisionLogged** | `{decision_log_id, gate_type, decision, decided_by}` | After every gate decision logged to KG |

---

## 25. Clarifications (v17)

| # | Clarification |
|---|--------------|
| C36 | Adversarial rounds are not code review. They challenge assumptions and completeness. Both may occur. |
| C37 | Ground truth primacy does NOT apply to design decisions. sigma_oracle is supreme for design. |
| C38 | The critic agent is not an enemy. Adversarial = structured opposition, not hostility. |
| C39 | Lite Mode uses self-critique with full D22.3 template. Weaker but still required. |
| C40 | Foundation:composite ratio is per-Span, not per-KG. |
| **C41** | **v17: allow_agent_sigma: false is LOCKED. No configuration can change this. Agent cannot self-approve.** |
| **C42** | **v17: Every gate transition creates an AptDecisionLog node. No silent transitions allowed.** |
| **C43** | **v17: If adversarial critic returns < 3 findings, it is re-run with escalated prompt before proceeding.** |
| **C44** | **v17: Override of any HARD RULE requires explicit human reason logged in KG. Agent cannot generate the reason.** |

---

## 26. Project-Specific Invariants

Each SemanticAnchor may define domain invariants:
```cypher
MATCH (sa:SemanticAnchor {name: $project})-[:HAS_INVARIANT]->(inv)
RETURN inv.name, inv.description, inv.check_query
```

---

## 27. Reference Files

| File | Content | When to Read |
|------|---------|-------------|
| `references/apt_core.md` | SS1-SS9: Sets, Functions, Predicates, Relations, Axioms, Dual Guidance, Design Principles, KAL Config | Understanding foundations |
| `references/apt_infra.md` | SS23-SS30: Kafka Events, KG-Git Sync, MERGE-Only, Indexes, HA, Observability, Incident Response, CI/CD | Infrastructure setup |
| `references/apt_reference.md` | SS31-SS40: V1-V17 Queries, Traceability, Gap Resolution, Theory, Errors, Anti-Patterns, Feedback, Tutorials | Validation details |

---

## 28. Theoretical Foundations

| Domain | APT Element |
|--------|-------------|
| Dynamic Programming | SP decomposition (independent subproblems, memoization) |
| P-Coalgebra | DECOMPOSES_TO (branching with termination) |
| Hoare Logic | Contract as {P}f{Q} analogy, SEQUENCED_WITH |
| Extended Mind | KG as external cognition (Clark & Chalmers 1998) |
| Thompson Sampling | Gap Resolution (70% exploitation, 30% exploration) |
| DDD | Bounded contexts, ubiquitous language |
| CSP | Agent -> Kafka -> KG (no shared state) |
| Kuhn / Godel | Version evolution, sigma_oracle irreducibility |
| Wolfram Hypergraph | Bipartite incidence, EXPLORES_VIA, confluence |
| **GAN Theory** | **Adversarial validation, mode collapse detection, regularization (v17)** |

---

## 29. Version History

| Ver | Key Change |
|-----|-----------|
| v14 | Harness techniques executable, eval-optimizer, hook engine |
| v15 | Adversarial Validation Layer (D20-D24), FulfillmentGate 13/13, V27-V29 |
| v16 | Skill file consolidation, Auto Mode, Mold Flow, full orchestrator |
| **v17** | **MANDATORY adversarial enforcement. allow_agent_sigma: false LOCKED. Every gate: adversarial + ground truth + HUMAN sigma_oracle. Anti-bypass mechanisms. KG logging for all decisions. Stronger re-attack prompts. Mode collapse detection. 29 validations. Cannot be bypassed.** |

---

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

# apt — Validation

> **Lazy-load reference for `apt` skill.**
> Loaded *only when* the orchestrator enters the relevant phase/gate.
> Parent skill: [`../SKILL.md`](../SKILL.md). Repo CHANGELOG: [`../../CHANGELOG.md`](../../CHANGELOG.md).
> Refactor source: PROM 16 F6.1 Progressive Disclosure (2026-04-29).
> KG: `lesson-prom16-skillver-progressive-disclosure-drift-2026-04-29`.

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

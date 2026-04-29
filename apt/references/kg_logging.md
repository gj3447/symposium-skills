# apt — Kg Logging

> **Lazy-load reference for `apt` skill.**
> Loaded *only when* the orchestrator enters the relevant phase/gate.
> Parent skill: [`../SKILL.md`](../SKILL.md). Repo CHANGELOG: [`../../CHANGELOG.md`](../../CHANGELOG.md).
> Refactor source: PROM 16 F6.1 Progressive Disclosure (2026-04-29).
> KG: `lesson-prom16-skillver-progressive-disclosure-drift-2026-04-29`.

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

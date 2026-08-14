# Naesengmoon receipt persistence

Despite the historical filename, normal validation does not write the KG.

```yaml
receipt_id: stable local identifier
target: exact revision or claim
decision: APPROVE | CONDITIONAL | BLOCK | INCONCLUSIVE
criteria_checked: []
findings: []
supported_blockers: []
supported_dissent: []
coverage_gaps: []
independence: explicit executor/reviewer relationship
provenance: commands, paths, sources, actor, and date
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

Only material reusable evidence may be proposed as `PENDING`. Do not create or mutate a ValidationResult,
Lesson, MCTS record, status, confidence, configuration, contract, canon, or seed. A separately authorized
ratifier/writer must name the pending ID, allowed fields, prior values, and exact readback.

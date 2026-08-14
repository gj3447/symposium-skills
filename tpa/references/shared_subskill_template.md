# TPA subskill output template

```yaml
phase: TCW | ST | SP | TA
target_revision: string
inputs: []
outputs: []
evidence: []
checks: []
coverage:
  denominator: explicit scope
  observed: []
  exclusions: []
blockers: []
unknowns: []
followups: []
status: COMPLETE | PARTIAL | RETURN | BLOCKED | INCONCLUSIVE
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

This is a local receipt. It does not create a ValidationResult, Lesson, ActionPlan, seed, status change, or
canonical mutation. Counts report coverage only.

# Jaebaeman manifest and persistence

Despite the historical filename, orchestration does not require a KG write.

```yaml
cycle_id: stable local identifier
tasks:
  - task_id: string
    objective: string
    permissions: read_only | explicit_write
    status: COMPLETE | PARTIAL | BLOCKED | FAILED | CANCELLED
    evidence: []
    changes: []
    uncertainty: []
evidence_lineage: []
conflicts: []
integration_decision: string
followups: []
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

Only repeated, high-risk, cross-repository, or reusable results may be proposed as `PENDING`. Do not
create or mutate TaskSpec seeds, statuses, ValidationResults, ResearchFindings, ActionPlans, Lessons,
configuration, canon, or supersession. Ratification is external and requires exact readback.

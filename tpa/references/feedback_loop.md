# TPA feedback classification

TPA findings normally remain in the local recovery bundle.

## Classification

- `LOCAL_OBSERVATION`: ordinary gap, drift, ambiguity, or recovery note.
- `PENDING_VERDICT`: repeated/high-risk/cross-repository issue whose cause is unresolved.
- `PENDING_ROOT_CAUSE`: evidence isolates the cause.
- `PENDING_LESSON`: evidence establishes both cause and reusable prevention.
- `PENDING_CANON_CHANGE`: specific anchor/binding/status proposal awaiting authority.

Do not skip directly from a count or repeated label to RootCause/Lesson. Repetition changes persistence
priority, not causal truth.

## Pending proposal

```yaml
pending_id: proposed identifier
target: exact code/design artifact and revision
finding_ids: []
proposed_type: VERDICT | ROOT_CAUSE | LESSON | CANON_CHANGE
root_cause: required only when evidenced
reusable_prevention: required only for Lesson
proposed_fields: exact field-level changes, if any
provenance: actor, date, commands, paths, and commits
status: PENDING
ratifier_required: explicit authority
```

Independent review/reproduction adds evidence but does not self-ratify. No automatic ActionPlan, status,
confidence, supersession, research, sibling, or recursion follows from this classification.

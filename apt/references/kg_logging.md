# APT — evidence receipts and persistence boundary

This reference defines how an APT cycle records evidence without turning every transition into knowledge
graph ceremony. The parent skill is [`../SKILL.md`](../SKILL.md).

## Default rule

Keep ordinary gate decisions, findings, tests, and overrides in the local cycle artifact or parent
handoff. Do not create a KG node for every finding or transition. Counts are telemetry, never votes for
truth, priority, confidence, or ratification.

Durable persistence is considered only for evidence that is repeated, high-risk, cross-repository, or
reusable across sessions. Such evidence is proposed as `PENDING`; it does not directly mutate canon,
status, confidence, configuration, a Span, a Contract, or a Lesson.

## Local decision receipt

Record a receipt when a gate materially changes execution:

```yaml
receipt_id: stable local identifier
cycle_id: parent cycle
target: exact artifact, Span, or contract under review
gate: gate name
decision: PASS | RETURN | ESCALATE | BLOCK | OVERRIDE | INCONCLUSIVE
actor: executor or reviewer identity
observed_at: timestamp
inputs:
  command: optional exact command
  environment: relevant versions or commit
  artifacts: paths or external identifiers
evidence:
  supporting: []
  contradicting: []
  unknowns: []
independence: executor_same_as_reviewer | independent_reviewer | not_applicable
reason: concise evidence-based rationale
followups: bounded candidates
```

An override additionally records who authorized it, the exact boundary waived, duration, and rollback or
review condition. Human approval is not inferred from silence.

## Local finding receipt

```yaml
finding_id: stable local identifier
cycle_id: parent cycle
target: exact claim or artifact
category: correctness | evidence | security | performance | operations | method | other
severity: blocker | high | medium | low | note
claim: one falsifiable statement
observation: what was actually observed
provenance: path, command, URL, dataset, commit, and date as applicable
relation: SUPPORTS | CONTRADICTS | INCONCLUSIVE | NOT_APPLICABLE
dependence: independent | shared_input | derivative | unknown
reproduction: not_run | reproduced | failed_to_reproduce | not_applicable
limitations: []
suggested_action: optional bounded proposal
```

Preserve evidence-backed dissent. Do not merge contradictory findings into a synthetic consensus score.

## Pending evidence proposal

Use only when the persistence threshold is met:

```yaml
pending_id: proposed stable identifier
proposal_type: EVIDENCE | VERDICT | ROOT_CAUSE | LESSON | POLICY_CHANGE
target: exact claim, artifact, or policy
target_fiber: algebra | physics | engineering | narrative | operations
source_receipts: []
proposed_change: specific field-level change, or NONE
reason_reusable: recurrence, risk, or cross-repository value
root_cause: required only when evidenced
reusable_prevention: required only for a Lesson proposal
provenance: actor, timestamp, commit, paths, and source identifiers
status: PENDING
ratifier_required: explicit authority or user decision
```

A recurrence threshold may justify `PENDING_VERDICT`; it does not establish a `RootCause`. A Lesson
proposal requires both evidenced cause and reusable prevention. Do not invent `truth`, a mechanism, or a
Lakatos label to fill a schema.

## Ratification request and receipt

Ordinary APT execution cannot self-ratify. A ratification request must name:

```yaml
pending_id: existing pending proposal
ratifier: explicitly authorized person or role
allowed_fields: exact fields that may change
previous_values: exact current values
proposed_values: exact requested values
evidence_reviewed: source receipt ids
```

The authorized writer performs a bounded mutation, then returns an exact readback receipt containing the
pending ID, actor, timestamp, changed fields, before/after values, and external record identifier. If any
precondition is missing, retain `PENDING` and report the blocker.

Independent reproduction adds evidence; it is not ratification. Majority, unanimity, critic count, or a
producer's own success return is not ratification.

## Scientific evidence

When an APT cycle materially affects a scientific claim, apply the highest applicable T0/T1/T2 tier
before execution. T2 receipts identify the target claim and algebra/physics fiber and keep these axes
independent:

- relation: `SUPPORTS | CONTRADICTS | INCONCLUSIVE`;
- novelty: `REPRODUCTION | DISCOVERY_CANDIDATE`;
- fitting risk: `NULL_PASS | NUMEROLOGY_HOLD | NOT_APPLICABLE | NOT_ASSESSED`.

Null/multiplicity checks apply only when a valid null exists. Numerical Bayes and Lakatos assessments
remain behind their canonical gates; do not add them merely to satisfy a logging template.

## Retention and deduplication

- Keep exact commands, versions, commits, and source dates near the observation.
- Link derivative findings to their shared source so reruns are not double-counted.
- Prefer one pending proposal referencing several receipts over duplicate proposals.
- Redact secrets and personal data before any durable persistence.
- Keep local receipts append-only when they are an audit trail; correct them with a superseding receipt.

This follows W3C PROV's useful separation of entity, activity, and agent without requiring a graph write.

## Definition of done

- Material decisions have local provenance-bearing receipts.
- Ordinary events stayed local.
- Durable candidates are `PENDING`, deduplicated, and scoped to an exact target.
- Canonical changes have separate authority and exact readback.
- No count-vote, automatic Lesson creation, or automatic recursive follow-up occurred.

Legacy mandatory Cypher and every-transition KG logging remain in Git history. They are not active APT
instructions.

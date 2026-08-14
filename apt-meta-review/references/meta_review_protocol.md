# APT MetaReview protocol

The authoritative workflow is [`../SKILL.md`](../SKILL.md).

## 1. Receive a bounded cycle record

Require the cycle ID, exact target, reviewed diff, observed tests/verdicts, completion state, write
authority, and validation budget. Missing causal evidence yields `INCONCLUSIVE` or `CAUSE_UNKNOWN`.

## 2. Separate symptom, cause, and prevention

- A symptom is an observed mismatch.
- A root cause requires evidence isolating why it occurred.
- A reusable prevention requires evidence that the proposed guard addresses that cause.

Recurrence or severity raises persistence priority but does not prove a cause.

## 3. Choose one bounded outcome

- `LOCAL_REPORT` for ordinary cycle learning;
- `PENDING_VERDICT` for material unresolved recurrence/risk;
- `PENDING_LESSON` only with evidenced cause and prevention;
- `PATCH_PROPOSAL` for a specific method change.

## 4. Patch only with authority

When the current task and writer boundary authorize it, make the smallest change and run directly relevant
checks. Otherwise return a proposal. Never update KG/canon/config/status/materialization as a side effect.

## 5. Stop

Return the local report or qualified pending proposal. An independent material review may be requested,
but MetaReview never invokes itself or creates an automatic descendant cycle.

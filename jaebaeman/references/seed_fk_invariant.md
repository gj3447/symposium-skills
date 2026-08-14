# TaskSpec atomicity invariant

The historical “seed” terminology now means a local TaskSpec only. It does not require a persistent KG
node or lifecycle status.

## Invariant

One TaskSpec maps to one bounded deliverable and one integration owner. A larger Span may have several
TaskSpecs only when their scopes are independent and their outputs can be integrated explicitly. Several
agents may examine the same target for different adversarial concerns, but their reports are not duplicate
owners and are never votes.

## Required local identifiers

- `task_id`: unique within the parent cycle;
- `source_id`: exact parent artifact, claim, or Span identifier;
- `objective`: single deliverable;
- `integration_owner`: parent;
- `permissions`: read-only or exact write-set;
- `status`: local collection status only.

## Checks

- no orphan TaskSpec without `source_id`;
- no duplicate `task_id` in one cycle;
- no overlapping explicit write-set across active tasks;
- no task whose completion depends on an undispatched hidden child;
- no automatic persistence, status transition, archival, or sibling creation.

Legacy persistent seed/FK Cypher remains in Git history and is not active protocol.

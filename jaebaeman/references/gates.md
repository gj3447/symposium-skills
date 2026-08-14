# Jaebaeman gates

## Task gate

Each task has one objective, exact scope/non-goals, inputs, permissions, output contract, completion
condition, and bounded failure policy.

## Independence gate

Parallel tasks can make useful progress without waiting on one another and do not contend for the same
write target. Otherwise keep them sequential or under one owner.

## Authority gate

Read-only is the default. Explicit writes require parent authority and an exact disjoint write-set.

## Dispatch gate

The actual runtime tool schema, concurrency cap, timeout, cancellation owner, and retry limit are known.

## Collection gate

Results match the output contract and include evidence, changes, checks, and uncertainty. Partial or
missing output is never reported as complete.

## Integration gate

Evidence lineage and conflict are preserved. Counts do not determine truth or priority.

## Persistence gate

The manifest is local unless a result meets the qualified `PENDING` threshold. Canonical mutation is a
separate authorized operation.

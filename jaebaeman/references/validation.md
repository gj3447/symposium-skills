# Jaebaeman validation checklist

- [ ] Every task has a unique ID, one objective, exact scope, and completion condition.
- [ ] Dependencies form a finite acyclic plan.
- [ ] Concurrency, timeout, cancellation, and retries are bounded.
- [ ] Read-only is default; explicit write-sets are disjoint and authorized.
- [ ] Tool calls use the current runtime schema.
- [ ] Every collected result matches the output contract.
- [ ] Partial, failed, blocked, and cancelled work remains visible.
- [ ] Shared evidence and contradictory results are preserved.
- [ ] Integration uses evidence rather than task count.
- [ ] The manifest stayed local or became only a qualified `PENDING` proposal.
- [ ] No automatic sibling, recursion, status mutation, or canonical write occurred.

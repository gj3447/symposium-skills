# Prometheus evidence persistence

Despite this historical filename, this is not an automatic KG-write procedure.

The default research packet is local and contains finding IDs, exact provenance, evidence lineage,
limitations, contradictions, and decision impact. A result may be proposed as `PENDING` only when it is
repeated, high-risk, cross-repository, or reusable.

```yaml
pending_id: proposed identifier
target: exact claim or artifact
target_fiber: algebra | physics | engineering | narrative | operations
finding_ids: []
proposed_change: specific field-level change, or NONE
reason_reusable: string
status: PENDING
ratifier_required: explicit authority
```

Do not emit mutating Cypher from a research cycle. Independent reproduction adds evidence but does not
self-ratify. Canon, status, confidence, configuration, seed, ActionPlan, Lesson, and supersession changes
require an identified pending record plus a separately authorized ratifier/writer and exact readback.

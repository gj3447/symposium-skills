---
name: apt-orchestrator
kg_ref: ATOM_Skill_apt_orchestrator
version: "2.0.0"
channel: stable
canonical_name: apt-orchestrator
description: >-
  Route bounded APT phase work from actual artifact state, resolve optional method capabilities read-only, and return explicit local phase handoffs without automatic re-entry or persistence. Use when: the parent `$apt` workflow needs internal phase routing, dispatch planning, or capability lookup. Do not use when: a user wants the complete APT entry point rather than internal phase coordination; use `$apt` instead.
---

# APT internal orchestrator

The parent `$apt` skill owns the cycle. This internal router identifies the smallest next phase and any
conditional supporting method. It never creates phase nodes, seeds, Lessons, ActionPlans, or status changes.

## Layer boundary

Declare the exact repository and artifact layer before routing. Paper/canon evidence, implementation code,
and external runtime state are different layers. Use absolute or repository-relative resolved paths and
do not infer authority across repositories.

## Read-only capability resolution

When a methodology registry or KG is available, read current capability names and invocations. Treat the
result as routing metadata. Missing or stale registry data becomes a local warning, not permission to edit
the slot, bootstrap nodes, or silently substitute a method.

## Routing

```text
intent not framed        -> SA
cohesive spans missing   -> SP
contract missing         -> ST
approved contract        -> SCW
passing implementation   -> proportional Cleanup
reusable method impact   -> optional MetaReview
```

Branches route independently from their own artifacts. Do not globally advance a project or reopen an
earlier phase because a discovery appeared elsewhere.

## Conditional supporting methods

- missing decision-critical evidence -> propose `$prometheus`;
- independent bounded work -> propose `$jaebaeman`;
- material formal review -> propose `$taliban`;
- code-to-claim traceability -> propose `$longinus`;
- bounded runtime loop -> propose `$harness`;
- evidenced reusable method issue -> propose `$apt-meta-review`.

Invoke only when the current decision needs it or the user explicitly requests it. Each child has its own
scope, permissions, budget, completion condition, and local receipt.

## Handoff

```yaml
cycle_id: string
target: exact artifact/revision
detected_phase: SA | SP | ST | SCW | CLEANUP | META_REVIEW
evidence: []
missing_inputs: []
next_task: bounded objective
supporting_method: optional name and reason
permissions: exact read/write boundary
stop_condition: observable condition
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

Ordinary phase handoffs stay local. Material reusable evidence may be proposed as `PENDING`; separate
authorized ratification is required for KG/canon/config/status/confidence changes.

## Stop rule

Return after one routing/dispatch boundary is resolved. Re-entry is a separate invocation when a blocker
or explicit user request requires it. Counts are telemetry, never a routing vote.

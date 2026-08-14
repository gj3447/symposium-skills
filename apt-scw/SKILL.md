---
name: apt-scw
kg_ref: ATOM_Skill_apt_scw
version: "28.0.0"
channel: stable
description: >-
  Implement approved APT contracts through the smallest RED→GREEN→REFACTOR slices, explicit dependency waves, directly relevant checks, scoped Effect boundaries when TypeScript is used, and a local fulfillment receipt. Use when: the parent `$apt` workflow dispatches SCW after a sufficient ST contract. Do not use when: the task still lacks crystallized contracts or material design decisions; use `$apt-st` instead.
---

# APT SCW — contract implementation

## Preconditions

Require the exact contract/revision, repository rules, current writer authority, explicit write-set,
dependency plan, and completion condition. Preserve foreign dirty state.

## Functional TypeScript / Effect boundary

When the implementation is TypeScript with Effect:

- deterministic decisions and transforms are pure functions over immutable values;
- external I/O, typed failures, services, concurrency, resources, schedules, and observability live in
  lazy Effect values behind narrow ports;
- unknown input is decoded with the installed version's Schema API;
- Layers are assembled once at the production composition root;
- files, processes, clients, and fibers have scoped ownership and interruption-safe cleanup;
- retries, waits, queues, and concurrency are explicitly bounded;
- tests replace ports with compatible Layers and cover negative/cleanup behavior.

Do not install, upgrade, or mix Effect majors unless the task explicitly authorizes a migration.

## Slice loop

1. **RED**: add or identify an observable failing contract check.
2. **GREEN**: implement the smallest behavior that satisfies the check.
3. **REFACTOR**: simplify while keeping all relevant checks green.
4. Record exact commands, outputs, changed files, and remaining uncertainty.

Independent dependency waves may run concurrently only with disjoint write-sets and parent-managed bounds.
Later waves wait for prerequisite evidence. Partial failure is explicit; no automatic retry/sibling occurs.

## Fulfillment receipt

```yaml
contract_id: string
target_revision: string
changes: []
red_evidence: []
green_evidence: []
refactor_evidence: []
checks: []
external_readbacks: []
blockers_and_unknowns: []
decision: FULFILLED | PARTIAL | RETURN | BLOCKED | INCONCLUSIVE
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

Run directly relevant typecheck/tests/builds and broader checks in proportion to risk. A formal independent
review or Longinus binding audit is conditional on material risk/policy, not automatic. The phase does not
write Contract/Task/KG/status/materialization, inject mandatory KG comments, create a Lesson/ActionPlan/
seed, or recursively reopen design. Historical references are inactive unless explicitly requalified.

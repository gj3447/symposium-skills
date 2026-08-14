---
name: apt-st
kg_ref: ATOM_Skill_apt_st
version: "28.0.0"
channel: stable
description: >-
  Crystallize contract-ready APT spans into typed local contracts and implementation tasks with exhaustive material decisions, explicit failures, evidence criteria, and reference proposals before code. Use when: the parent `$apt` workflow dispatches ST after SP reaches a sufficient frontier. Do not use when: design recovery starts from existing code rather than forward spans; use `$tpa` instead.
---

# APT ST — contract crystallization

## Contract

```yaml
contract_id: stable local identifier
span_id: exact source span/revision
purpose: bounded behavior
inputs: typed and validated boundary values
outputs: typed success values
preconditions: []
postconditions: []
invariants: []
expected_failures: typed variants
side_effects_and_resources: explicit ports/lifetimes
concurrency_and_idempotency: when applicable
examples_and_counterexamples: []
acceptance_evidence: tests, proofs, builds, or readbacks
open_decisions: only material unresolved choices
```

For TypeScript/Effect work, distinguish pure immutable domain transforms from services and adapters; keep
expected failure in the error channel, dependencies in the requirement channel, resources in Scope,
unknown inputs behind version-matched Schema, and runtime/Layer assembly at one composition root.

## Task plan

Derive the smallest implementation tasks with exact dependencies, permissions, outputs, and checks. Task
size follows cohesion/risk rather than fixed lines or counts. Reference-site changes are proposals until the
owning writer implements and validates them.

## Gate

The contract is unambiguous enough to implement, decision areas with material impact are resolved or
blocked, and tests can distinguish success from failure. Return `READY`, `RETURN`, or `INCONCLUSIVE`.
Do not write Contract/SemanticTask/KG/status/config/materialization, spawn automatic critics, or create
Lessons/ActionPlans/seeds. Historical references are inactive unless explicitly requalified.

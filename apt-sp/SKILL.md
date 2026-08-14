---
name: apt-sp
kg_ref: ATOM_Skill_apt_sp
version: "28.0.0"
channel: stable
description: >-
  Decompose an approved APT SemanticAnchor into a finite dependency-aware set of cohesive, testable spans and expose the contract-ready frontier. Use when: the parent `$apt` workflow dispatches SP after sufficient SA framing. Do not use when: one bounded child-span draft is delegated from an existing brief or leaves are ready for contract crystallization; use `$design-agent` or `$apt-st` instead.
---

# APT SP — bounded decomposition

## Workflow

1. Load the exact SA artifact and target revision.
2. Identify responsibilities, change boundaries, data/control dependencies, and explicit non-goals.
3. Split only where units can be specified and validated independently.
4. Record a finite dependency DAG and detect cycles or shared ownership.
5. Stop when each leaf is cohesive, testable, owned, and contract-ready.

## Span record

```yaml
span_id: stable local identifier
objective: one responsibility
definition: bounded behavior or artifact
key_assertion: observable claim
inputs_and_outputs: []
dependencies: []
sibling_independence: evidence or explicit coupling
acceptance_criteria: []
verification: []
owner: integration owner
non_goals: []
provenance: parent anchor/revision
```

Line count, depth, child, and lens values are planning telemetry/configuration inputs, not proof of
atomicity. Infrastructure exceptions and shared types are explicit; they do not silently relax cohesion.

## Gate and stopping

Return a local frontier with `CONTRACT_READY`, `NEEDS_SPLIT`, `COUPLED`, or `INCONCLUSIVE` per leaf. One
supported dependency/collision can block a proposed split. Discovery is a bounded candidate, not automatic
recursion or research. No Span/KG/status/config write, seed, Lesson, ActionPlan, automatic critic, or next
phase occurs. Historical references are inactive unless explicitly requalified.

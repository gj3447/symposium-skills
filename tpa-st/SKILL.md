---
name: tpa-st
kg_ref: ATOM_Skill_tpa_st
version: "2.0.0"
channel: stable
provenance: AI_DERIVED_FROM_USER_PRIMARY
description: >-
  Recover explicit and conventional contracts, signatures, preconditions, postconditions, and failure behavior from an approved TPA code inventory with line-level evidence. Use when: the parent `$tpa` workflow dispatches ST after a sufficient TargetCodeWorld inventory. Do not use when: code inventory is incomplete or extracted contracts are ready for pattern recovery; use `$tpa-tcw` or `$tpa-sp` instead.
---

# TPA ST — contract recovery

## Workflow

1. Load the exact TCW inventory and target revision.
2. Classify contracts as `EXPLICIT` (interface/type/schema/assertion) or `CONVENTIONAL` (behavior inferred
   from implementation, callers, tests, or docs). Never silently promote convention to formal contract.
3. Extract inputs, outputs, side effects, preconditions, postconditions, invariants, errors, lifecycle, and
   concurrency assumptions.
4. Cite exact symbols/paths and list contradictory call sites or missing tests.
5. For large independent symbol groups, use bounded read-only parent-managed dispatch and integrate by
   evidence lineage.

## Contract record

```yaml
contract_id: stable local identifier
symbol: fully qualified symbol
kind: EXPLICIT | CONVENTIONAL | UNKNOWN
inputs: []
outputs: []
preconditions: []
postconditions: []
invariants: []
failures_and_effects: []
evidence: paths, symbols, tests, and observations
confidence_basis: direct | corroborated | inferred | conflicting
limitations: []
```

Completion means all in-scope public symbols are accounted for as recovered, excluded, or unknown; it does
not require a fixed coverage number or critic count. Giant/complex symbols are flagged for separate bounded
analysis, not automatic research. Findings stay local or qualified `PENDING`; no KG, status, seed, Lesson,
ActionPlan, or recursive dispatch mutation occurs.

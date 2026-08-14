---
name: tpa-sp
kg_ref: ATOM_Skill_tpa_sp
version: "2.0.0"
channel: stable
provenance: AI_DERIVED_FROM_USER_PRIMARY
description: >-
  Recover a TPA TargetPyramid from extracted contracts by testing architectural and design-pattern hypotheses, alternatives, and counterevidence with explicit confidence bases. Use when: the parent `$tpa` workflow dispatches SP after a sufficient TargetTwin. Do not use when: raw symbols still need contract extraction or recovered structure is ready for final anchoring; use `$tpa-st` or `$tpa-ta` instead.
---

# TPA SP — pattern and structure recovery

## Workflow

1. Freeze the ST contract set and target revision.
2. Group symbols by data/control flow, ownership, dependency direction, lifecycle, and change boundary.
3. For each candidate pattern, test required elements and record counterevidence and plausible alternatives.
4. Separate `SUPPORTED`, `PARTIAL`, `ALTERNATIVE`, `NOVEL_CANDIDATE`, and `INCONCLUSIVE`.
5. Verify distributed/concurrent properties with appropriate runtime, model, or mathematical evidence only
   when they matter; no preset verifier is automatic.

## Pattern record

```yaml
pattern_id: stable local identifier
name: known pattern or descriptive candidate
status: SUPPORTED | PARTIAL | ALTERNATIVE | NOVEL_CANDIDATE | INCONCLUSIVE
required_elements: []
observed_elements: []
counterevidence: []
alternatives: []
evidence: contracts, symbols, paths, commands, or traces
confidence_basis: why this classification follows
limitations: []
```

Confidence is evidence-based, not a fixed numeric threshold. Unknown or novel patterns become bounded
follow-up candidates; research starts only when blocking or user-requested. Counts are telemetry. No KG,
status, seed, Lesson, ActionPlan, automatic meta-verifier, critic, or recursive discovery occurs.

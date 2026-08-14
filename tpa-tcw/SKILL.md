---
name: tpa-tcw
kg_ref: ATOM_Skill_tpa_tcw
version: "2.0.0"
channel: stable
provenance: AI_DERIVED_FROM_USER_PRIMARY
description: >-
  Inventory external or legacy code into a local TPA TargetCodeWorld using parser or AST evidence, exact scope accounting, bounded optional partitioning, and an evidence-backed exit receipt. Use when: the parent `$tpa` workflow begins reverse engineering from an actual codebase. Do not use when: the target is forward design or an approved inventory already needs contract recovery; use `$apt` or `$tpa-st` instead.
---

# TPA TCW — code-world inventory

## Input

Freeze repository/path, revision, languages, generated/vendor/test inclusion, entry points, and output scope.
Default to read-only.

## Workflow

1. Enumerate files with repository-aware tools and record exclusions.
2. Detect languages/build manifests and choose version-matched parsers.
3. Extract modules, public symbols, signatures, imports/dependencies, entry points, and source locations.
4. Cross-check parser counts against file/manifests; grep may supplement but not replace semantic parsing.
5. Record unresolved parse failures and unknown external symbols.

For large independent partitions, the parent may use `$jaebaeman` with a local manifest, bounded
concurrency, explicit file lists, and read-only tasks. The parent recomputes coverage; disagreement triggers
a bounded check, not an automatic extra agent. Unknown-symbol research is a candidate unless blocking.

## Output

```yaml
target_revision: string
files: []
languages_and_parsers: []
symbols: []
dependencies: []
entry_points: []
exclusions: []
parse_failures: []
unknowns: []
coverage_basis: exact denominator and observations
status: COMPLETE | PARTIAL | BLOCKED | INCONCLUSIVE
```

Completion requires an exact denominator, evidence-bearing symbols, and visible gaps. Counts are coverage
telemetry. No KG write, status mutation, seed, Lesson, ActionPlan, automatic critic, or recursive research
occurs. Material reusable gaps may be returned only as `PENDING` proposals.

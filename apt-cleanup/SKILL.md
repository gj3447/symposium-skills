---
name: apt-cleanup
kg_ref: ATOM_Skill_apt_cleanup
version: "28.0.0"
channel: experimental
description: >-
  Run proportional APT package-level cleanup after passing implementation by measuring cohesion, dependency direction, cycles, duplication, dead code, and complexity, then applying only authorized behavior-preserving refactors. Use when: SCW or several cycles have accumulated structural debt or package-level drift. Do not use when: performing local refactoring inside the current RED→GREEN→REFACTOR slice; use `$apt-scw` instead.
---

# APT cleanup — behavior-preserving structural refinement

## Input

Require a passing baseline, exact target/revision, scope, writer authority, and relevant architecture rules.
Freeze metrics and exclusions before comparing.

## Diagnose

Inspect cohesion, dependency direction/cycles, duplication, large files/functions, dead code, public API
surface, and package boundaries with tools appropriate to the repository. Tool count and metric thresholds
are diagnostics, not verdict votes.

## Plan and apply

Propose the smallest refactors that remove demonstrated accidental structure. Apply only when authorized,
with rollback/recoverability for moves/deletions. Preserve public behavior and avoid mixing unrelated
features into cleanup.

For TypeScript/Effect code, preserve pure domain kernels, service contracts, Layer composition, Schema
boundaries, typed errors, and scoped resources. Do not move I/O into pure code or introduce scattered
runtime execution.

## Verify

Run the baseline checks plus directly affected static analysis and tests. Compare before/after metrics using
the frozen denominator and report regressions honestly.

```yaml
target_revision: string
baseline_checks: []
observations: []
changes: []
after_checks: []
metric_deltas: []
decision: CLEAN | IMPROVED | NEEDS_FOLLOWUP | BLOCKED | INCONCLUSIVE
followups: []
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

A cleanup failure remains local unless materially reusable. It does not auto-create a Lesson, KG node,
MetaReview, ActionPlan, status/config change, or recursive cycle. Historical references are inactive unless
explicitly requalified.

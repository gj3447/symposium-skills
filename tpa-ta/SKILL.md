---
name: tpa-ta
kg_ref: ATOM_Skill_tpa_ta
version: "2.0.0"
channel: stable
provenance: AI_DERIVED_FROM_USER_PRIMARY
description: >-
  Propose a new, reused, or branched SemanticAnchor for recovered TPA design, audit fixed-denominator drift classes, and prepare evidence-backed reference bindings without applying canonical mutations. Use when: the parent `$tpa` workflow dispatches TA after a sufficient TargetPyramid. Do not use when: reverse recovery has not completed pattern and structure analysis; use `$tpa-sp` instead.
---

# TPA TA — anchor proposal and drift audit

## Workflow

1. Load the exact TCW/ST/SP bundle and target revision.
2. Compare recovered intent/structure with candidate anchors using meaning, scope, ownership, provenance, and
   compatibility—not name similarity alone.
3. Choose `REUSE_PROPOSAL`, `BRANCH_PROPOSAL`, `NEW_PROPOSAL`, or `NO_ANCHOR` with reasons.
4. Prepare code-to-claim/reference bindings with exact symbols, paths, line/range identity, and revision.
5. Fix drift denominators/exclusions before measuring missing, orphan, signature, pattern, label, or other
   target-specific drift.

## Output

```yaml
anchor_decision: REUSE_PROPOSAL | BRANCH_PROPOSAL | NEW_PROPOSAL | NO_ANCHOR
target_revision: string
candidate_and_reason: string
binding_proposals: []
drift:
  denominator: exact scoped items
  exclusions: []
  observations: []
  severity_basis: evidence and impact
unknowns: []
status: COMPLETE | PARTIAL | BLOCKED | INCONCLUSIVE
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

This phase proposes but does not apply anchor, binding, status, confidence, `SUPERSEDES`, or archive
changes. A separately authorized ratifier/writer is required for canonical mutation and exact readback.
Drift counts are telemetry, not an automatic suspension or verdict. Formal review is conditional on risk;
no automatic critic, Lesson, seed, ActionPlan, or recursion occurs.

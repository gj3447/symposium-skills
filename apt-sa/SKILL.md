---
name: apt-sa
kg_ref: ATOM_Skill_apt_sa
version: "28.0.0"
channel: stable
description: >-
  Establish or recover a local APT SemanticAnchor with user intent, objective, scope, key assertion, constraints, provenance, and unresolved questions before decomposition. Use when: the parent `$apt` workflow starts a project or feature and dispatches SA framing. Do not use when: an anchor already exists and needs bounded decomposition; use `$apt-sp` instead.
---

# APT SA — semantic framing

## Input

Load user-primary intent, existing artifacts, exact target/revision, domain constraints, and current write
authority. KG/canon lookup is read-only. Do not create an anchor merely because none was found.

## Anchor artifact

```yaml
anchor_id: stable local identifier
objective: requested outcome
definition: what the project/feature is
key_assertion: central testable or design claim
actors_and_users: []
scope:
  included: []
  excluded: []
constraints: []
invariants: []
assumptions: []
primary_provenance: exact user/source references
interpretations: explicitly labeled AI inferences
open_questions: only material unresolved choices
completion_condition: observable downstream outcome
```

Fields are required when semantically applicable, not to satisfy a fixed count. Preserve user wording and
separate mythology/narrative, engineering, algebra, and physics layers when relevant.

## Gate

- target and ownership are exact;
- objective, scope, non-goals, assumptions, and provenance are visible;
- key assertions are testable or clearly labeled narrative/intent;
- unresolved choices that materially change design are not guessed;
- the anchor is small enough to guide decomposition without embedding implementation.

Return `COMPLETE`, `RETURN`, or `INCONCLUSIVE` with evidence. The artifact stays local unless qualified as
a material `PENDING` proposal. No KG/canon/status/config mutation, seed, Lesson, critic quota, or automatic
next phase occurs. Historical reference files are not active unless the parent explicitly requalifies them.

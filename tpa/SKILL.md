---
name: tpa
kg_ref: ATOM_Skill_tpa_orchestrator_v10
version: "2.0.0"
channel: stable
provenance: AI_DERIVED_FROM_USER_PRIMARY
description: >-
  Orchestrate the bounded TPA reverse code-to-design cycle TCW→ST→SP→TA with local recovery artifacts, evidence-based gates, drift audit, and optional feedback candidates. Invoke when: the user requests `/tpa`, reverse engineering, external or legacy code analysis, design recovery, status, or anchor audit. Do not use when: a new feature or project should be designed forward from intent to code; use `$apt` instead.
---

# TPA — bounded code-to-design recovery

TPA reconstructs an explanatory design model from existing code. It proposes anchors and bindings; it does
not automatically write ontology, status, supersession, ActionPlans, seeds, or Lessons.

## Entry contract

```yaml
cycle_id: stable local identifier
target: repository/path and exact revision
objective: inventory, contract recovery, pattern recovery, anchor audit, or full cycle
scope: included/excluded languages, generated code, tests, and dependencies
authority: read-only by default; exact writes only when separately authorized
validation_budget: parsers, builds/tests, and optional independent review
output: local recovery bundle and completion condition
```

## Phases

1. **TCW — TargetCodeWorld**: inventory files, languages, public symbols, dependencies, and entry points.
2. **ST — TargetTwin**: recover explicit and conventional contracts, preconditions, postconditions, and
   failure behavior.
3. **SP — TargetPyramid**: infer architectural/design patterns and alternatives from evidence.
4. **TA — TargetAnchor**: propose anchor/bindings and audit drift against code.

Route from available artifacts. A phase may return `BLOCKED` or `INCONCLUSIVE`; do not fabricate the next
artifact to complete the sequence.

## Gates

- target revision and inventory scope are exact;
- parser/AST evidence is preferred over grep-only claims;
- every recovered contract cites code evidence and distinguishes explicit from conventional;
- pattern claims list required elements, counterevidence, alternatives, and confidence basis;
- drift denominators and exclusions are fixed before measurement;
- independent review is used when material risk or policy requires it;
- one supported blocker can block; counts are telemetry only.

Zero findings is neither automatic pass nor automatic failure. Record checks and limits. Missing evidence
yields `RETURN`, `BLOCK`, or `INCONCLUSIVE`.

## Bounded orchestration

Use `$jaebaeman` only when file/language partitions can be reviewed independently. The parent creates a
manifest, grants read-only permission by default, bounds concurrency/timeouts, validates coverage, and
integrates by evidence rather than agent count.

Unknown symbols or patterns become bounded research candidates. Invoke `$prometheus` only if they block the
current recovery or the user requests it. Formal `$taliban` review and `$longinus` binding checks are also
conditional, not automatic phase ceremonies.

## Local recovery bundle

```yaml
cycle_id: string
target_revision: string
inventory: files, symbols, dependencies, and exclusions
contracts: explicit and conventional records
patterns: supported, alternative, novel, and uncertain records
anchor_proposal: reuse | branch | new | none
drift: fixed-denominator observations
evidence: paths, lines/symbols, commands, and versions
blockers: []
unknowns: []
followups: []
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

## Feedback boundary

Ordinary QualityGap, AntiPattern, and drift observations remain local. Repeated, high-risk,
cross-repository, or reusable evidence may become a `PENDING` verdict. A RootCause/Lesson candidate requires
demonstrated cause and reusable prevention. Canonical anchor/status/supersession mutation requires a named
pending record and separately authorized ratifier/writer with exact readback.

## Stop rule

The cycle completes when the requested recovery bundle is classified and relevant checks are recorded.
Discoveries become bounded candidates; there is no automatic research, sibling, seed, feedback node,
ActionPlan, or recursive re-entry.

## Subskills

- [`../tpa-tcw/SKILL.md`](../tpa-tcw/SKILL.md)
- [`../tpa-st/SKILL.md`](../tpa-st/SKILL.md)
- [`../tpa-sp/SKILL.md`](../tpa-sp/SKILL.md)
- [`../tpa-ta/SKILL.md`](../tpa-ta/SKILL.md)
- [`references/feedback_loop.md`](references/feedback_loop.md)
- [`references/hard_rules.md`](references/hard_rules.md)

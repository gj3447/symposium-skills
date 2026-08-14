---
name: apt-lens-enforce
kg_ref: ATOM_Skill_apt_lens_enforce
version: "2.0.0"
channel: stable
canonical_name: apt-lens-enforce
description: >-
  Enforce target-specific Naesengmoon evidence rules at material APT gates, including steelmanning, independent review when required, direct oracle checks, blocker criteria, and a local receipt. Use when: admitting or auditing a material APT gate verdict or its evidence contract. Do not use when: diagnosing which Inform/Constrain/Verify/Correct axis is weak; use `$apt-feedback-lens` instead.
---

# APT lens enforcement

This skill checks whether a material APT gate has enough evidence for its declared decision. It does not
force adversarial review, human approval, a fixed finding count, or a KG write at every transition.

## Input

```yaml
target: exact artifact and revision
gate: decision being made
criteria: observable pass, return, and blocker conditions
oracle: directly relevant test, proof, source, or readback
risk: why independent adversarial review is or is not required
lenses: bounded target-specific concerns
independence: executor/reviewer relation
```

## Checks

1. The target and criteria were fixed before review.
2. The artifact was steelmanned against its source/contract.
3. Decision-relevant findings have falsifiable claims and inspectable evidence.
4. Shared evidence and reviewer dependence are explicit.
5. Direct oracle checks ran when available.
6. One supported blocker blocks; unsupported objections and counts do not.
7. `APPROVE` has no unresolved declared blocker; missing evidence yields `RETURN` or `INCONCLUSIVE`.

Zero findings is not an automatic pass. Require a receipt of checks and limitations. It is also not an
automatic rejection or reason to invent nitpicks.

## Human and substitution boundaries

Human input is required only for a genuine unresolved choice, explicit waiver, authority boundary, or
ratification. A substitute contract or reduced rigor is allowed only when the current task names it and
the receipt records the resulting limits; the skill does not edit configuration to enable it.

## Output

```yaml
decision: APPROVE | CONDITIONAL | RETURN | BLOCK | INCONCLUSIVE
target: exact revision
criteria_checked: []
oracle_results: []
findings: []
supported_blockers: []
coverage_gaps: []
independence: explicit value
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

The default is local. Material reusable evidence may be proposed as `PENDING`; canonical/status/config/
confidence mutation requires separate authorized ratification and exact readback. No automatic Lesson,
feedback node, retry sprint, or recursive review occurs.

## Done

- The verdict follows declared evidence criteria, not counts.
- Independence and coverage gaps are visible.
- Any override names its authorizer, boundary, supplied reason, duration, and review condition.
- No direct KG/canon/config/status mutation occurred.

Historical HR rules that mandated every-gate critics, minimum findings, human ceremony, and Cypher writes
remain in Git history and are not active in v2.

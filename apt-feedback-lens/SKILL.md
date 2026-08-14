---
name: apt-feedback-lens
kg_ref: ATOM_Skill_apt_feedback_lens
version: "2.0.0"
channel: stable
canonical_name: apt-feedback-lens
aliases: [apt-4axis-lens, harness-4axis-lens]
description: >-
  Apply the APT Inform/Constrain/Verify/Correct concern preset to L_IDE harness health and return evidence-backed per-concern findings through Naesengmoon. Use when: an APT gate shows wrong direction, gold plating, false-green verification, recurrence, or explicitly requests `--lens apt-4axis`. Do not use when: enforcing target-specific gate admissibility or reviewing another harness layer; use `$apt-lens-enforce` or the owning layer review instead.
---

# APT feedback lens — four concern preset

This is a named set of four diagnostic concerns for the L_IDE harness layer. Four is taxonomy/coverage
metadata, not a mandatory critic count, finding quota, unanimity rule, or verdict threshold.

## Concerns

| Concern | Question | Typical evidence |
|---|---|---|
| **Inform** | Did the actor have the necessary context before action? | supplied specs, source provenance, missing context |
| **Constrain** | Were scope, permissions, contracts, and resource bounds explicit? | write-set, types, limits, gate contract |
| **Verify** | Did direct post-action checks test the claimed outcome? | tests, builds, proofs, exact external readback |
| **Correct** | Was an observed defect corrected and recurrence prevention evidenced when reusable? | before/after evidence, root-cause discriminator, prevention check |

These concerns refine the Guides/Sensors distinction. They are not automatically applicable to runtime
or multi-computer harness layers; choose those layers' own failure modes.

## Invocation

```text
/taliban <target> --lens apt-4axis
```

The parent may assign the four concerns to one or more reviewers as useful. Each concern returns:

```yaml
concern: INFORM | CONSTRAIN | VERIFY | CORRECT
status: PASS | BLOCK | INCONCLUSIVE | NOT_APPLICABLE
claim: falsifiable statement
evidence: exact path, command, source, or observation
limitations: []
suggested_action: optional bounded proposal
```

## Synthesis

- One supported blocker may block the target decision.
- `PASS` requires positive evidence for the declared criterion, not an empty finding list.
- Missing evidence yields `INCONCLUSIVE`.
- `NOT_APPLICABLE` includes a reason.
- Counts and unanimity never determine the verdict.
- Preserve supported dissent and shared-evidence dependence.

The output is a local Naesengmoon receipt or qualified `PENDING` proposal. Do not create/mutate KG,
ValidationResult, AptFeedback, Lesson, ActionPlan, status, confidence, or configuration. Correction does not
require a Lesson for ordinary bugs; a Lesson candidate needs evidenced cause and reusable prevention.

## Stop rule

Return after the four concerns are classified for the exact target/revision. No automatic additional lens,
critic, retry, repair, or recursive feedback cycle occurs.

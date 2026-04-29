# apt — Adversarial

> **Lazy-load reference for `apt` skill.**
> Loaded *only when* the orchestrator enters the relevant phase/gate.
> Parent skill: [`../SKILL.md`](../SKILL.md). Repo CHANGELOG: [`../../CHANGELOG.md`](../../CHANGELOG.md).
> Refactor source: PROM 16 F6.1 Progressive Disclosure (2026-04-29).
> KG: `lesson-prom16-skillver-progressive-disclosure-drift-2026-04-29`.

---

## 7. Anti-Bypass Mechanisms

### 7.1 Detection Rules

| # | Bypass Attempt | Detection | Response |
|---|---------------|-----------|----------|
| 1 | Critic returns < 3 findings | Count check | Re-run with stronger prompt (Section 7.2) |
| 2 | Same model for design and critique | Model comparison | BLOCK -- switch critic model |
| 3 | No human response to sigma_oracle | Response check | BLOCK and re-ask. Never assume approval. |
| 4 | Agent tries to auto-approve sigma | Config check | BLOCKED by allow_agent_sigma: false |
| 5 | Gate transition without adversarial round | KG audit (V28) | BLOCK -- run adversarial round |
| 6 | Ground-truth-testable claim not tested | KG audit (V29) | BLOCK -- run ground truth command |
| 7 | Critic produces only NITPICK findings 5+ times | Severity distribution | Rotate critic model + alert |
| 8 | Design agent ignores PERFORMANCE findings | Diff comparison | Escalate to sigma_oracle |
| 9 | All findings dismissed by ground truth 3+ times | Override history | Review critic prompt for hallucination |
| 10 | sigma_oracle approves without reviewing findings | Cannot detect automatically | Include findings summary in approval prompt |

### 7.2 Stronger Prompt for Insufficient Findings

When the critic returns fewer than 3 findings, re-invoke with this escalated prompt:

```markdown
# ESCALATED ADVERSARIAL REVIEW

Your previous review produced only {N} findings. The minimum is 3.
This is NOT acceptable. You MUST find at least 3 issues.

Mandatory deep-dive checklist:
1. Re-read EVERY line of the artifact. What could go wrong at runtime?
2. What happens with EMPTY input? NULL input? MAXIMUM-SIZE input?
3. What concurrent access patterns could cause race conditions?
4. What happens if a DEPENDENCY changes its API?
5. What error handling is MISSING?
6. What SECURITY implications exist?
7. What PERFORMANCE characteristics are unverified?
8. Does this violate ANY APT axiom (A1-A4)?
9. Is every postcondition ACTUALLY TESTABLE with concrete assertions?
10. What would a HOSTILE code reviewer say about this?

You MUST produce at least 3 findings. If you still cannot, produce 3 NITPICK
findings with documented evidence of thorough review methodology.
```

### 7.3 Model Separation Enforcement

| Design Agent | Acceptable Critic | Rationale |
|-------------|------------------|-----------|
| opus | sonnet or haiku | Different weights = different biases |
| sonnet | haiku or opus | Cross-tier critique |
| Any model | Same model, different temperature | INSUFFICIENT -- same weights |
| Any model | Same model, different prompt only | INSUFFICIENT -- framing contagion |

**v17 enforcement**: Before spawning critic, check that critic_model != design_model.
If they match, BLOCK and log error.

**Lite Mode exception**: When only one model is available, the same model MAY serve as
critic but MUST use the full D22.3 template AND all anti-rubber-stamp techniques are
MANDATORY. This exception must be logged as AptDecisionLog with reason.

### 7.4 Anti-Rubber-Stamp Techniques (10)

| # | Technique | Mechanism | Detects |
|---|-----------|-----------|---------|
| 1 | Model separation | Different model weights | Confirmation bias contagion |
| 2 | Minimum finding count | Hard minimum of 3 | Lazy approval |
| 3 | Core assumption challenge | 1+ finding must target core assumption | Surface-only critique |
| 4 | Anti-checklist | 10-item checklist critic must address | Incomplete review |
| 5 | Falsifiability requirement | Every finding must be testable/verifiable | Vague handwaving |
| 6 | Ground truth cross-check | ground_truth_testable findings auto-verified | Phantom bugs |
| 7 | Severity distribution audit | >80% NITPICK across 5+ rounds = flag | Nitpick-only rubber-stamp |
| 8 | Historical finding rate | Track findings-per-round; alert if always 3 | Gaming the minimum |
| 9 | Blind review | Critic does not see previous sigma_oracle decisions | Anchoring to authority |
| 10 | Rotation | Critic model rotated after 5+ consecutive rounds | Adaptation/overfitting |

---



## 15. Mode Collapse Detection (D24)

### 15.1 Detection Signals

| Signal | Threshold | Action |
|--------|-----------|--------|
| Exactly 3 findings (minimum) for 5+ consecutive rounds | 5 rounds | Alert: critic may be rubber-stamping |
| Same NITPICK-only verdict for 3+ consecutive rounds | 3 rounds | Rotate critic model |
| Design agent does not modify artifact after PERFORMANCE findings | 2 rounds | Escalate to sigma_oracle |
| All findings dismissed by ground truth override | 3 rounds | Review critic prompt for hallucination |
| sigma_oracle approves without reading critic findings | 1 occurrence | Alert (meta-discriminator failure) |

### 15.2 The Human as Meta-Discriminator

sigma_oracle remains essential even with automated adversarial rounds. The adversarial system
can itself fail (both agents converge on a shared blind spot). The human detects meta-level
failures that no amount of automated adversarial rounds can catch.

This is why `allow_agent_sigma: false` is LOCKED in v17.

### 15.3 Context Window as Shared Weight Space

```
Session-scoped:  Context Window  <-->  GAN weights during one training run
Persistent:      Knowledge Graph  <-->  GAN weights saved to checkpoint

AdversarialRound findings --> KG:AptFeedback nodes
  = saving validated knowledge (like checkpoint saving)

Next session loads KG findings --> context
  = loading pretrained weights for continued training
```

---

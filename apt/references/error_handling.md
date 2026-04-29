# apt — Error Handling

> **Lazy-load reference for `apt` skill.**
> Loaded *only when* the orchestrator enters the relevant phase/gate.
> Parent skill: [`../SKILL.md`](../SKILL.md). Repo CHANGELOG: [`../../CHANGELOG.md`](../../CHANGELOG.md).
> Refactor source: PROM 16 F6.1 Progressive Disclosure (2026-04-29).
> KG: `lesson-prom16-skillver-progressive-disclosure-drift-2026-04-29`.

---

## 9. Error Handling

### 9.1 When Critic Disagrees with Design Agent

```
IF critic verdict = REJECT (>= 1 BLOCKER):
  1. Design agent reviews BLOCKER findings
  2. For ground_truth_testable findings: run ground truth command
     - If ground truth CONFIRMS: fix the issue, re-submit
     - If ground truth CONTRADICTS: finding dismissed (log override)
  3. For non-testable findings: present to sigma_oracle with both perspectives
  4. sigma_oracle decides: fix it | dismiss with reason | escalate
  5. Log decision as AptDecisionLog

IF critic verdict = CONDITIONAL_PASS (PERFORMANCE findings):
  1. Design agent reviews PERFORMANCE findings
  2. Run benchmarks if applicable
  3. sigma_oracle decides: fix now | accept with tech debt | escalate
  4. Log decision

IF critic verdict = PASS (only DESIGN_DEBT + NITPICK):
  1. Log findings as tech debt
  2. Proceed to sigma_oracle for final approval
  3. sigma_oracle may still RETURN for any reason
```

### 9.2 When Ground Truth Fails

```
IF cargo test fails:
  1. BLOCK gate immediately
  2. Fix the failing tests
  3. Re-run cargo test
  4. Only proceed when ALL tests pass
  5. Re-run adversarial round (critic sees updated code)

IF cargo build fails:
  1. BLOCK gate immediately
  2. Fix compilation errors
  3. Re-run from step 1

IF WebSearch contradicts design decision:
  1. Log the contradiction as AptFeedback (severity: BLOCKER)
  2. Present to sigma_oracle with evidence
  3. sigma_oracle decides: change approach | accept with justification
```

### 9.3 When sigma_oracle Does Not Respond

```
IF sigma_oracle prompt sent and no response in current context:
  1. DO NOT PROCEED
  2. DO NOT auto-approve
  3. Re-state the question clearly
  4. List what needs approval:
     - The proposal summary
     - Critic findings (count + severities)
     - Ground truth results
  5. Wait for human response
  6. If conversation continues on different topic: remind about pending approval
```

### 9.4 When Adversarial Round Reaches Max Iterations

```
IF adversarial_rounds >= max_adversarial_rounds (3):
  1. Log all findings from all rounds
  2. Escalate to sigma_oracle with full history
  3. sigma_oracle decides:
     - APPROVE with remaining findings as accepted debt
     - RETURN to earlier phase (SP/ST)
     - ABORT the span entirely
  4. Log decision with all context
```

### 9.5 When KAL Cannot Satisfy Density Requirements

```
IF KAL runs 3+ times and density still not met:
  1. Log current state (what types are missing, what ratio is)
  2. Present to sigma_oracle:
     "Density requirements not met after 3 KAL iterations.
      Current: {count} links, {types} source types, {ratio} ratio.
      Required: 5 links, 3 types, 2:1 ratio.
      Options: (a) override with justification, (b) manual knowledge entry, (c) abort span"
  3. sigma_oracle decides
  4. Log decision as AptDecisionLog with override_reason if applicable
```

### 9.6 When Critic and Design Agent Both Wrong (Meta-Failure)

```
IF sigma_oracle detects both agents converged on wrong approach:
  1. sigma_oracle provides correction
  2. Log as AptFeedback category="FalseNegative" (validation missed real issue)
  3. Reset to earlier phase if needed
  4. Record in KG for future training (KG as persistent weight space -- D24)
  5. Consider rotating both models for next round
```

---



## 13. Parallel Execution (D12)

### 13.1 Five Rules

| Rule | Description |
|------|-------------|
| SameLayer | Same parent's children = all parallel (A3 guarantees independence) |
| ParentChild | Parent decomposition complete -> then children. Vertical = sequential. |
| CrossBranch | Independent branches may be in different phases simultaneously. |
| AtomicIndependent | Sibling becomes AtomicSpan -> proceeds to PH4 independently. |
| LayerGateFirst | All children created -> RefinementGate -> then descend. |

### 13.2 SharedType (D14-D16)

Parent Span defines boundary types shared between children BEFORE children enter ST.

```
(Parent)--DEFINES_SHARED_TYPE-->(World:SharedType)<--OUTPUTS_TYPE--(CT_WorldGen)
                                       ^
                              INPUTS_TYPE
                                       |
                                (CT_Renderer)
```

- One type = one node (D14). MERGE only.
- Parent defines first (D15). Children reference only.
- SEQUENCED_WITH auto-derived (D16). From OUTPUTS_TYPE -> INPUTS_TYPE pairs.

### 13.3 Visibility Scope (D13)

| Phase | Can See | Cannot See |
|-------|---------|-----------|
| SP decomposition | Parent description + sibling names | Sibling internals, other branches |
| ST crystallization | Self + parent + SharedType | Sibling Contract internals |
| SCW implementation | Self Contract + target_file | Sibling source code |
| Integration | Sibling input/output_type | Sibling internal logic |

### 13.4 Layer Gates

| Gate | When | On Fail |
|------|------|---------|
| LayerDecomposition | After all children created | Delete children + re-decompose |
| CrystallizationEntry | Before PH4 entry | Remove AtomicSpan + back to PH3 |
| ContractComplete | Before PH5 entry | Contract draft + /apt-st |
| Fulfillment | After PH5 implementation | Re-implement / back to PH4/PH3 |
| Integration | After all siblings complete | Contract modification or re-decompose |

**v17**: Each layer gate ALSO requires adversarial round completion (V28).

### 13.5 Parallel Validation (V18-V20)

| V# | Target | Severity |
|----|--------|:--------:|
| V18 | Duplicate SharedType | P1 |
| V19 | Orphan SharedType (no references) | P3 |
| V20 | Producer without consumer | P2 |

---

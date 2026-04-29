# apt — Gates

> **Lazy-load reference for `apt` skill.**
> Loaded *only when* the orchestrator enters the relevant phase/gate.
> Parent skill: [`../SKILL.md`](../SKILL.md). Repo CHANGELOG: [`../../CHANGELOG.md`](../../CHANGELOG.md).
> Refactor source: PROM 16 F6.1 Progressive Disclosure (2026-04-29).
> KG: `lesson-prom16-skillver-progressive-disclosure-drift-2026-04-29`.

---

### 3.2 Gate Sequence at Each Transition

Every transition follows this EXACT sequence. No steps may be skipped.

#### PH3 (SP Decomposition) Gate Sequence:

```
1. KG Density Check (D21)
   - Query INFORMED_BY count
   - If < 5: BLOCK --> run KAL
   - Check source type diversity
   - If < 3 types: BLOCK --> diversify via KAL
   - Check foundation:composite ratio
   - If < 2:1: BLOCK --> acquire more foundational sources

2. C(S) Predicate Evaluation (cheap rejection first)
   - v (complexity <= 500 lines)
   - tau (concrete I/O types)
   - iota (testable assertions)
   - delta (decomposition diseconomy)
   - sigma_auto (automated check)

3. Adversarial Round (C_S_sigma)
   - Spawn adversarial-critic agent (sonnet model)
   - Critic receives: decomposition plan, INFORMED_BY links, span context
   - Critic MUST produce >= 3 findings
   - If < 3 findings: re-run with STRONGER prompt (see Section 7.2)
   - Each finding logged as AptFeedback node in KG
   - WebSearch evidence MUST be cited for each design decision

4. Ground Truth Verification
   - KAL link density verified (automated)
   - Architecture pattern WebSearch completed
   - tau banned-type check executed

5. sigma_oracle (HUMAN)
   - Present to human: proposal + critic findings + ground truth results
   - BLOCK until human responds
   - Human decides: APPROVE | RETURN(reason) | ESCALATE
   - Decision logged as AptDecisionLog node in KG

6. Log to KG
   - Create AptDecisionLog node with full audit trail
   - Link to span, critic findings, ground truth results
```

#### PH4 (ST Crystallization) Gate Sequence:

```
1. Contract Completeness Check
   - input_type defined
   - output_type defined
   - acceptance_tests defined
   - postconditions falsifiable

2. Adversarial Round (RefinementGate)
   - Spawn adversarial-critic agent (sonnet model)
   - Critic receives: contract draft, task description, test sketch
   - Critic MUST produce >= 3 findings
   - If < 3 findings: re-run with STRONGER prompt
   - Each finding logged as AptFeedback node in KG
   - WebSearch evidence MUST be cited for design decisions

3. Ground Truth Verification
   - tau_check 5/5 passes
   - Postcondition falsifiability test passes
   - WebSearch for API compatibility, prior art

4. sigma_oracle (HUMAN)
   - Present to human: contract + critic findings + ground truth
   - BLOCK until human responds
   - Decision logged as AptDecisionLog node in KG

5. Log to KG
```

#### PH5 (SCW Implementation) Gate Sequence:

```
1. Implementation Completion
   - Code written following TDD (RED -> GREEN -> REFACTOR)
   - MATERIALIZES relationship created

2. Ground Truth Verification (MANDATORY -- runs FIRST)
   - cargo test: MUST pass (all tests green)
   - cargo build --release: MUST compile
   - cargo clippy -- -D warnings: MUST pass
   - If any fail: BLOCK -- fix before proceeding

3. Adversarial Round (FulfillmentGate)
   - Spawn adversarial-critic agent (sonnet model)
   - Critic receives: implemented code, contract, test results, coverage
   - Critic MUST produce >= 3 findings
   - If < 3 findings: re-run with STRONGER prompt
   - Each finding logged as AptFeedback node in KG
   - Ground-truth-testable findings get auto-verified (D23)

4. FulfillmentGate 13/13 Check
   - Checks 1-11: unchanged from v14
   - Check 12: Adversarial Critic review PASS -- no unresolved BLOCKERs
   - Check 13: Ground truth primacy verified -- all factual claims validated

5. sigma_oracle (HUMAN)
   - Present to human: code + test results + critic findings + coverage
   - BLOCK until human responds
   - Decision logged as AptDecisionLog node in KG

6. Log to KG
```

---



## 12. Gate Evidence Table (v17)

```
Gate Evidence Table (v17):
+---------------+--------------------------------------------------------------+
| Transition    | Required Evidence                                            |
+---------------+--------------------------------------------------------------+
| -> PH3 (SP)  | SA exists AND root span created                              |
| SP internal   | KAL complete AND INFORMED_BY >= 5                            |
|               | v17: source_types >= 3 AND foundation:composite >= 2:1       |
|               | v17: DensityCheck logged in KG                               |
+---------------+--------------------------------------------------------------+
| -> PH4 (ST)  | C(S) auto pass AND sigma_oracle approved                     |
|               | v17: AdversarialRound(C_S_sigma) -- no BLOCKERs             |
|               | v17: WebSearch evidence cited for design decisions           |
|               | v17: sigma_oracle is HUMAN (allow_agent_sigma: false)        |
|               | v17: AptDecisionLog created in KG                            |
+---------------+--------------------------------------------------------------+
| -> PH5 (SCW) | tau_check 5/5 AND impact_tests defined                       |
|               | v17: AdversarialRound(RefinementGate) -- no BLOCKERs        |
|               | v17: WebSearch evidence for API choices                      |
|               | v17: sigma_oracle is HUMAN                                   |
|               | v17: AptDecisionLog created in KG                            |
+---------------+--------------------------------------------------------------+
| PH5 -> DONE  | FulfillmentGate 13/13 AND coverage AND NFR                   |
|               | v17: cargo test PASS (MANDATORY before anything else)        |
|               | v17: cargo clippy PASS                                       |
|               | v17: AdversarialRound(FulfillmentGate) completed             |
|               | v17: Ground truth primacy verified (all claims tested)       |
|               | v17: sigma_oracle is HUMAN                                   |
|               | v17: AptDecisionLog created in KG                            |
+---------------+--------------------------------------------------------------+
| -> PH6       | AptFeedback created (category + severity)                    |
+---------------+--------------------------------------------------------------+
```

---



## 23. Approval Gates Table (v17)

| Gate | Who | SLA | On Timeout |
|------|-----|-----|------------|
| sigma_auto (v,tau,iota,delta) | automated | instant | N/A |
| sigma_oracle | **HUMAN (LOCKED)** | 0 (immediate) | BLOCK -- re-ask |
| Adversarial Critic | automated (sonnet) | <= 60s per round | ESCALATE -- critic timeout = gate blocked |
| Ground truth (compiler/test) | automated | <= 300s | BLOCK -- ground truth must complete |
| DensityCheck | automated | <= 30s | BLOCK -- KAL must complete |

---

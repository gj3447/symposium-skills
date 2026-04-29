# apt — Theory

> **Lazy-load reference for `apt` skill.**
> Loaded *only when* the orchestrator enters the relevant phase/gate.
> Parent skill: [`../SKILL.md`](../SKILL.md). Repo CHANGELOG: [`../../CHANGELOG.md`](../../CHANGELOG.md).
> Refactor source: PROM 16 F6.1 Progressive Disclosure (2026-04-29).
> KG: `lesson-prom16-skillver-progressive-disclosure-drift-2026-04-29`.

---

## 17. Diffusion Analogy

| Diffusion | APT | Role |
|-----------|-----|------|
| prompt/conditioning | SA | Initial identity |
| noise -> coarse structure | SP | Abstract -> Span decomposition |
| coarse -> fine detail | ST | Span -> Contract specification |
| fine -> pixel-level | SCW | Contract -> Code (TDD) |
| U-Net | /apt orchestrator | Drives the denoising loop |
| denoising step | Phase transition | Each step reduces ambiguity |
| discriminator | adversarial-critic | Validates each denoising step (v17) |

---



## 18. GAN-Context Analogy (D24 -- Theoretical Foundation)

### 18.1 The Mapping

| GAN Concept | Agent Analog | Key Difference |
|------------|-------------|----------------|
| Generator | Design Agent | Produces code/architecture |
| Discriminator | Critic Agent | Evaluates quality |
| Weight space | Context Window + KG | Ephemeral + persistent |
| Training iteration | Adversarial round (D20) | 2-3 rounds vs thousands |
| Loss function | Ground truth: compiler, tests (D23) | Binary pass/fail |
| Mode collapse | Rushing through gates, self-approving | Detected by human |
| Overfitting | Confirmation bias / echo chamber | Fix: model separation (D22) |
| Gradient backprop | Context filling with critique text | Discrete chunks vs continuous |
| Nash equilibrium | Consensus or human decision | sigma_oracle breaks tie |
| Regularization | Anti-rubber-stamp techniques (D22.4) | Structural constraints |

### 18.2 KG as Persistent Weight Space

Adversarial round outcomes are recorded in KG (AptDecisionLog, AptFeedback nodes).
Next session loads relevant KG context = loading pretrained weights for continued training.

---



## 19. Mold Flow Diagram

```
Governance Mold -STARTS_WITH-> Intent Mold -NEXT-> Boundary Mold -NEXT-> Execution Mold -NEXT-> Assurance Mold
     |                |              |              |              |
     | Hook Engine     | Span Planner | Contract Reg | Work Queue   | Eval Harness
     | Agent Profile   | Req Graph    | Twin Registry| Subagent Rtr | Adversarial Gate (v17)
     |                |              |              | Runtime Trace|
     |                |              |              |              |
     +--- /apt -------+-- /apt-sp ---+-- /apt-st --+-- /apt-scw --+

     Memory Mold -CROSS_CUTS-> (all phases)
     | Memory Tier Manager / Reflection Memory / Checkpoint Ledger

     Adversarial Layer (v17) -CROSS_CUTS-> (SP, ST, SCW gates)
     | Critic Agent / Ground Truth / KG Logging / Anti-Bypass
```

---



## 28. Theoretical Foundations

| Domain | APT Element |
|--------|-------------|
| Dynamic Programming | SP decomposition (independent subproblems, memoization) |
| P-Coalgebra | DECOMPOSES_TO (branching with termination) |
| Hoare Logic | Contract as {P}f{Q} analogy, SEQUENCED_WITH |
| Extended Mind | KG as external cognition (Clark & Chalmers 1998) |
| Thompson Sampling | Gap Resolution (70% exploitation, 30% exploration) |
| DDD | Bounded contexts, ubiquitous language |
| CSP | Agent -> Kafka -> KG (no shared state) |
| Kuhn / Godel | Version evolution, sigma_oracle irreducibility |
| Wolfram Hypergraph | Bipartite incidence, EXPLORES_VIA, confluence |
| **GAN Theory** | **Adversarial validation, mode collapse detection, regularization (v17)** |

---



## 29. Version History

| Ver | Key Change |
|-----|-----------|
| v14 | Harness techniques executable, eval-optimizer, hook engine |
| v15 | Adversarial Validation Layer (D20-D24), FulfillmentGate 13/13, V27-V29 |
| v16 | Skill file consolidation, Auto Mode, Mold Flow, full orchestrator |
| **v17** | **MANDATORY adversarial enforcement. allow_agent_sigma: false LOCKED. Every gate: adversarial + ground truth + HUMAN sigma_oracle. Anti-bypass mechanisms. KG logging for all decisions. Stronger re-attack prompts. Mode collapse detection. 29 validations. Cannot be bypassed.** |

---

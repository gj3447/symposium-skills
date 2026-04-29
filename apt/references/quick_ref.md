# apt — Quick Ref

> **Lazy-load reference for `apt` skill.**
> Loaded *only when* the orchestrator enters the relevant phase/gate.
> Parent skill: [`../SKILL.md`](../SKILL.md). Repo CHANGELOG: [`../../CHANGELOG.md`](../../CHANGELOG.md).
> Refactor source: PROM 16 F6.1 Progressive Disclosure (2026-04-29).
> KG: `lesson-prom16-skillver-progressive-disclosure-drift-2026-04-29`.

---

## 16. Auto Mode (Restricted in v17)

Auto Mode is available but with MANDATORY adversarial gates at every transition.
sigma_oracle is STILL HUMAN even in auto mode -- the agent handles KAL, decomposition,
and ground truth automatically, but BLOCKS at each sigma_oracle checkpoint.

### 16.1 Auto Mode Algorithm (v17 Modified)

```
ALGORITHM AutoMode_v17(project_name, description):
  // PH1-PH2: SA
  INVOKE /apt-sa with {project_name, description}
  WAIT for SA + RootSpan creation

  // PH3-PH6: Loop until all spans materialized
  WHILE true:
    unfinished = QUERY all non-materialized AtomicSpans
    IF unfinished is empty: BREAK

    FOR EACH span IN unfinished (parallel, max 4):
      phase = detect_phase(span)

      IF phase = 'PH3':
        // v17: Density check FIRST
        density = DensityCheck(span)
        IF NOT density.pass: AUTO_KAL(span)  // automatic
        // Decompose
        INVOKE /apt-sp with {span}
        // v17: Adversarial round (automatic)
        critic = AdversarialRound(decomposition, "C_S_sigma")
        // v17: BLOCK for human sigma_oracle
        PRESENT {proposal, critic.findings, ground_truth} to HUMAN
        WAIT for HUMAN response  // CANNOT SKIP

      ELIF phase = 'PH4':
        INVOKE /apt-st with {span}
        // v17: Adversarial round
        critic = AdversarialRound(contract, "RefinementGate")
        PRESENT to HUMAN
        WAIT for HUMAN response

      ELIF phase = 'PH5':
        INVOKE /apt-scw with {span}
        // v17: Ground truth FIRST
        RUN cargo test -- MUST PASS
        // v17: Adversarial round
        critic = AdversarialRound(code, "FulfillmentGate")
        PRESENT to HUMAN
        WAIT for HUMAN response

      ELIF phase = 'PH6':
        feedback = get_feedback(span)
        IF feedback.returns < max_returns_per_span:
          route_feedback(feedback)
        ELSE:
          PAUSE "Max returns reached. Human review needed."

    // Validate after each round
    violations = RUN V1-V6 + V28 + V29
    IF violations > 0: PAUSE "Violation detected."

  // Final validation
  RUN V1-V29 (full health check)
  RETURN "All spans materialized. Project complete."
```

### 16.2 When to Use Auto Mode

| Scenario | Auto Mode? | Why |
|----------|:----------:|-----|
| Simple project (CRUD, CLI) | Maybe | Human sigma still required at every gate |
| Tutorial / Hello World | Maybe | Lower risk but gates still enforced |
| Complex domain project | No | Manual control recommended |
| Production-critical | No | Full manual mode essential |

### 16.3 Guardrails

- V1-V6 + V28 + V29 axiom checks after every round
- max_returns_per_span prevents infinite feedback loops
- sigma_auto still runs even in auto mode
- PAUSE on axiom violation -> human must resolve before continuing
- sigma_oracle is ALWAYS HUMAN even in auto mode (HR2)

---



## 20. Quick Reference -- Decision Tree

```
"I need to..."
    |
    +-- "...start a new project"
    |       -> /apt-sa (create SemanticAnchor, bootstrap context)
    |
    +-- "...break down a feature"
    |       -> /apt-sp (density check -> decompose -> adversarial -> sigma_oracle)
    |
    +-- "...write a contract/spec"
    |       -> /apt-st (crystallize -> adversarial -> sigma_oracle)
    |
    +-- "...implement code"
    |       -> /apt-scw (TDD -> cargo test -> adversarial -> sigma_oracle)
    |
    +-- "...check APT compliance"
    |       -> /apt (run V1-V29 including V28/V29 adversarial checks)
    |
    +-- "...find what phase I'm in"
    |       -> /apt (phase detection query, Section 2)
    |
    +-- "...report a problem"
    |       -> /apt (feedback system, Section 14)
    |
    +-- "...see adversarial history"
    |       -> /apt (decision audit trail query, Section 8.5)
    |
    +-- "...override a gate"
    |       -> HUMAN must provide reason. Logged as AptDecisionLog (Section 8.3)
    |
    +-- "...understand the methodology"
    |       -> Read references/apt_core.md
    |
    +-- "...check infrastructure setup"
    |       -> Read references/apt_infra.md
    |
    +-- "...see validation details"
            -> Read references/apt_reference.md
```

---



## 21. When to Use Each Skill

| Situation | Skill | Why |
|-----------|-------|-----|
| New project / no SA | `/apt-sa` | Bootstrap identity first |
| "Implement feature X" (unknown phase) | `/apt` -> detect phase -> delegate | Don't assume phase |
| "Plan the architecture for Y" | `/apt-sp` directly | Clearly SP work |
| "Write the contract for Z" | `/apt-st` directly | Clearly ST work |
| "Code the function for W" | `/apt-scw` directly | Clearly SCW work |
| "Check APT compliance" | `/apt` validation | Run V1-V29 |
| "Where does this feature go?" | `/apt` + KG query | Phase detection |
| "Audit the KG" | `/apt` validation | Full health check |
| "What phase am I in?" | `/apt` phase detection | Per-branch detection |
| "Review adversarial history" | `/apt` + Section 8.5 query | Decision audit trail |

---



## 22. Core Concepts Summary

### 22.1 Axioms (violation = not APT)

- **A1: ContractOnlyAtST** -- Contracts owned only by SemanticTwin
- **A2: RecursiveDecomposition + Termination** -- min 2 children, all paths end at AtomicSpan
- **A3: SiblingIndependence** -- no DEPENDS_ON between siblings
- **A4: CrystallizationFrontierUniqueness** -- CRYSTALLIZES_TO is the sole SP->ST bridge

### 22.2 Key Design Principles (D1-D24)

| Principle | Description |
|-----------|-------------|
| D1 | HyperedgeHub -- CrystallizationEvent as bipartite incidence hub |
| D3 | TaskAsScaffolding -- Task (NL) != Contract (formal spec) |
| D4 | DenseBeforeContract -- links(S) >= 5 before crystallization |
| D5 | SingleFileProjection -- AtomicSpan -> 1 file <= 500 lines |
| D9 | GenerativeFlowOrdering -- SA->SP->ST->SCW forward; reverse for Bottom-Up Ascent |
| D10 | NFR as First-Class -- latency, memory, accuracy in Contract nfr_* fields |
| D11 | KnowledgeAcquisitionLoop -- auto-search KG + web before decomposition |
| D12 | ParallelExecution -- sibling parallel, parent-child sequential |
| D14 | OneTypeOneNode -- one SharedType = one KG node |
| D15 | ParentDefinesInterfaceTypes -- parent defines boundary types before children ST |
| D16 | SequencingFromSharedType -- SEQUENCED_WITH auto-derived from types |
| D17 | SA as Index -- SA connected to everything, retroactive OK |
| **D20** | **AdversarialValidation -- every gate includes adversarial round** |
| **D21** | **FoundationalDensityPrinciple -- source diversity + foundation:composite ratio** |
| **D22** | **AdversarialCriticAgent -- model separation + anti-rubber-stamp** |
| **D23** | **GroundTruthPrimacy -- compiler > agent > intuition for facts** |
| **D24** | **GAN-ContextAnalogy -- theoretical foundation for adversarial layer** |

### 22.3 Crystallization Predicate C(S)

C(S) = v AND tau AND iota AND delta AND sigma (ALL must pass, cheap rejection first)

### 22.4 KG Reference Convention

All code files MUST include:
```
# KG: TASK_xxx -- links to SemanticTask node
# KG: CT_xxx -- links to AptContract node
```

---

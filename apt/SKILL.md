---
name: apt
kg_ref: ATOM_Skill_apt_orchestrator
version: "28.0.0"
channel: stable
description: >-
  Orchestrate a bounded APT forward design-to-code cycle through semantic framing, decomposition, contract refinement, implementation, verification, cleanup, and optional method review with evidence-based gates. Use when: the user invokes APT, a new project needs the formal phase cycle, or an existing APT artifact must continue or be validated. Do not use when: an ordinary scoped implementation or debug can proceed directly, or existing code needs reverse design recovery; use direct handling or `$tpa` instead.
---

# APT — bounded design-to-code orchestration

APT turns an intent into checked implementation artifacts while preserving traceability between meaning,
decomposition, contract, code, and evidence. It is not a mandatory multi-agent ceremony or an automatic
KG/Lesson feedback loop.

## Invariants

- The parent owns scope, phase routing, write authority, integration, and the final decision.
- Each phase consumes an explicit artifact and returns a bounded artifact or blocker.
- Gates test observable criteria. Finding, reviewer, lens, and pass counts are telemetry only.
- Ordinary decisions, findings, and discoveries stay in the local cycle record.
- No phase directly mutates KG canon, confidence, status, configuration, ActionPlan, seed, or supersession.
- Follow-up, MetaReview, and adversarial review are conditional bounded invocations, never automatic
  recursive descendants.

## Entry contract

Freeze:

```yaml
cycle_id: stable local identifier
objective: requested outcome
target: repository, subsystem, or artifact
scope:
  included: []
  excluded: []
constraints: compatibility, safety, authority, and deadlines
existing_artifacts: known anchor, spans, contracts, code, and receipts
write_authority: exact files or systems allowed
validation_budget: directly relevant checks and optional reviewers
output: requested artifact and completion condition
```

For scientific work, declare the highest applicable T0/T1/T2 tier before observing results. T0/T1 may
escalate when a result materially affects a claim; T2 never downgrades after the outcome is seen.

## Phase routing

Route from the actual artifact state rather than a global phase counter:

1. **SA — semantic anchor**: clarify intent, users, boundaries, and non-goals.
2. **SP — span decomposition**: split work into cohesive, testable units with explicit dependencies.
3. **ST — semantic twin/contract**: define inputs, outputs, invariants, failures, and evidence criteria.
4. **SCW — implementation**: implement the smallest contract slice and verify it.
5. **Cleanup**: remove duplication and accidental structure while preserving verified behavior.
6. **MetaReview**: only when the cycle reveals a material reusable method issue.

Branches may be in different phases. Do not create missing artifacts merely to satisfy a sequence; create
only what the requested work needs.

## Phase contracts

### SA

Input: user intent and existing context. Output: a local anchor containing the objective, actors, domain,
scope, constraints, assumptions, and unresolved questions. User-primary language is preserved verbatim
where it matters; AI interpretation is labeled.

### SP

Input: anchor and current system. Output: bounded spans with one responsibility, explicit dependencies,
acceptance criteria, and ownership. Decomposition size follows cohesion and risk, not fixed line counts.

### ST

Input: one span. Output: a contract with typed inputs/outputs, preconditions, postconditions, invariants,
failure cases, examples, and validation strategy. Ambiguity yields a question or blocker rather than a
fabricated decision.

### SCW

Input: approved contract and exact write authority. Output: the smallest coherent implementation, tests,
and observed checks. Preserve foreign dirty state. Use the repository's required writer/token protocol.

For TypeScript applications using Effect, keep deterministic transforms pure and immutable; put typed
failure, services, resources, concurrency, and I/O in the Effect shell; assemble Layers at one runtime
root; validate unknown inputs with version-matched Schema; and keep concurrency, retries, waits, and
cleanup bounded.

### Cleanup

Input: passing implementation and diff. Output: simpler structure with behavior preserved. Cleanup is
proportionate to the change; it does not require a fixed tool count or ratio. Destructive changes need
explicit scope and recoverability.

### MetaReview

Use `$apt-meta-review` only for a material recurring/high-risk/reusable method issue or explicit request.
A routine completed cycle returns without a Lesson. RootCause/Lesson proposals require demonstrated
cause and reusable prevention.

## Gates

Apply only gates relevant to the phase and risk:

- **scope**: target, non-goals, and authority are exact;
- **traceability**: each artifact cites its inputs and revision;
- **contract**: observable acceptance and failure criteria exist;
- **ground truth**: directly relevant tests, proofs, builds, or exact readbacks ran;
- **independence**: an external reviewer is used when material risk or policy requires it;
- **integration**: branch outputs agree on interfaces and shared assumptions;
- **cleanup**: verified behavior is preserved and accidental complexity did not grow.

One evidence-backed blocker may block. Zero findings is neither automatic approval nor automatic failure;
the receipt must show what was checked. Missing evidence yields `RETURN`, `BLOCK`, or `INCONCLUSIVE`.

Human input is required only for a genuine unresolved choice, authority boundary, or explicit ratification.
Do not manufacture a human gate for routine deterministic checks.

## Conditional method dispatch

- `$prometheus`: missing external evidence blocks design or a user requests research.
- `$jaebaeman`: independent subtasks can make useful bounded parallel progress.
- `$taliban`: formal adversarial validation is material to the decision.
- `$longinus`: code-to-claim/reference integrity needs verification.
- `$harness`: a bounded runtime/test loop is required.
- `$apt-meta-review`: evidenced reusable method improvement needs review.

Each dispatch has its own scope, permissions, budget, and completion condition. No commander is invoked to
fill a quota.

## Local cycle receipt

```yaml
cycle_id: string
target: exact artifact and revision
phase: SA | SP | ST | SCW | CLEANUP | META_REVIEW
inputs: []
outputs: []
decisions: []
evidence: []
checks: []
blockers: []
unknowns: []
followups: []
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

An override records the exact boundary waived, who authorized it, reason supplied, duration, and review or
rollback condition. Never invent authorization or an override reason.

## Persistence and ratification

The local cycle receipt is sufficient for ordinary work. Repeated, high-risk, cross-repository, or reusable
evidence may be proposed as `PENDING` with exact provenance and target. A separate authorized ratifier/writer
must identify that pending record, allowed fields, current values, and exact post-write readback before any
canonical mutation.

Independent reproduction strengthens evidence but cannot self-ratify. Counts, unanimity, or a producer's
success return never ratify.

## Follow-up and stopping

Discovery produces a bounded follow-up candidate. Start it in the current cycle only if it blocks the
requested outcome or the user explicitly asks. Each child is independently scoped and tiered. The parent
may complete after classifying current evidence and recording the candidate.

## Definition of done

- Requested artifacts exist at the exact target and preserve traceability.
- The smallest relevant phase/gates were applied.
- Authorized changes passed directly relevant checks.
- Blockers, dissent, and unknowns are visible.
- Counts were used only for coverage/telemetry.
- Persistence stayed local or `PENDING`; canonical change had separate ratification.
- No automatic Lesson, KG write, status/config mutation, or recursive descendant occurred.

## References

- [`references/phases.md`](references/phases.md) — phase artifact contracts.
- [`references/gates.md`](references/gates.md) — evidence gate details.
- [`references/adversarial.md`](references/adversarial.md) — reviewer independence and blocker handling.
- [`references/error_handling.md`](references/error_handling.md) — bounded failures and recovery.
- [`references/kg_logging.md`](references/kg_logging.md) — local receipts and qualified persistence.
- [`references/validation.md`](references/validation.md) — validation checklist.
- [`references/quick_ref.md`](references/quick_ref.md) — compact routing guide.
- [`references/theory.md`](references/theory.md) — methodological grounding and limits.

Historical v17–v27 mandatory finding counts, every-gate KG logging, auto-mode, and recursive feedback rules
remain under `references/_legacy/` and Git history. They are not active instructions in v28.

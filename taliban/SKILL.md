---
name: taliban
kg_ref: ATOM_Skill_taliban
version: "4.0.0"
channel: stable
canonical_name: 나생문
aliases: [taliban, tlb, 88-taliban, Rashomon, naesengmoon]
provenance: AI_DERIVED_FROM_USER_PRIMARY
description: >-
  Run Naesengmoon adversarial validation with an explicit target, bounded independent lenses, evidence-backed findings, oracle checks, dissent preservation, and a local validation receipt. Invoke when: a Span, Contract, code change, claim, phase gate, or existing artifact needs formal adversarial audit or revalidation. Do not use when: the task is constructive design, implementation, or an ordinary review needing no formal gate; use `$apt` or direct review instead.
---

# Naesengmoon — evidence-backed adversarial validation

Naesengmoon tries to falsify or constrain a target through genuinely different lenses. Lenses are not
votes. One verified blocking defect may block; many unsupported objections do not become evidence by
agreement.

## Persistence boundary

- Produce a local `AdversarialReceipt` or parent handoff by default.
- Return a `PENDING` proposal only for repeated, high-risk, cross-repository, or reusable evidence.
- Do not directly create `ValidationResult`, `Lesson`, MCTS, seed, or canonical nodes, and do not mutate
  confidence, status, configuration, contracts, or methodology slots.
- Ratification requires an identified pending record and a separately authorized ratifier/writer.
- Lens, critic, finding, and agreement counts are coverage telemetry, never truth or approval.

## Input contract

Freeze this before review:

```yaml
target: exact artifact, revision, claim, or gate
question: what decision the review informs
contract: acceptance and rejection criteria
oracle: executable or documentary ground truth, when available
scope: included and excluded concerns
lenses: named independent concerns
budget:
  reviewers: bounded concurrency
  deadline: explicit stop condition
independence: executor/reviewer relationship
output: local receipt or parent handoff
```

If the target or decision criteria cannot be identified, return `INCONCLUSIVE` rather than inventing a
contract.

## Lens selection

Choose lenses for distinct failure modes, not to satisfy a fixed cardinality. Examples include:

- constitutional or policy compliance;
- mathematical validity and counterexamples;
- implementation correctness and tests;
- security, privacy, and destructive-operation risk;
- operational reliability and rollback;
- provenance, citation, or code-to-claim integrity;
- scientific null, multiplicity, and layer separation when applicable.

Read configured LensSet definitions when they exist, but treat them as input metadata. This skill does
not edit the configuration or mark a lens as used. A single lens is valid when it covers the actual risk;
an ensemble is useful only when independent concerns warrant it.

## Workflow

### 1. Steelman the target

State the strongest faithful interpretation, intended invariant, exact revision, and exclusions. Check
that formulas, quoted claims, and code symbols are interpreted in their native context. Record ambiguity
as ambiguity; do not convert it into a defect before checking the source.

### 2. Build bounded lens tasks

For each selected lens define:

```yaml
lens_id: stable identifier
concern: one distinct failure mode
target_slice: exact files, claims, or behavior
checks: evidence-gathering actions
blocker_condition: observable condition that would block
output_schema: AdversarialFinding
permissions: read-only by default
timeout: bounded
```

The parent dispatches independent tasks through `$jaebaeman` when parallel review is useful. Reviewers
do not write shared state unless the parent grants a narrower explicit write task.

### 3. Gather evidence

Use the most direct oracle available: compiler, test, formal proof, exact readback, primary source, or
controlled reproduction. Defect injection is optional and only permitted when safe, reversible, and in
scope. A synthetic test cannot establish an external production outcome.

Each reviewer returns:

```yaml
finding_id: stable local identifier
lens_id: assigned lens
claim: one falsifiable objection or confirmation
severity: BLOCKER | HIGH | MEDIUM | LOW | NOTE
evidence: exact command, path, source, or observation
oracle_result: PASS | FAIL | NOT_AVAILABLE
relation: SUPPORTS | CONTRADICTS | INCONCLUSIVE
reproducibility: reproduced | not_reproduced | not_run | not_applicable
limitations: []
suggested_action: optional bounded correction
```

Reject findings with no inspectable claim or evidence. Preserve supported dissent even when other lenses
pass.

### 4. Reconcile without voting

Deduplicate by shared evidence lineage. Distinguish independent corroboration from derivative restatement.
Resolve conflicts by checking source quality, directness, applicability, and oracle results—not by
headcount or average severity.

Use these decision rules:

- `BLOCK`: at least one in-scope blocker condition is supported by valid evidence;
- `APPROVE`: every declared blocker condition was checked or shown not applicable, with no supported
  blocker remaining;
- `CONDITIONAL`: non-blocking corrections or explicit preconditions remain;
- `INCONCLUSIVE`: evidence, oracle access, scope, or independence is insufficient.

Coverage metrics may reveal an unreviewed concern, but a metric threshold does not itself approve or
reject the target.

### 5. Return the local receipt

```yaml
receipt_id: stable local identifier
target: exact revision or claim
decision: APPROVE | CONDITIONAL | BLOCK | INCONCLUSIVE
criteria_checked: []
findings: []
supported_blockers: []
supported_dissent: []
coverage_gaps: []
executor_reviewer_independence: explicit value
commands_and_sources: []
followups: bounded candidates
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

An `APPROVE` receipt means the declared checks passed for this target and revision. It is not universal
proof and does not update canon by itself.

## Scientific targets

For work that materially affects a scientific claim, declare the highest applicable T0/T1/T2 tier
before observing output. A T2 receipt names the target claim and algebra/physics fiber and reports the
independent relation, novelty, and fitting-risk axes. Null/multiplicity, numerical Bayes, and Lakatos
checks apply only under their canonical gates. A rerun of the same data is not independent evidence.

## Follow-up and stopping

Record discoveries and remediation as bounded follow-up candidates. Start one during this invocation
only if it blocks the requested decision or the user explicitly asks. Each child is independently scoped
and tiered. Do not automatically launch MCTS, another adversarial sprint, a sibling reviewer, or a
recursive self-review.

## Definition of done

- The exact target, criteria, oracle, scope, and review budget were frozen.
- Findings have inspectable evidence and dependence is visible.
- Supported dissent and coverage gaps are preserved.
- The decision follows evidence, never reviewer counts.
- The output stayed local unless it met the pending threshold.
- No direct KG/canon/config/status mutation or automatic recursion occurred.

## Method relationships

- `$jaebaeman` provides parent-managed independent dispatch.
- `$apt` owns constructive remediation.
- `$longinus` checks code-to-claim/reference integrity.
- `$prometheus` gathers missing external evidence.

Historical v0–v3 mandatory critic counts, unanimity gates, KG writes, MCTS hooks, and recursive variants
remain in Git history. They are not active instructions in v4.

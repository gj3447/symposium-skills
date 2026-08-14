---
name: prometheus
kg_ref: ATOM_Skill_prometheus
version: "7.0.0"
channel: stable
provenance: AI_DERIVED_FROM_USER_PRIMARY
description: >-
  Run an evidence-first Prometheus research cycle from a frozen question through source collection, independent-axis analysis, conflict-aware synthesis, and a bounded action handoff. Invoke when: the user requests `/prometheus`, research before action, an axis matrix, or a parameterized multi-finding cycle without using the short command. Do not use when: the user explicitly enters `/prom` or needs only a stable lookup or immediate scoped fix; use `$prom`, `$symposium-research`, or direct handling instead.
---

# Prometheus — evidence before action

Prometheus gathers the minimum evidence needed for a decision before implementation. It is a bounded
research method, not a mechanism for automatically expanding work, writing the knowledge graph, or
turning agreement counts into truth.

## Persistence boundary

- The default result is a local report or parent handoff.
- A repeated, high-risk, cross-repository, or reusable result may be returned as a provenance-bearing
  `PENDING` proposal.
- Do not directly create a `Lesson`, `ActionPlan`, seed, canonical node, or supersession, and do not
  mutate confidence, status, configuration, or a methodology slot.
- Canonical mutation requires an identified pending record and a separately authorized ratifier/writer.
- Finding and reviewer counts measure coverage only. They never determine truth, priority, confidence,
  or ratification.

## Inputs

Freeze these before collection:

```yaml
question: the exact question to answer
decision: the action or claim this research may affect
scope: included and excluded systems, files, dates, and domains
evidence_bar: what would support, contradict, or leave the question unresolved
source_policy: allowed sources and required primary-source checks
budget:
  axes: bounded number of independent concerns
  agents: bounded concurrency
  deadline: explicit stop condition
output: local artifact or parent handoff target
scientific_target:
  claim: exact claim, when T2
  fiber: ALGEBRA | PHYSICS, when T2
  evidence_layer: ALGEBRAIC | NUMERICAL | PHYSICS_MAPPING, when T2
```

If this is scientific work, declare the highest applicable ICE tier before observing the result. T0/T1
may escalate to T2 when a result materially affects a claim; T2 never downgrades after the outcome is
known.

## Workflow

### 1. Freeze the target

Write the question, decision boundary, assumptions, evidence bar, and stop condition. Separate facts
already known from hypotheses and requested deliverables. Do not broaden the task merely because a new
topic appears interesting.

### 2. Prefetch existing context

Read local canon, prior reports, code, and—when available—relevant KG records before external research.
KG access here is read-only. Record exact paths, identifiers, versions, dates, and unresolved conflicts.
Absence of a configured KG or methodology slot is not permission to create one.

### 3. Design independent axes

Split the question by genuinely different failure modes or evidence sources, for example:

- primary-source and version verification;
- implementation or runtime behavior;
- counterexamples and boundary conditions;
- operational, legal, security, or scientific consequences;
- independent reproduction.

Avoid several prompts that merely restate the same search. The parent owns the plan and dispatches only
subtasks that can make progress independently. Use `$jaebaeman` for a substantial bounded dispatch.

### 4. Collect structured findings

Each finding must contain:

```yaml
finding_id: stable local identifier
axis: assigned concern
claim: one falsifiable statement
evidence:
  source: path, URL, command, or dataset identifier
  observation: concise result
  captured_at: timestamp or source date
method: how the observation was obtained
relation: SUPPORTS | CONTRADICTS | INCONCLUSIVE | NOT_APPLICABLE
independence: independent | shared_input | derivative | unknown
limitations: known uncertainty, selection, or missing check
suggested_followup: optional bounded task
```

Prefer primary and version-matched sources. A rerun of the same input is a reproduction check, not an
independent item of evidence.

### 5. Reconcile evidence

Deduplicate findings by evidence lineage, not wording. Preserve contradictions and minority objections.
Assess source quality, directness, reproducibility, independence, and applicability to the frozen target.
Do not average incompatible claims or promote a conclusion because several derivative reports agree.

For T2 scientific work, keep the required axes independent:

- claim relation: `SUPPORTS | CONTRADICTS | INCONCLUSIVE`;
- novelty: `REPRODUCTION | DISCOVERY_CANDIDATE`;
- fitting risk: `NULL_PASS | NUMEROLOGY_HOLD | NOT_APPLICABLE | NOT_ASSESSED`.

Apply null/multiplicity checks only when a valid null exists. Numerical Bayes requires explicit `H`,
`E`, a frozen prior, both likelihoods, and selection/dependence in those likelihoods. Lakatos applies
only at a declared programme/fiber checkpoint with a baseline and longitudinal window.

### 6. Synthesize for the decision

Return:

```yaml
answer: the narrowest evidence-supported answer
confidence_basis: why the evidence is sufficient or insufficient
supporting_findings: ids
contradicting_findings: ids
unknowns: unresolved items
decision_impact: action enabled, blocked, or unchanged
followups: bounded candidates, each independently scoped
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

One strong counterexample may outweigh broad agreement. `INCONCLUSIVE` is a valid outcome.

### 7. Act and verify only when authorized

Research does not itself authorize code, configuration, canon, or external-system changes. If the task
also requests implementation, make the smallest in-scope change and run checks relevant to that plane.
Record exact commands and observed outcomes. Do not claim external success from an internal return value.

## Discovery and follow-up

A discovery becomes a bounded follow-up candidate. Start it now only when it blocks the current decision
or the user explicitly requests it. Each child task gets its own tier, scope, budget, and completion
condition. The parent may complete after classifying its evidence and recording the candidate; there is
no automatic descendant chain.

## Optional pending proposal

Use only for material, reusable evidence:

```yaml
pending_id: proposed stable identifier
target: exact claim, artifact, or policy
target_fiber: algebra | physics | engineering | narrative | operations
finding_ids: provenance-bearing local findings
proposed_change: specific field-level change, if any
reason_reusable: recurrence, risk, or cross-repository value
ratifier_required: explicit authority or user decision
status: PENDING
```

Independent reproduction strengthens the evidence but does not self-ratify the proposal.

## Definition of done

- The question, scope, evidence bar, and budget were frozen.
- Sources and observations have exact provenance.
- Dependence, conflict, and uncertainty are visible.
- Counts were used only for coverage.
- The result is local unless it meets the pending threshold.
- No canonical mutation or recursive follow-up occurred without separate authorization.

## Method relationships

- `$prom` is the short explicit command route.
- `$jaebaeman` manages substantial independent subagent dispatch.
- `$taliban` performs formal adversarial validation when the decision needs it.
- `$apt` owns constructive implementation cycles.
- `$longinus` may verify code-to-claim references after an authorized change.

Historical v1–v6 automation, Cypher templates, seed crystallization, and count-based consensus rules remain
in Git history. They are not active instructions in v7.

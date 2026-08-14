---
name: apt-meta-review
kg_ref: ATOM_Skill_apt_meta_review
version: "28.0.0"
channel: stable
description: >-
  Run the terminal APT MetaReview phase after an approved SCW by classifying deltas, identifying evidenced reusable prevention, and returning a bounded local or pending handoff. Use when: the parent `$apt` orchestrator dispatches MetaReview after SCW or a user explicitly requests review of an APT cycle. Do not use when: a user wants general skill creation or an ordinary code review; use `$skill-creator` or direct review instead.
---

# APT MetaReview — bounded method review

MetaReview asks whether a completed APT cycle revealed a reusable method improvement. It is not a
mandatory Lesson factory, a KG writer, or a self-recursive validation loop.

## Entry contract

The parent supplies:

```yaml
cycle_id: stable local identifier
target: exact Span, artifact, or decision reviewed
inputs: specs, diffs, test outputs, and reviewer verdicts
completion_state: what SCW approved or left open
write_authority: files and systems this run may modify, if any
validation_budget: bounded checks and reviewers
```

If the evidence set is incomplete, return `INCONCLUSIVE` with missing inputs. Do not manufacture a root
cause or broaden the task to make the cycle appear complete.

## Workflow

### 1. Normalize observations

Record each material delta with provenance:

```yaml
observation_id: stable local identifier
expected: prior contract or behavior
observed: actual behavior
evidence: command, path, test, or external verdict
impact: local | reusable | high_risk | cross_repository
```

Success is not automatically a Lesson. Failure is not automatically a method defect.

### 2. Classify the causal state

For each material observation choose one:

- `NO_METHOD_CHANGE`: ordinary completion, local fix, or no reusable implication;
- `CAUSE_UNKNOWN`: the symptom is real but the cause is not established;
- `ROOT_CAUSE_EVIDENCED`: evidence isolates the cause;
- `PREVENTION_EVIDENCED`: the cause and a reusable prevention are both demonstrated.

Repeated occurrence or high risk raises persistence priority but does not prove causation.

### 3. Choose the smallest outcome

```yaml
outcome: LOCAL_REPORT | PENDING_VERDICT | PENDING_LESSON | PATCH_PROPOSAL
reason: concise evidence-based rationale
target: exact skill, method, or contract
evidence_ids: supporting observation ids
root_cause: required only for PENDING_LESSON
prevention: required only for PENDING_LESSON
unknowns: unresolved causal questions
```

- Use `LOCAL_REPORT` for ordinary cycle learning.
- Use `PENDING_VERDICT` when recurrence or risk matters but the cause is unresolved.
- Use `PENDING_LESSON` only when cause and reusable prevention are evidenced.
- Use `PATCH_PROPOSAL` when a specific authorized method change follows from the evidence.

No outcome directly changes KG status, confidence, configuration, canon, methodology slots, or
materialization links.

### 4. Apply a patch only when authorized

If the task explicitly authorizes a method or skill change and the parent owns the write boundary:

1. identify the exact contradictory instruction or missing guard;
2. make the smallest coherent patch;
3. preserve useful behavior and remove only the evidenced failure path;
4. validate frontmatter, references, formatting, and directly affected behavior;
5. record the observed checks in the local report.

Otherwise return the proposal without editing. A proposed patch is not authorization.

### 5. Request independent review only when material

Use an external reviewer when the patch affects a gate, safety boundary, shared contract, or canonical
policy. The executor does not impersonate the reviewer. Reviewer headcount is coverage metadata; one
evidence-backed blocker can block and unsupported agreement cannot approve.

### 6. Stop

MetaReview completes after the evidence is classified, any authorized patch is checked, and bounded
follow-ups are recorded. It never invokes itself. A follow-up is a separate task with its own scope and
tier.

## Persistence and ratification

The default output is a local report or parent handoff. Material reusable results may be returned as a
provenance-bearing `PENDING` proposal. Ratification requires an identified pending ID and an explicitly
authorized external ratifier/writer; independent reproduction alone cannot self-ratify.

## Output

```yaml
cycle_id: string
target: string
classification: NO_METHOD_CHANGE | CAUSE_UNKNOWN | ROOT_CAUSE_EVIDENCED | PREVENTION_EVIDENCED
outcome: LOCAL_REPORT | PENDING_VERDICT | PENDING_LESSON | PATCH_PROPOSAL
evidence: []
patches: []
checks: []
followups: []
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

## Definition of done

- Claims are tied to observed evidence.
- Root cause and prevention are present only when demonstrated.
- Relevant engineering checks ran for any code or skill patch.
- No direct KG/canon/config/status mutation occurred.
- No automatic recursion, sibling creation, or count-based decision occurred.

Historical automatic Lesson, Cypher, recursive self-gate, and composite count-gate procedures remain in
Git history. They are not active instructions in v28.

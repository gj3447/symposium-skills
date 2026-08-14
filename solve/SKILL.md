---
name: solve
kg_ref: ATOM_Skill_solve
version: "3.0.0"
channel: stable
provenance: AI_DERIVED_FROM_USER_PRIMARY
description: >-
  Run a bounded error-notebook resolution cycle that freezes a problem, inspects evidence, researches only when needed, plans and executes an authorized fix, verifies the outcome, and classifies persistence. Invoke when: the user calls `/solve <problem>` or requests a complete recorded remediation cycle. Do not use when: the request needs only research, adversarial audit, or forward implementation; use `$prometheus`, `$taliban`, or `$apt` instead.
---

# Solve — bounded remediation cycle

## 1. Freeze the problem

Create a local `ProblemRecord`:

```yaml
problem_id: stable local identifier
symptom: exact observed behavior
expected: intended behavior
target: artifact, revision, and environment
impact: affected users or systems
scope: included and excluded work
evidence: logs, commands, tests, or user verdict
authority: allowed files and external actions
done: observable completion condition
```

Do not label a symptom as a root cause before evidence establishes it.

## 2. Inspect before changing

Read repository rules, current state, relevant code/config, logs, and recent changes. Use read-only queries
first. Preserve foreign dirty state and resolve the exact target before any destructive action.

## 3. Research only when needed

Use `$prometheus` or bounded `$jaebaeman` subtasks when missing knowledge blocks diagnosis. Results return
to the local record with provenance and dependence. Do not automatically create ResearchFinding nodes or
expand every discovery.

## 4. Diagnose and plan

Separate:

- observation;
- candidate causes;
- discriminating checks;
- evidenced root cause, if found;
- smallest safe correction;
- rollback and validation.

If the cause remains unknown, keep it unknown and choose a safe diagnostic next step. A plan is local and
does not require an ActionPlan node.

## 5. Execute within authority

Make the smallest coherent authorized change. For TypeScript/Effect code, preserve the functional core /
Effect shell boundary, typed errors, Schema decoding, scoped resources, bounded concurrency, and one
composition root. Do not weaken types or tests to force success.

## 6. Verify

Run directly relevant checks, then broader checks in proportion to risk. Verify external effects by exact
readback rather than the producer's return value. Preserve negative and partial outcomes.

Use a formal `$taliban` review only when material risk or the task requires it; reviewer count is never an
approval vote.

## 7. Classify persistence

```yaml
outcome: FIXED | MITIGATED | NOT_REPRODUCED | BLOCKED | INCONCLUSIVE
root_cause_state: UNKNOWN | CANDIDATE | EVIDENCED
prevention_state: NONE | CANDIDATE | EVIDENCED
persistence: LOCAL_ONLY | PENDING_VERDICT | PENDING_LESSON
```

Ordinary results stay in the execution log/handoff. Repeated, high-risk, cross-repository, or reusable
evidence may become `PENDING`. A Lesson candidate requires both evidenced cause and reusable prevention.
Canonical mutation needs an identified pending ID and separate authorized ratification.

## Follow-up and done

Record discoveries as bounded candidates. Start one only if it blocks the requested resolution or the user
explicitly asks. The current cycle may finish after classifying its evidence; no automatic recursion,
sibling spawn, KG write, status change, or confidence update occurs.

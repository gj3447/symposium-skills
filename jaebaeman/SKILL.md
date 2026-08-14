---
name: jaebaeman
aliases: [SOP, subagent-orchestration-protocol]
kg_ref: ATOM_Skill_jaebaeman
version: "3.0.0"
channel: stable
provenance: AI_DERIVED_FROM_USER_PRIMARY
description: >-
  Coordinate parent-managed subagents through the bounded Pre-fetch→Plan→Dispatch→Collect→Classify protocol with explicit local task specs, permissions, provenance, cancellation, and output contracts. Invoke when: independent research, review, solve, or implementation subtasks can run concurrently and need structured collection. Do not use when: the task has no independent subtasks or needs only ordinary local planning; use direct handling instead.
---

# Jaebaeman — parent-managed subagent protocol

Jaebaeman is a protocol followed by the parent agent, not a persistent service or KG seed lifecycle. It
coordinates bounded independent work while keeping authority, integration, and final judgment with the
parent.

## Core invariants

- The parent owns scope, task decomposition, dispatch, collection, integration, and the final answer.
- Subagents are read-only by default. A write task must name an explicit narrower write-set and cannot
  override the repository's single-writer rule.
- One task spec represents one bounded deliverable with a clear completion condition.
- Dependencies, concurrency, retries, waits, and recursion are explicit and bounded.
- Agent and result counts are throughput/coverage telemetry, never votes for truth or priority.
- A failed or surprising result does not automatically spawn a sibling, retry, or descendant.
- Ordinary results remain in the local manifest or parent handoff.

## Local TaskSpec

Create specs in the parent context; do not persist them merely to dispatch work.

```yaml
task_id: stable local identifier
objective: one concrete deliverable
scope:
  included: exact artifacts, systems, or questions
  excluded: explicit non-goals
inputs: paths, revisions, prior receipts, and assumptions
dependencies: task ids that must complete first
permissions:
  mode: read_only | explicit_write
  write_set: []
tools: allowed or forbidden capabilities
output_contract:
  schema: required fields
  evidence: required provenance
completion_condition: observable definition of done
failure_policy:
  timeout: bounded duration
  retries: bounded count, normally zero
  partial_result: accept | reject | parent_decides
integration_owner: parent
```

Do not pass unsupported tool parameters or embed credentials. Resolve tool and model capabilities from
the active environment rather than copying historical API signatures.

## Protocol

### 1. Pre-fetch

The parent gathers shared context once: repository instructions, exact revisions, relevant local files,
read-only KG context when available, and already-known evidence. Supply only the subset each task needs.
Never make a child rediscover a policy the parent is required to enforce.

### 2. Plan

Create a dependency graph and dispatch only tasks that can make useful independent progress. Keep coupled
work with one owner. Identify shared-file collision risk before granting any write permission.

Good parallel tasks:

- separate source or platform audits;
- independent adversarial lenses;
- distinct modules with non-overlapping explicit write-sets;
- validation that does not mutate the implementation under review.

Poor parallel tasks:

- several agents editing the same file;
- a chain where each task needs the previous result;
- duplicate prompts used as majority voting;
- open-ended “keep researching” descendants.

### 3. Dispatch

Send the TaskSpec and relevant context. Use bounded concurrency chosen for workload and resource limits.
The parent remains responsive, tracks task IDs, and can cancel work that becomes irrelevant. Do not use
unbounded fan-out or detached work with no owner.

For explicit write tasks:

1. verify the parent has authority;
2. give one owner a disjoint exact write-set;
3. require the child to preserve foreign dirty state;
4. integrate and validate centrally;
5. revoke the write grant when the task ends.

### 4. Collect

Validate every result against its output contract. A useful result includes:

```yaml
task_id: string
status: COMPLETE | PARTIAL | BLOCKED | FAILED | CANCELLED
summary: concise outcome
evidence: exact paths, commands, sources, or observations
changes: exact files or external records changed, normally none
checks: commands and observed results
uncertainty: limitations and unresolved questions
followups: bounded candidates
```

Record timeout, cancellation, invalid output, and missing evidence explicitly. Do not silently convert a
partial result into success.

### 5. Classify and integrate

The parent deduplicates shared evidence, preserves contradictions, and distinguishes independent results
from derivative ones. Integrate by evidence quality and applicability, not agent count. One supported
blocker may control a decision; many unsupported reports do not.

Return a local manifest:

```yaml
cycle_id: stable local identifier
tasks: []
completed: []
partial_or_failed: []
evidence_lineage: []
conflicts: []
integration_decision: concise parent judgment
followups: bounded candidates
persistence: LOCAL_ONLY | PENDING_PROPOSAL
```

## Failure and cancellation

- Retry only when the failure is classified as transient and the bounded retry was declared.
- On partial failure, stop or continue according to the TaskSpec; never invent missing results.
- Cancel descendants when their prerequisite fails or the parent decision is already resolved.
- If an external write may have an unknown outcome, reconcile with exact readback before retrying.
- Compensation is an explicit in-scope action, not arbitrary stored code or automatic Cypher.

## Persistence boundary

The default is `LOCAL_ONLY`. A repeated, high-risk, cross-repository, or reusable result may become a
provenance-bearing `PENDING` proposal. Do not directly create or mutate a Lesson, ValidationResult,
ActionPlan, seed, status, confidence, configuration, canon, or supersession. Ratification requires an
identified pending record and a separately authorized ratifier/writer.

A repeated failure can justify a pending verdict or handoff. Create a RootCause or Lesson candidate only
when evidence establishes both cause and reusable prevention; do not invent them to close the cycle.

## Follow-up boundary

Record discoveries as bounded candidates. Start a child only when it blocks the current task or the user
explicitly requests it. The parent may complete after classifying the current evidence. Any new child has
its own TaskSpec, permissions, budget, and completion condition; there is no automatic fractal growth.

## Definition of done

- Every dispatched task had an explicit objective, scope, permissions, output contract, and bound.
- Shared context was prefetched and write ownership was unambiguous.
- Results were schema-checked and evidence lineage is visible.
- Partial failures and dissent were preserved.
- Integration used evidence rather than counts.
- No unbounded retry, recursion, automatic sibling creation, or unauthorized persistence occurred.

## Consumers

Prometheus, Naesengmoon, APT, Solve, and TPA may use this protocol. Each consumer owns its domain rules;
Jaebaeman supplies orchestration only and does not duplicate their logic.

Historical v1–v2 KG seed schemas, lifecycle triggers, status writes, compensation Cypher, automatic
fractal spawning, and fixed tool signatures remain in Git history. They are not active instructions in
v3.

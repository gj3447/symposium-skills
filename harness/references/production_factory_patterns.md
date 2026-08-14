# Production factory patterns — Harness L_RT reference

This reference supplies optional runtime-team recipes for [`../SKILL.md`](../SKILL.md). Patterns are chosen
by dependency, risk, and evidence needs; they are not mandatory phases or agent-count prescriptions.

## Team pattern × orchestration model

| Team pattern | Use when | Common control-flow form |
|---|---|---|
| Pipeline | outputs have strict sequential dependencies | linear graph/chain |
| Fan-out/fan-in | independent work can be reconciled centrally | bounded parallel branches + join |
| Expert pool | different concerns require different specialists | supervisor/router |
| Producer-reviewer | material output needs independent checking | produce then evidence-based review |
| Supervisor | central owner must allocate dynamic work | bounded manager/work queue |
| Hierarchical delegation | a large scoped task has owned subtrees | bounded child graph |

The model/pattern pair is a design choice, not a truth claim. Keep concurrency, queues, retries, waits, and
descendants bounded. Counts are throughput/coverage telemetry.

## Boundary-cross QA

QA checks both sides of an interface: for example an API response and its client decoder, a schema and its
serialized payload, or a claim and the exact referenced code. Verify incrementally when failure would make
later work wasteful. Use an independent reviewer only when material risk or policy calls for it.

## Trigger validation

Skill routing descriptions should be tested with a small representative set of:

- positive prompts that clearly require the skill;
- near-miss prompts that should route elsewhere;
- ambiguous prompts whose explicit alternate route exposes the boundary.

Choose the smallest set that exercises materially different boundaries. Do not require 16–20 cases, create
a TriggerValidationSuite node, or backfill every skill automatically. Keep results local unless the routing
defect is repeated/high-risk/reusable, then return a `PENDING` proposal.

## Intermediate artifacts

Use a task-local artifact directory only when intermediate evidence aids audit/resume. Name files by phase,
owner, and purpose; avoid overwriting prior evidence. Repository conventions and user paths take precedence
over a universal `_workspace/` layout.

## Evolution signals

Repeated feedback, repeated validated failure, or observed routing bypass may justify a bounded method
review. These are investigation signals, not causal proof or automatic triggers.

1. record the original verdict and provenance locally;
2. determine whether the issue is repeated, high-risk, cross-repository, or reusable;
3. isolate root cause and demonstrate reusable prevention if possible;
4. return `LOCAL_ONLY`, `PENDING_VERDICT`, `PENDING_LESSON`, or `PATCH_PROPOSAL`;
5. start MetaReview/Naesengmoon only when material to the current decision or explicitly requested.

A repeat count does not establish cause. Do not automatically create a Lesson, patch a skill, write KG,
alter status/confidence/configuration, or recurse.

## Harness invariants

- intent, scope, permissions, and stop conditions are explicit;
- producer and reviewer independence is visible when required;
- direct checks cross the claimed boundary;
- partial failure and dissent are preserved;
- local artifacts are default;
- canonical persistence requires qualified `PENDING` evidence and separate authorized ratification.

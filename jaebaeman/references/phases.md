# Jaebaeman phases

The authoritative protocol is [`../SKILL.md`](../SKILL.md).

## Phase 1 — Pre-fetch and plan

The parent reads repository rules, exact revisions, shared evidence, and tool capabilities. It then creates
one bounded local TaskSpec per independent deliverable, with read-only permissions by default. Coupled work
and overlapping writes stay with one owner.

## Phase 2 — Dispatch

Dispatch independent tasks concurrently when the active tool supports it. A single orchestration turn may
contain multiple independent tool calls; do not serialize them through a loop merely to imitate parallel
work. Use the runtime's actual tool schema and pass no unsupported historical parameters.

Concurrency, timeout, cancellation, and retry limits are explicit. The parent retains ownership and stays
available to cancel irrelevant work.

## Phase 3 — Collect

Validate each result against its output contract. Record `COMPLETE`, `PARTIAL`, `BLOCKED`, `FAILED`, or
`CANCELLED`, plus evidence, changes, checks, uncertainty, and bounded follow-ups.

## Phase 4 — Classify and integrate

Deduplicate shared evidence, preserve conflicts, and integrate by quality and applicability rather than
agent count. Return a local manifest. Material reusable evidence may become a `PENDING` proposal; no
status, seed, ActionPlan, Lesson, or KG write occurs automatically.

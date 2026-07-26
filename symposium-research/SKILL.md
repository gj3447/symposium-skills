---
name: symposium-research
description: >-
  Route repository-specific research inside SYMPOSIUM and PI through the correct canon, specialist skills, agents, evidence gates, and artifact nest. Use when: handling PI experiments, internal engineering research, mythology or canon study, paper preparation, cross-layer synthesis, interrupted research, or crystallization in this repository. Do not use when: the request is ordinary scoped implementation or debugging with no research, canon, or artifact-routing question; use direct handling instead.
---

# SYMPOSIUM Research

Use one thin router to activate the heavy methods only when the task measures a
need for them. Do not compile a fixed commander chain.

## 1. Establish the research contract

Read the nearest `AGENTS.md`, then classify the task into one or more lanes:

- `PI`: experiments and engineering under `PI/`;
- `MYTH_CANON`: user-primary material under `METAHUMOTONIC/` or `MIND/metahumotonic/`;
- `ENGINEERING`: methods, engines, FSMs, Harnesses, and tooling under `THEORY/` or `SKILLS/`;
- `PAPER`: submission-ready analysis under `PAPERS/<paper_slug>/`;
- `BRIDGE`: an explicit connection between myth, formal material, engineering, or a paper.

State the question, target lane, requested artifact, acceptance evidence, and
write scope. Keep sourcebooks and manuscripts separate.

## 2. Resolve authority before interpretation

Check KG canon first when its read surface is available, then local user-primary
and formal sources, then engineering skill canon. If KG is unavailable, report
that once and continue from local canon. Treat user speech as canonical and AI
synthesis as secondary until ratified. Do not close an open canon question for
the sake of a tidy report.

Use `$prometheus` or the `prometheus_expert` agent only when the task has a real
knowledge gap, needs external evidence, or requests PROM. Technical web research
uses primary sources. Record source path or URL, retrieval time where relevant,
claim supported, caveat, and confidence.

## 3. Dispatch by measured need

Read [references/routing.md](references/routing.md), then select the smallest
useful combination:

- PI coordination or code work: `pi_research_engineer` plus `$pi-workbench`;
- executable behavior evidence: `$ooptdd-receipt`;
- independent progress judgment: `progress_judge` plus `$lakatotree-judge`;
- a new engine, FSM, or bounded agent loop: `engine_systems_designer` with
  `$engine-design`, `$fsm-design`, and `$loop-engineering` as applicable;
- Harness classification or four-axis diagnosis: `$harness` or
  `harness_diagnostician`;
- forward design-to-code crystallization: `$apt` or `apt_orchestrator`;
- reverse engineering/design recovery: `$tpa` or `tpa_orchestrator`;
- source/KG/hash drift or binding work: `$longinus` or
  `longinus_reference_linker`;
- heavy computation: `$compute-offload` after fleet headroom checks.

When the collaboration tool exposes `agent_type`, pass the specialist's exact
snake-case name in that field and use a separate descriptive `task_name`.
`task_name` alone creates a generic child. On a surface without `agent_type`,
embed the selected role contract and skills in the child message and label the
fallback honestly.

Naesengmoon is user-explicit adversarial validation. Ordinary research, PROM,
or implementation does not authorize it automatically. KG writes, publication,
messages, deployment, and destructive cleanup also require their own authority.

## 4. Parallelize bounded independent work

With a four-thread cap, keep the root as collector and use at most three direct
children at once. Give every child a bounded question, input paths, required
output fields, evidence standard, and explicit non-goals. Prefer read-only axes
in parallel. Parallel children remain read-only. When mutation is required, one
root/parent session performs it sequentially on canonical `main` under the
repository writer token. Do not create parallel writers, session branches,
linked worktrees, or OMD leases.

The parent collects all results, checks required fields, deduplicates repeated
claims, preserves conflicts, and decides the next dispatch. A child never writes
KG canon or declares the whole research cycle complete on the parent's behalf.

## 5. Close with evidence, not activity

Return:

1. question and lane;
2. authority sources and unavailable sources;
3. findings with evidence, caveats, alternatives, and confidence;
4. artifacts and exact paths;
5. commands, tests, receipts, or judge output actually run;
6. unresolved questions and the next falsifier.

For PI completion or progress claims, activity and a passing local test are not
enough: require the single-writer plus two-evidence-layer `$pi-workbench` contract.

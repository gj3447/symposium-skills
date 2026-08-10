---
name: engine-design
description: >-
  Design or review a reusable software engine boundary, deterministic kernel, command-event-effect protocol, ports, persistence, concurrency, failure model, and verification. Use when: creating an engine, runtime, scheduler, orchestration core, reusable subsystem, or deciding whether a capability should become an engine. Do not use when: the task is a one-off feature or only detailed lifecycle or agent-loop behavior is in scope; use direct implementation, `$fsm-design`, or `$loop-engineering` instead.
---

# Engine Design

Turn a capability into the smallest reusable mechanism that can own it without absorbing product policy. Produce contracts and falsifiers before implementation.

## Workflow

### 1. Prove that an engine is warranted

Collect concrete evidence of reuse pressure, determinism, isolation, durability, scheduling, or replaceable implementations. Name the actual consumers.

Keep the capability as an ordinary module when it has one call path, unstable semantics, or mostly product policy. Do not create an engine merely to make a directory look architectural.

If the verdict is `module` or `defer`, stop the engine workflow here. Produce a short rejection ADR with the pure module contract, current versus planned consumers, promotion gates, and falsifiers. Start from [assets/module-decision.example.json](assets/module-decision.example.json) and validate it with the same script. Do not manufacture commands, events, persistence, or migration for a boundary that does not need them.

### 2. Establish authority and scope

- Read repository instructions, existing contracts, and local canon before proposing a new abstraction.
- Distinguish user-primary decisions, accepted project canon, external standards, and preliminary AI proposals.
- Write one sentence each for purpose, owned mechanism, excluded policy, and non-goals.
- For agent infrastructure, classify the boundary as `L_IDE`, `L_RT`, or `L_MC`; do not collapse the Harness family into one product.

### 3. Specify the kernel

Define:

- resources and work units;
- commands accepted by the engine;
- facts/events emitted after accepted changes;
- effects requested from the environment;
- invariants that every accepted transition preserves;
- the single authority for mutable state.

Prefer a pure deterministic kernel:

```text
decide(state, command) -> events | rejection
evolve(state, event) -> state
effects(events) -> effect requests
```

Keep clock, randomness, network, filesystem, model calls, and credentials behind ports. Record their returned values before replaying decisions.

Separate five planes when the engine is operationally substantial:

- domain core: immutable state, commands, facts, guards, and invariants;
- data plane: versioned ingress, routing, bounded queues, and admission;
- state plane: journal/snapshot, transactional dedup inbox, outbox, and views;
- control plane: versioned policy, quotas, ownership, rollout, and repair;
- effects shell: injected environmental ports and telemetry.

### 4. Design the narrow waist

- Keep the public protocol smaller than any adapter.
- Separate mechanism from policy and ports from adapters.
- Version commands, events, snapshots, and externally stored data.
- Use a registry or intermediate representation only when multiple implementations truly need one.
- Make capabilities explicit; reject ambient authority.
- State ownership, concurrency, ordering, backpressure, cancellation, and timeout rules.
- Enforce security-domain non-interference: private traffic, counters, indexes, and telemetry must not alter shared decisions.

When lifecycle behavior has several states or forbidden transitions, invoke `$fsm-design`. Use orthogonal machines instead of one product-state enum when dimensions change independently.

### 5. Design failure and recovery

- Enumerate invalid input, invariant violation, transient dependency failure, permanent rejection, cancellation, timeout, overload, and incompatible-version behavior.
- Separate checkpointing from durable execution. State what is replayable and what is not.
- Give every external effect an idempotency key or an explicit at-most-once compromise.
- Couple dedup claim, accepted events/state version, and outbox intent atomically when durability is promised.
- Retry only classified transient failures, with a bound and observable exhaustion state.
- Make migrations and rollback paths explicit.

### 6. Make it observable and testable

Require correlation IDs, command/event/effect traces, latency and queue metrics, rejection reasons, and redaction rules. Test the pure kernel with tables or properties, adapters with contract tests, recovery with crash injection, and concurrency with race/backpressure tests.

Implement as vertical slices: one consumer, one command, one event, one adapter, one recovery path. Expand only after the seam survives use.

## Required deliverables

For a `module` or `defer` verdict, produce only the decision record, pure contract, boundary/non-goals, current and planned consumers, invariants, failure/verification plan, promotion gates, and falsifiers.

For an `engine` verdict, produce:

Produce:

1. decision record: why an engine and why now;
2. context and ownership boundary;
3. mechanism/policy split and non-goals;
4. command, event, effect, port, and version contracts;
5. state/FSM model and invariants;
6. concurrency, persistence, recovery, and migration model;
7. failure taxonomy, observability, security capabilities, and test plan;
8. incremental implementation slices and explicit falsifiers.

Start from [assets/engine-spec.example.json](assets/engine-spec.example.json), then run either decision profile with:

```bash
python3 scripts/validate_engine_spec.py path/to/engine-design.json
```

Read [references/engine-standard.md](references/engine-standard.md) for the design checklist and source provenance. Read [references/symposium-cases.md](references/symposium-cases.md) before reusing local APT or EngineBoy designs; it preserves their canon status.

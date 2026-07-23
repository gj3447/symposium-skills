# Engine design standard

Use this reference after the workflow in `SKILL.md`; it is a checklist, not a reason to create an engine.

## Boundary laws

1. The engine owns a stable mechanism. Consumers own product policy.
2. One mutable fact has one authoritative writer. Read models may be many.
3. The public protocol is a narrow waist: smaller and more stable than adapters.
4. Environmental nondeterminism enters through ports and becomes recorded input before replay.
5. Accepted state change is expressed as facts/events. External work is an effect, not a hidden mutation inside the reducer.
6. Every durable schema has an explicit compatibility and migration policy.
7. Every queue has capacity and backpressure behavior. Every wait has cancellation and timeout behavior.
8. Every privileged operation requires an explicit capability.
9. A duplicate identity with different intent is a conflict, not a successful retry.
10. Traffic or state from one security domain cannot influence another domain unless an explicit aggregate contract permits it.
11. Inactive work that must decay, expire, or retry has an explicit scheduled event; lazy reads are not a liveness guarantee.

## Review questions

- Which concrete consumers force reuse now?
- What code becomes simpler if this boundary exists?
- Which policy can change without changing the engine?
- What is the smallest trusted core?
- Can the decision kernel run without I/O, wall clock, randomness, credentials, or model calls?
- Can a command be retried safely? Can an event be replayed safely? Can an effect be deduplicated?
- Are dedup claim, state/event commit, and outbox intent atomic, or is the weaker failure behavior explicit?
- How is overload visible to the caller?
- Which recovery promise is actually tested?
- Can arbitrary private-domain traffic change a shared rank, score, capacity decision, or cache residency?
- What evidence would prove the abstraction premature?

## Source basis

- Local synthesis: `THEORY/engine_os_design/PROM_16_REPORT.md` — mechanism/policy separation, small-OS analogy, scheduler/indirection/isolation, narrow waist, single writer, capabilities, backpressure, and the warning against premature engineization.
- Local design proposal: `THEORY/APT/vnext/APT_ENGINE_FSM_DESIGN_2026-07-13.md` — pure kernel, command/event/effect separation, ports/outbox, versioned event store, derived phase projection. It is a proposal, not automatically production canon.
- Event envelope vocabulary: CloudEvents specification, <https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md>. CloudEvents standardizes occurrence data plus contextual attributes; adopting its entire wire format is optional.
- Durable execution comparison: Temporal Workflow Execution documentation, <https://docs.temporal.io/workflow-execution>. Use it to distinguish replayable durable workflow guarantees from ordinary checkpoints.
- Backpressure baseline: Reactive Streams specification, <https://www.reactive-streams.org/>. Apply demand/bounded-mailbox semantics at asynchronous boundaries; keep the domain reducer synchronous.
- Retry identity: AWS Builders' Library, <https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/>. Couple an idempotency token to the mutation and detect same-key/different-intent requests.
- Event evolution: Protocol Buffers compatibility guidance, <https://protobuf.dev/best-practices/dos-donts/>. Retain field identity and old-event fixtures; use an explicit upcaster boundary where necessary.

The rules above are SYMPOSIUM synthesis. External sources support constituent mechanisms; they do not define a universal “engine architecture standard.”

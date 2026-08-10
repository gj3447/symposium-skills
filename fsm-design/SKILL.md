---
name: fsm-design
description: >-
  Design, review, and verify finite-state machines or hierarchical and orthogonal statecharts from a machine-readable semantic source, including events, guards, timers, recovery, safety, and conformance tests. Use when: lifecycle protocols, controllers, parsers, device or UI modes, forbidden transitions, or enum-and-if drift require explicit state semantics. Do not use when: the target is a static schema or only an outer agent retry and checkpoint loop; use direct contract design or `$loop-engineering` instead.
---

# FSM Design

Fix execution semantics before drawing the diagram. Treat diagrams as generated views of a versioned machine contract.

The bundled `fsm-spec/v1` is a machine-readable semantic contract, not a runtime or guard language. Bind every named guard and effect to typed implementation functions, type-check event-to-effect payload bindings, and prove that the production `step` function conforms to the contract before calling the machine executable.

## 1. Select the right formalism

- Use a flat DFA for recognition or admissibility.
- Use Moore semantics when output belongs to a stable state.
- Use Mealy semantics when output belongs to a transition.
- Add hierarchy only for genuinely shared behavior or defaults.
- Add orthogonal regions only for independently changing concerns that are simultaneously active.
- Prefer a decision table, DAG/workflow, Petri net, timed/hybrid automaton, or planner when rules, acyclic flow, resource synchronization, continuous time, or optimization is the real problem.

Record why an FSM is the smallest honest model.

## 2. Define the semantic contract

Specify:

```text
step(configuration, event) -> (next_configuration, commands)
```

The configuration includes active state(s) and bounded extended context. Define:

- initial, atomic, compound, parallel, history, and final semantics actually supported;
- event names and payload schemas;
- external and internal event queue ordering;
- run-to-completion or other step boundary;
- trigger matching, guard evaluation, priority, and conflict resolution;
- exit, transition, and entry action order;
- explicit behavior for every unsupported event: ignore, reject/audit, error, or defer;
- timers, cancellation, and failure events.

Guards must be pure and synchronous. Emit commands/effect intents after transition selection; do not hide network, filesystem, clock, random, model, or credential access inside a guard or reducer.

A `TIMEOUT` transition must use a `kind: deadline` guard whose declared deadline context field and observed event field are both typed timestamps and are actually read by the guard. Delivery of an event named `TIMEOUT` is not proof that its deadline is due.

Define whether a known event whose guard is false is rejected/audited, ignored, deferred, or handled by a lower-priority default. It is not automatically the same case as an unknown or disabled event.

## 3. Control complexity

- Separate state from extended data. Do not encode every data value as a state.
- Use multiple orthogonal machines when dimensions change independently; define the global product configuration and cross-region invariants anyway.
- Coordinate regions with explicit events. Avoid direct cross-region transitions.
- Remember that logical parallel regions are not threads and do not erase Cartesian reachability cost.
- Bound or abstract extended context before claiming the model is finite.

## 4. Make determinism and completeness explicit

For each configuration/event class, require one observable result. Make guards mutually exclusive or give them an explicit stable priority and documented default. Define unmatched-event behavior rather than inheriting an accidental wildcard.

Separate:

- determinism: no ambiguous observable outcome;
- completeness: every relevant input class has transition, ignore, reject, or defer behavior;
- safety: forbidden things never happen;
- liveness: desired progress eventually happens under stated timeout and fairness assumptions.

## 5. Verify before implementation

Run these gates:

1. schema, duplicate ID, target, initial, and event validation;
2. ambiguity, priority, terminal isolation, and eventless-cycle checks;
3. state/transition reachability and dead-state analysis;
4. positive, boundary, invalid, duplicate, reordered, timeout, and concurrent traces;
5. property-based action-sequence tests with shrinking;
6. model-to-implementation conformance tests;
7. temporal model checking for critical bounded safety/liveness claims.

Generate transition tables, Mermaid/SVG, test vectors, and coverage from the semantic source. Never patch a generated diagram as the source of truth.

Handoff rule: when `$loop-engineering` invokes this skill, return the crystallized machine and conformance obligations to the caller. Do not mechanically reinvoke `$loop-engineering`; that would form a skill-selection cycle.

## Required artifacts

Start from [assets/fsm-spec.example.json](assets/fsm-spec.example.json). Include the machine source, transition table, properties, trace fixtures, generated diagram, and verification report. Validate the source with:

```bash
python3 scripts/validate_fsm.py path/to/fsm-spec.json
```

Run the bundled abstract trace profile before binding production code:

```bash
python3 scripts/run_fsm_traces.py path/to/fsm-spec.json path/to/fsm-traces.json
```

The runner fails unless each declared transition is selected, every declared guard is exercised false, and each machine's invalid-event policy is exercised at least once.

Read [references/fsm-standard.md](references/fsm-standard.md) for the standards crosswalk and [references/testing.md](references/testing.md) for the verification profile. For an agent execution controller, invoke `$loop-engineering` after the state semantics are stable.

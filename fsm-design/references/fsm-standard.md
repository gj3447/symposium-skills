# FSM and statechart standards crosswalk

## Semantic baselines

- NIST's finite-state-machine references give the basic state, start-state, alphabet, and transition-function vocabulary and distinguish determinism from completeness: <https://xlinux.nist.gov/dads/HTML/finiteStateMachine.html> and <https://xlinux.nist.gov/dads/HTML/determFinitStateMach.html>.
- W3C SCXML 1.0 is the normative executable statechart baseline for hierarchy, parallel regions, legal configurations, event processing, transition selection, and exit/transition/entry ordering: <https://www.w3.org/TR/scxml/>.
- OMG UML 2.5.1 defines behavioral state machines for UML interoperability: <https://www.omg.org/spec/UML/2.5.1>. Use PSSM 1.0 when precise UML execution semantics and its test suite matter: <https://www.omg.org/spec/PSSM/1.0>.
- Erlang/OTP `gen_statem` is a current production reference for event-driven state machines, transition actions, state entry, postponement, and multiple timeout classes: <https://www.erlang.org/doc/system/statem.html>.

## Repository profile

The `fsm-spec/v1` JSON profile is intentionally smaller than SCXML or UML. It defines multiple flat machines as orthogonal regions, an explicit invalid-event policy, ordered guarded choices, pure transition decisions, effect commands, safety/liveness statements, and static validation. Escalate to SCXML when nested/history/parallel execution semantics or portable interchange are required. Do not pretend the small profile implements constructs it omits.

The local `SKILLS/_common/contract_lifecycle_fsm.md` contributes repository invariants: explicit events, terminal isolation, no silent transitions, and creator/reviewer separation. The EngineBoy Activity/Validity/Visibility split is a useful but `PRELIMINARY` and verdict-pending case, not ratified universal canon.

## Interpretation rules

1. Orthogonal regions mean simultaneously active logical regions, not one thread per region.
2. A priority rule can make a machine deterministic while hiding overlapping guards; test exclusivity as a correctness property.
3. An unmatched event policy is part of the public protocol. Security-sensitive inputs should reject and audit.
4. Eventless cycles are invalid unless the chosen execution semantics prove macrostep termination.
5. Diagrams are views. The executable or machine-readable semantic source is authoritative.
6. Extended context can make the effective state space infinite. State the abstraction and bounds used by tests or model checking.

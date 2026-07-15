# FSM verification profile

## Static gates

- unique state, transition, machine, and event identifiers;
- valid initial and target states;
- stable conflict resolution for competing transitions;
- explicit unmatched-event behavior;
- terminal states with no outgoing transitions;
- no nonterminating eventless strongly connected component;
- reachable states and transitions, with every intentional dead state justified.

## Trace suites

For every transition, include a positive trace and a guard-boundary trace. Add invalid, duplicate, reordered, delayed, timeout, cancellation, and restart traces. For orthogonal regions, permute independent event order and assert global invariants after every step.

## Generative verification

Use model-based or stateful property testing to generate event sequences, compare model and implementation, check invariants after every step, and shrink failures. Hypothesis documents this pattern for Python: <https://hypothesis.readthedocs.io/en/latest/stateful.html>.

## Formal verification

State safety and liveness separately. For a critical bounded model, translate the semantic source to a model checker and record environment/fairness assumptions. A proof covers the abstraction and assumptions, not uncontrolled services or omitted data domains.

## Coverage report

Report state, transition, event, guard outcome, invalid-event, and terminal-path coverage. Coverage is evidence of exercised model elements, not proof of correctness.

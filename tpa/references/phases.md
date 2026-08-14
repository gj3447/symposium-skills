# TPA phase contracts

- **TCW** inventories the exact code world with parser/AST evidence and visible exclusions.
- **ST** recovers explicit and conventional contracts with code-level provenance.
- **SP** tests pattern/architecture hypotheses, counterevidence, and alternatives.
- **TA** proposes an anchor and bindings, then audits drift with a frozen denominator.

Each phase returns `COMPLETE`, `PARTIAL`, `RETURN`, `BLOCKED`, or `INCONCLUSIVE`. A phase does not create
or mutate persistent nodes, status, seeds, Lessons, ActionPlans, or the next phase. The parent routes from
actual artifacts and starts any child as a separate bounded invocation.

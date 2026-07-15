# SYMPOSIUM case-status guard

Do not flatten these artifacts into one authority layer.

| Artifact | Status for this skill | Safe use |
|---|---|---|
| `THEORY/engine_os_design/PROM_16_REPORT.md` | Research synthesis | Design heuristics with cited provenance |
| `THEORY/APT/vnext/APT_ENGINE_FSM_DESIGN_2026-07-13.md` | APT engine proposal | Candidate architecture and vocabulary; verify current acceptance before implementation |
| `METAHUMOTONIC/ORBITAL_MOTION_CLOUD/engineboy/EMERGENCE_ENGINE_FSM_DESIGN_PRELIMINARY_2026-07-13.md` | `PRELIMINARY` / `VerdictPending`, AI-authored | Case study for three orthogonal FSMs only; never present as ratified user canon |
| EngineBoy traffic-weighted hierarchy parent decision | User-source parent context | Re-check its exact current wording before deriving a new engine decision |

The EngineBoy case separates Activity, Validity, and Visibility machines to avoid a 36-state Cartesian product. Reuse the *technique* only after proving those dimensions are independently authoritative in the target. Do not copy its state names as a universal taxonomy.

As inspected on 2026-07-15, the implementation remains an Alpha research prototype: the deterministic reducer/Hawkes core is valuable, but durable dedup, atomic state-plus-outbox commit, recovery, enforced single-writer/version conflicts, bounded ingress, schema evolution, full telemetry, and several liveness/non-interference cases remain outside the proved contract. Re-inspect the current code and tests rather than treating this dated audit as live truth.

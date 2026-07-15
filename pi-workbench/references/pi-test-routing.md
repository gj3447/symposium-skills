# PI test and evidence routing

Always prefer the target repository's current nested instructions when they
conflict with this snapshot.

| Target | Narrow verification route |
|---|---|
| `PI/omd` | `make verify`; add TLA+/Hypothesis checks when the changed contract touches them |
| `PI/ooptdd` | `UV_CACHE_DIR=$PWD/.uv-cache uv run --extra dev pytest -q` |
| `PI/ooptdd-loop` | `.venv/bin/python -m pytest -q`; full harness: `scripts/verify_ooptdd.sh` |
| `PI/lakatotree` | `.venv/bin/python -m pytest -q`; after core definition-line changes add `.venv/bin/python -m lakatos.longinus audit` |
| `PI/apt-engine` | `PYTHONPATH=src python3 -m pytest -q` |
| `PI/tpa-engine` | target pytest/ruff checks plus `tpa-engine check ... --max-cycles 0` where applicable |
| `PI/bhgman_tool` | narrow relevant tests first, then `uv run --all-extras pytest -q` for shared engine/CLI behavior |
| `PI/p333` | Rust tests in its declared container plus `sh verify/run_gates.sh` |

Some legacy scripts contain Dell/DGX absolute paths. Inspect them before use and
do not advertise them as portable Mac commands without proving that route.

## Required separation

```text
OMD coordinator/implementer
        -> immutable executable receipt
        -> independent LakatoTree judge
```

The implementer may propose a preregistration or spec before execution. It may
not alter either after seeing the result merely to obtain green.

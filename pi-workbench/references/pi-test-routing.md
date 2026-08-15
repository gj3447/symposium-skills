# PI test and evidence routing

Always prefer the target repository's current nested instructions when they
conflict with this snapshot.

| Target | Narrow verification route |
|---|---|
| `PI/apt-engine` | `PYTHONPATH=src python3 -m pytest -q` |
| `PI/tpa-engine` | target pytest/ruff checks plus `tpa-engine check ... --max-cycles 0` where applicable |
| `PI/bhgman_tool` | narrow relevant tests first, then `uv run --all-extras pytest -q` for shared engine/CLI behavior |
| `PI/p333` | Rust tests in its declared container plus `sh verify/run_gates.sh` |
| Any other PI target | Read its nearest instructions and run the narrowest direct test or probe that exercises the changed path |

Some legacy scripts contain Dell/DGX absolute paths. Inspect them before use and
do not advertise them as portable Mac commands without proving that route.

## Evidence boundary

```text
implementation
        -> direct execution record
        -> interpretation kept separate from measurements
```

The implementer may state a prediction or spec before execution. It must not
alter either after seeing the result merely to obtain a preferred conclusion.

---
name: pi-workbench
description: >-
  Coordinate PI research and engineering through its three-layer contract:
  OMD write-set leases, executable ooptdd/LTDD measurement, and deterministic
  LakatoTree judgment. Use for any task under PI/, its symlinked repositories,
  EngineBoy measurement work, or a claim that a PI implementation or research
  programme made progress.
---

# PI Workbench

Treat coordination, measurement, and judgment as separate authorities. A Codex
subagent does not replace the cross-session OMD lease, and an implementer does
not grade its own result.

## 1. Resolve the target

Read `PI/AGENTS.md` and the target repository's own instructions. Resolve every
symlink and record `git rev-parse --show-toplevel`. If the imported snapshot has
no usable Git repository, keep it reference-only or work in an authorized fresh
clone; do not pretend it can be pushed.

Choose the narrowest repo-specific test route from
[references/pi-test-routing.md](references/pi-test-routing.md).

## 2. Coordinate every shared write with OMD

For a mutating task, use stable `task` and `agent` identifiers and repo-qualified
paths. Call `declare`, then `claim`, and edit only when every required orbit is
`HELD`. Immediately heartbeat the agent and renew during long work. `PENDING`,
`DENIED`, or an unavailable OMD surface means the pass remains read-only.

Edit only claimed paths. On completion release each orbit using its exact fence,
then cancel the lease-only task so it does not stay pending. Preserve unrelated
dirty files and use explicit pathspecs for commits.

## 3. Measure behavior through real code

For a behavior change, invoke `$ooptdd-receipt` before calling the work complete.
Lock the expectation before the satisfying run, execute the real code path, read
the evidence back, and inject a negative that makes the same gate fail. A mock
that bypasses the changed path, a hand-written receipt, or `ship()` without
readback is not evidence.

Keep `inconclusive` distinct from failure and success. Use direct numeric,
security, concurrency, or territory probes where logs are not a valid oracle.

## 4. Judge progress independently

If the claim is scientific or programme progress, invoke `$lakatotree-judge` and
the `progress_judge` agent after the evidence is frozen. The implementer and
judge identities must differ. Preregister the prediction and kill condition
before measurement, pass grounded evidence without a verdict, and accept only a
verdict computed by the declared judge/harness. Never type a verdict into the
evidence record.

Naesengmoon remains a separate, user-explicit adversarial review; it is not the
LakatoTree scoring engine.

## 5. Offload only when justified

Use `$compute-offload` for heavy jobs. Check `PI/dt.sh headroom`, retain production
CPU/memory/GPU/IO guards, and return hashes/manifests with artifacts. The DGX
cold-storage path is neither the default compute target nor a backup.

## Completion packet

Copy [assets/pi-cycle.example.json](assets/pi-cycle.example.json), replace every
placeholder from actual output, and set `template_only` to `false`. The bundled
example itself is only a schema fixture and can be checked with `--template`:

```bash
python3 scripts/validate_pi_cycle.py assets/pi-cycle.example.json --template
python3 scripts/validate_pi_cycle.py path/to/pi-cycle.json --verify-linked --root /absolute/repo/root
```

Report the OMD task/orbit/fence, changed paths, correlation ID, positive and
negative receipts, exact test commands, independent judge command/result,
provenance, and unresolved risks. A missing required layer is `incomplete`, not
a soft green. `--verify-linked` checks packet-linked file hashes but does not
execute the claimed commands.

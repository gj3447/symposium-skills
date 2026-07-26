---
name: pi-workbench
description: >-
  Coordinate PI research and engineering through a canonical-main single-writer gate, executable ooptdd or LTDD measurement, and deterministic LakatoTree judgment. Use when: work touches `PI/`, its symlinked repositories, EngineBoy measurement, or a claim of PI implementation or research progress. Do not use when: research is elsewhere in SYMPOSIUM and has no PI measurement or judgment surface; use `$symposium-research` instead.
---

# PI Workbench

Treat write authority, measurement, and judgment as separate authorities. One
root/parent session writes canonical `main`; parallel children remain read-only,
and an implementer does not grade its own result.

## 1. Resolve the target

Read `PI/AGENTS.md` and the target repository's own instructions. Resolve every
symlink and record `git rev-parse --show-toplevel`. If the imported snapshot has
no usable Git repository, keep it reference-only or work in an authorized fresh
clone; do not pretend it can be pushed.

Choose the narrowest repo-specific test route from
[references/pi-test-routing.md](references/pi-test-routing.md).

## 2. Serialize every shared write on canonical `main`

OMD is retired. Never call its MCP/CLI, write its coordination DB, create a lease
or heartbeat, run its health/heal path, or revive it as an optional fallback.
Historical OMD code, databases, and reports are read-only evidence.

For a mutating task, the root/parent session acquires the repository-wide writer
token with `scripts/session_writer.sh` from the canonical checkout's `main` and
declares exact paths. If another owner holds the token, remain read-only; never
create a session branch or linked worktree as a workaround. Preserve unrelated
dirty files, use explicit pathspecs, and release only after every configured push
remote reads back the committed SHA. A partial publication is `IN_DOUBT`, not done.

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

Report the writer owner/state, exact write-set, base and commit SHAs, remote
readback, correlation ID, positive and negative receipts, exact test commands,
independent judge command/result, provenance, and unresolved risks. A missing
required layer is `incomplete`, not a soft green. `--verify-linked` checks
packet-linked file hashes but does not execute the claimed commands.

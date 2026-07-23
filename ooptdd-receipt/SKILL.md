---
name: ooptdd-receipt
description: >-
  Design, produce, or audit an executable ooptdd/LTDD behavior receipt with a
  pre-run locked trace gate, real-code execution, positive readback, source
  binding, and an injected negative oracle. Use after PI behavior changes,
  when an agent claims a runtime path works, or when a green may be vacuous,
  self-authored, uncorroborated, or disconnected from the changed code.
---

# OOPTDD Receipt

An OOPTDD green is evidence that named events matched a spec, not proof that the
system is correct. Build the strongest honest receipt the target supports.

## 1. Lock a falsifiable gate before Green

Identify one requirement and one real entry point. Write or identify the
structured gate before the satisfying implementation run. Record its path and
SHA-256, a unique correlation ID, gating checks, forbidden events, and the
source symbol expected to emit them. Reject optional-only, pending-only, or
existence-only gates when they cannot falsify the claim.

Do not edit the spec to fit an observed trace. If a requirement changes, record
that as a new spec version and rerun Red.

## 2. Run the real producer and read back

Execute the repository's real test, CLI, service, or harness path. Capture the
command, cwd, commit, exit code, correlation/trace IDs, and emitted identity.
Flush and query the configured store or local memory backend through the normal
verifier. `ship()` success alone is not arrival.

Classify the observation as `present`, `absent`, or `inconclusive`. Never turn an
unreachable store into a pass or a code failure. Record scope, charge ratio,
evidence tier, forbidden-event result, and Longinus source binding when the
target exposes them.

## 3. Prove the gate can fail

Inject one controlled fault against the same spec hash: suppress or corrupt a
required event, violate a pinned value/invariant, trigger a forbidden event, or
make an explicitly separate territory probe refute the claim. The verifier must
return `red`/`failed`/`rejected`. Restore the fault and rerun the positive case.

A negative that only breaks a mock outside the changed path does not count.

## 4. Surface the oracle boundary

Prefer separate-source `external:` corroboration for effects that exist outside
the trace. State the write identity and read identity. If they are the same,
label the result derived/self-consistency. Precise numeric metrology, secret
redaction, and microsecond race claims need dedicated oracles rather than log
assertions.

## Receipt contract

Copy [assets/ooptdd-receipt.example.json](assets/ooptdd-receipt.example.json),
replace every placeholder from machine output, and set `template_only` to
`false`. Check the bundled schema fixture separately with `--template`:

```bash
python3 scripts/validate_receipt.py assets/ooptdd-receipt.example.json --template
python3 scripts/validate_receipt.py path/to/ooptdd-receipt.json --verify-linked --root /absolute/repo/root
```

The validator checks structure, anti-vacuity fields, and—with
`--verify-linked`—the files referenced by the packet. It does not rerun the
system or certify the truth of supplied observations. Read
[references/receipt-strength.md](references/receipt-strength.md) when selecting
the evidence tier and negative.

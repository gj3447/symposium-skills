# Receipt strength and honest claims

Use the target repository's OOPTDD implementation as runtime authority. This
crosswalk only prevents overclaiming during handoff.

| Evidence | Defensible claim |
|---|---|
| local test exit only | local path returned the recorded exit code |
| event emitted | producer reported an event; arrival is unproved |
| positive readback with charge | named evidence arrived and exercised a gate |
| invariant/metamorphic relation | observed trace is internally consistent for that relation |
| separate-source external corroboration | the named trace claim agrees with the identified territory probe |

For every tier, state what is outside the gate. `inconclusive` means unverified,
not falsified and not successful.

## Good negative oracles

- suppress the required event at the real emission boundary;
- change one pinned field to an out-of-contract value;
- emit a forbidden error under the same correlation ID;
- break an invariant while keeping event count constant;
- make a distinct DB/file/service probe disagree with the trace.

Keep the spec hash identical between the positive and injected-negative runs.
After the negative is observed, restore the producer and reproduce the positive.

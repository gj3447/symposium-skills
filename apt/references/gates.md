# APT evidence gates

Apply the smallest relevant subset:

- **Scope**: target, non-goals, and write authority are exact.
- **Traceability**: output cites the input artifact and revision.
- **Contract**: observable success and failure criteria exist.
- **Ground truth**: relevant tests, builds, proofs, or exact readbacks ran.
- **Independence**: external review is used when material risk/policy requires it.
- **Integration**: branch interfaces and assumptions agree.
- **Cleanup**: verified behavior is preserved and accidental complexity is controlled.

Gate decisions are `PASS`, `RETURN`, `BLOCK`, `OVERRIDE`, or `INCONCLUSIVE`. One supported blocker can
block. Zero findings is neither automatic pass nor automatic failure. Missing evidence is reported rather
than replaced by a critic count, human ceremony, or KG record.

An override requires explicit authority, the exact waived boundary, supplied reason, duration, and review
or rollback condition. It never follows from silence.

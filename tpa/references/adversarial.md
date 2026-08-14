# TPA adversarial review

Challenge recovery with direct code evidence:

- missing generated/vendor/test scope distinctions;
- parser failures hidden by grep-only scans;
- inferred conventions mislabeled as formal contracts;
- pattern names without required structural elements;
- alternatives or counterevidence omitted;
- anchor matches based only on names;
- drift denominators selected after results;
- bindings that do not resolve at the exact revision.

Formal review is bounded and target-specific. Do not require a fixed critic/finding count or mutate status.
Preserve supported dissent and return `INCONCLUSIVE` when the oracle is missing.

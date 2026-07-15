# LakatoTree judgment boundary

## Authorities

- Preregistration fixes the prediction before measurement.
- The measurement harness produces grounded evidence without a verdict.
- The deterministic judge computes the kernel verdict.
- Human authority handles hard-core mutation, ambiguous canon promotion, and
  other explicit human gates.
- Naesengmoon is adversarial critique, not a substitute scoring function.

## Fail closed

Return `unjudged` when any of these is true:

- preregistration occurred after measurement;
- evidence contains a hand-entered verdict;
- provenance or harness identity is missing;
- implementer and judge are the same agent;
- the declared judge did not execute or its result artifact is absent;
- the service is degraded and no local deterministic route was run.

An exploratory post-hoc measurement may still be useful evidence, but it cannot
be relabeled as a preregistered confirmatory result.

## Recommended local verification

From the LakatoTree repository, follow its current instructions. The standing
baseline is `.venv/bin/python -m pytest -q`; after core definition-line changes,
also run `.venv/bin/python -m lakatos.longinus audit`. For a single result, run
the smallest programme or pure judge command that reproduces the verdict and
record that exact command in the judgment packet.

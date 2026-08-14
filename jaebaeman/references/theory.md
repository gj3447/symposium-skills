# Jaebaeman method grounding

The protocol applies structured-concurrency and supervisor ideas to agent work:

- every child has an owner and bounded lifetime;
- dependencies and permissions are explicit;
- cancellation and partial failure are first-class outcomes;
- children do not outlive the parent without an explicit owner;
- integration is centralized while evidence collection may be parallel;
- observable evidence, not worker count, drives the decision.

Local TaskSpecs resemble messages or work orders, not durable ontology. W3C PROV concepts are useful for
recording activity, entity, and actor lineage without requiring graph persistence. Saga-style compensation
is used only for known external effects and must be explicit, safe, and authorized.

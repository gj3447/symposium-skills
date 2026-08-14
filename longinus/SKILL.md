---
name: longinus
kg_ref: ATOM_Skill_longinus
version: "4.0.0"
channel: stable
provenance: AI_DERIVED_FROM_USER_PRIMARY
description: >-
  Audit and propose traceable bindings from claims or KG identifiers to contracts, code symbols, files, ranges, hashes, and executable artifacts, including forward/reverse orphan and drift checks. Invoke when: existing artifacts need code-to-claim traceability, reverse mapping, contract-code alignment, or SHA verification. Do not use when: the work still needs design or implementation rather than binding existing artifacts; use `$apt-st` or `$apt-scw` instead.
---

# Longinus — code-to-claim reference integrity

Longinus verifies whether a semantic identifier resolves to the intended code/artifact at an exact
revision. The default operation is read-only audit plus binding proposals. It does not auto-create missing
ontology, Lessons, ActionPlans, status changes, or baselines.

## Reference record

```yaml
reference_id: stable local identifier
semantic_target: exact claim, contract, or source identifier
target_fiber: algebra | physics | engineering | narrative | operations
repository: exact repository and revision
symbol: fully qualified symbol, when applicable
path: repository-relative path
range: stable symbol/range identity, not line number alone
content_hash: algorithm and value
artifact: crate, package, script, binary, or document identifier
provenance: actor, tool/parser version, command, and date
status: RESOLVES | DRIFT | ORPHAN_CODE | ORPHAN_SEMANTIC | AMBIGUOUS | MISSING
limitations: []
```

The seven useful concerns are semantic identity, contract relation, symbol identity, file location, stable
range, content hash, and executable/artifact identity. Not every target uses every concern; record
`NOT_APPLICABLE` rather than fabricating a field.

## Modes

### Forward audit

Starting from a claim/contract/KG identifier, resolve candidate code and verify repository, revision,
symbol, path, range, hash, and artifact. Return ambiguity instead of choosing by name alone.

### Reverse orphan audit

Starting from code, use an AST/parser where available to enumerate in-scope symbols and compare them with
existing semantic references. Grep may cross-check but cannot replace semantic extraction. Missing bindings
become local proposals, not auto-created nodes.

### Drift audit

Compare the frozen reference record with the exact current revision. Distinguish moved symbols, changed
behavior/signatures, deleted files, changed hashes, and mere line movement. Directory counts and scan counts
are coverage telemetry, not severity or truth.

### Artifact audit

Parse the versioned package/build manifest and associate executable artifacts with symbols/files. Return a
proposal; do not create package, script, or edge records automatically.

## Bidirectional laws

Use GetPut, PutGet, and PutPut as diagnostics:

- reading and rewriting an unchanged binding should be stable;
- after an authorized binding update, readback must resolve to the requested target;
- sequential updates must not silently retain conflicting older bindings.

A law violation is evidence of drift, not an automatic Lesson or canonical repair.

## Binding proposal

```yaml
pending_id: proposed identifier
target: exact semantic record and code revision
current_binding: exact observed value or NONE
proposed_binding: exact field-level values
evidence: source record, parser result, hash, and readback plan
reason_reusable: risk or cross-repository value
status: PENDING
ratifier_required: explicit authority
```

Ordinary audit findings remain local. Persist only material reusable proposals. A RootCause/Lesson candidate
requires demonstrated cause and reusable prevention; drift alone is insufficient.

## Ratified apply

Apply a binding only when the current task explicitly authorizes it and supplies an identified pending
proposal, exact allowed fields, current values, and writer authority. Recheck freshness, make the smallest
bounded change, and return exact before/after readback. Do not combine binding ratification with confidence,
status, canon, supersession, or unrelated ontology changes.

## Output

```yaml
mode: FORWARD_AUDIT | REVERSE_AUDIT | DRIFT_AUDIT | ARTIFACT_AUDIT | RATIFIED_APPLY
scope: exact repository/revision
references_checked: []
findings: []
binding_proposals: []
coverage_gaps: []
commands_and_tools: []
followups: []
persistence: LOCAL_ONLY | PENDING_PROPOSAL | RATIFIED_UPDATE
```

## Stop rule

Return after the requested audit/apply boundary. One evidence-backed blocker may block a release; counts
never decide. Formal adversarial review is conditional on material risk. Do not auto-repair, create a
Lesson/ActionPlan/seed, dispatch a critic, or recurse into another audit.

Historical v1–v3 direct MERGE/SET templates, scheduled repair, mandatory KG comments, and automatic Lesson
rules remain in Git history and unlinked references. They are not active instructions in v4.

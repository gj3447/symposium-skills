# MetaReview validation guidance

Validation follows the plane changed; it is not a grep ceremony for legacy words.

- Skill/document changes: repository frontmatter validator, strict description audit, link check, and
  `git diff --check`.
- TypeScript/Effect control-plane changes: strict typecheck, focused Effect tests, and the owning package's
  broader check.
- Python numerical-kernel or lock changes: locked environment diagnosis and targeted run/repro.
- Shared policy or gate changes: one independent evidence-based review when material.

A test must exercise the intended invariant rather than require a fixed phrase such as `RUBBER_STAMP`, a
Cypher label, a finding count, or a mandatory Lesson. Report exact commands and observed outcomes.

The executor does not impersonate an independent reviewer, and a passing local test does not ratify a KG
or canonical change.

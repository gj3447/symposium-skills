# APT validation checklist

- [ ] Exact target, scope, write authority, and completion condition are frozen.
- [ ] Each phase output cites its input artifact and revision.
- [ ] Contracts expose observable success and failure criteria.
- [ ] Implementation changes use the repository's intended architecture and runtime boundary.
- [ ] Directly relevant tests, builds, proofs, or exact readbacks ran.
- [ ] Partial failures, dissent, and unknowns remain visible.
- [ ] Reviewer independence is explicit when required.
- [ ] Decisions follow evidence rather than counts or unanimity.
- [ ] Discovery is a bounded candidate, not automatic re-entry.
- [ ] Persistence is local or qualified `PENDING`; canon mutation is separately ratified.

For TypeScript/Effect work, include strict typecheck, focused Effect tests, negative interruption/cleanup
cases where relevant, and the owning package's broader check. For Python numerical work, use the locked
environment and targeted run/repro. Documents use directly relevant syntax/link validation.

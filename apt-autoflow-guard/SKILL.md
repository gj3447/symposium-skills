---
name: apt-autoflow-guard
kg_ref: ATOM_Skill_apt_autoflow_guard
version: "1.0.0"
channel: experimental
canonical_name: apt-autoflow-guard
description: >-
  Audit APT automation hooks for bounded phase routing, explicit authority, evidence preservation, safe user-choice handling, and prevention of unauthorized persistence or recursion. Use when: installing or auditing APT automation markers/hooks or diagnosing a concrete guard violation. Do not use when: starting an APT cycle, choosing phases, or implementing work; use `$apt` instead.
---

# APT automation guard

Automation may remove mechanical friction but cannot suppress material user choices or broaden authority.

## Audit rules

- Reversible deterministic steps may proceed within the user's requested scope.
- A genuine material choice, missing authority, destructive action, or external uncertainty pauses for the
  owning user/actor.
- Hooks must not require a KG write, fixed finding count, human ceremony, or specific legacy phrase at every
  transition.
- Any persistent write requires an identified pending record, explicit writer/ratifier authority, exact
  target fields, and readback.
- Automatic phase routing is bounded and cancellable; discoveries do not recursively reopen the cycle.
- Hook failures report the exact rule, observed input, and recovery path without mutating state.

## Output

```yaml
hook_or_marker: exact path/version
observed_behavior: string
decision: PASS | WARN | BLOCK | INCONCLUSIVE
evidence: []
authority_gap: optional
safe_recovery: bounded action
```

This skill audits or proposes hook changes. It does not install global hooks, alter user configuration,
write KG/canon/status, or start an APT cycle unless the current task explicitly authorizes that operation.

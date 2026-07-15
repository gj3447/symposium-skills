---
name: lakatotree-judge
description: >-
  Preregister and independently judge a PI research-program result with the
  LakatoTree deterministic engine. Use when claiming progressive, partial,
  equivalent, or rejected research progress; when consuming
  lakato-evidence-record/v1 data; or when auditing that a verdict was derived
  from a locked prediction, grounded measurement, and replayable provenance
  rather than typed by an agent.
---

# LakatoTree Judge

Separate evidence authoring from verdict computation. The evidence record
contains no verdict; the judge derives one.

## 1. Preregister before measurement

Lock the programme, branch, conjecture, prediction/metric, direction, noise
band, novel target where applicable, and kill condition before executing the
measurement. Record the artifact hash and registration time. If measurement
already occurred without a valid preregistration, label the result exploratory;
do not backfill `registered_before_measurement=true`.

## 2. Freeze grounded evidence

Consume `lakato-evidence-record/v1` where the target supports it. Require
programme/branch/conjecture identity, measurement value/unit/scope, provenance
inputs or data manifest, grounded status, harness command/environment/commit,
and findings as proposals. Reject any evidence record that contains `verdict`.

For final data artifacts, include raw roots, output hashes, environment, recipe,
and replay result. Preserve degenerating/rejected branches as history.

## 3. Run an independent deterministic judge

Use a judge identity different from the implementer. Prefer the repository's
pure `judge()`/record-judge API or declared example programme, with the exact
command, cwd, commit, exit code, stdout/result hash, and engine entry point.
LakatoTree MCP may be used when healthy; an unavailable or degraded service is
not permission to hand-enter a verdict, so fall back to the local deterministic
route or report `unjudged`.

The kernel verdict vocabulary is `progressive`, `partial`, `equivalent`, or
`rejected`. Human verdicts remain separate for gates that explicitly require
human authority.

## 4. Package the judgment

Copy [assets/judgment-packet.example.json](assets/judgment-packet.example.json),
replace every placeholder with raw receipt data, and set `template_only` to
`false`. Check the bundled schema fixture separately with `--template`:

```bash
python3 scripts/validate_judgment.py assets/judgment-packet.example.json --template
python3 scripts/validate_judgment.py path/to/judgment-packet.json --verify-linked --root /absolute/repo/root
```

The packet must bind preregistration hash, evidence hashes, judge execution, and
derived result while proving implementer/judge separation. `--verify-linked`
checks the referenced files, while the validator still does not execute the
judge or certify scientific truth.

Read [references/judgment-boundary.md](references/judgment-boundary.md) before
promoting a result or using service/MCP output.

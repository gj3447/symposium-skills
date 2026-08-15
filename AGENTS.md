# AGENTS.md — SYMPOSIUM Skills (cross-tool agent index)

> Cross-tool agent skill catalog following the emerging `AGENTS.md` convention.
> Discoverable from `.agents/skills/` (symlink farm) and `.well-known/skills/index.json` (RFC 8615).

## Identity

| Field | Value |
|---|---|
| Publisher | SYMPOSIUM |
| Canonical path | `/home/lagyeongjun/CD/SYMPOSIUM/SKILLS` |
| Release | `v26.0.0` |
| Schema | `claude-skill v1` (frontmatter: `name`, `version`, `description`, `kg_ref`, `channel`) |
| Manifest | `MANIFEST.json` (merkle-rooted, drift-gated) |
| Discovery | `.well-known/skills/index.json` (public-safe subset) |
| Attestation | `.well-known/skills/attestation.json` (in-toto SLSA Provenance v1) |
| SBOM | `SBOM.json` (CycloneDX 1.5) |
| Marketplace | `.claude-plugin/marketplace.json` |
| OCI artifact-type | `application/vnd.symposium.claude-skills.v1+json` |
| KG namespace | `ATOM_Skill_*` (Neo4j) |

## Skill tiers

| Tier | Skills | Role |
|---|---|---|
| **research** | symposium-research | Thin PI/internal research router; selects specialists by measured need. |
| **pi** | pi-workbench, compute-offload | PI coordination, direct measurement, and managed compute. |
| **essence** | apt, harness, longinus, taliban, jaebaeman, prometheus | 5대 무기 + APT orchestrator. Constitutional governance via CODEOWNERS. |
| **alias** | 88-taliban, tlb, prom | Thin aliases of essence (drift-sensitive). |
| **phase** | apt-sa, apt-sp, apt-st, apt-scw, apt-meta-review | APT 5-phase cycle. |
| **tpa** | tpa, tpa-tcw, tpa-tt, tpa-tp, tpa-ta | Reverse cycle (code → spec). |
| **engineering** | engine-design, fsm-design, loop-engineering | Engine boundary, executable state semantics, and bounded Harness/runtime loops. |
| **meta** | solve, skill-creator | Meta-tooling. |
| **ops** | db-query, docker-logs, kafka-manage, server-status, deploy, backup | Infrastructure operations. |
| **interop** | call-grok, call-codex | Cross-agent headless delegation (`grok-agent`, `codex-agent`). |

## Discovery for non-Claude agents

Agents that don't know about Claude's `.claude/skills/` convention can:

1. Read `AGENTS.md` (this file) for top-level orientation.
2. Walk `.agents/skills/<name>/SKILL.md` (cross-tool symlink farm).
3. Fetch `.well-known/skills/index.json` for machine-readable catalog with merkle integrity.
4. Verify `MANIFEST.json` against `.well-known/skills/attestation.json` + cosign signature (when remote is wired).

## Codex discovery budget

Codex keeps only the thin `symposium-research` router plus the high-frequency APT,
TPA, Harness, engine/FSM/loop, and compute entry points eligible for implicit
invocation. PI evidence subskills, commander methods, thin aliases, internal
APT/TPA phases, specialist workers, and infrastructure operations carry
`agents/openai.yaml` with `policy.allow_implicit_invocation: false`; the router
invokes them explicitly after measuring need. Do not expose every leaf merely to
improve discoverability—extend the router instead.

## Root persistence boundary

This section governs every descendant skill, including older instructions that still say to create a
Lesson, write every finding to the KG, mutate status/config/canon, or recurse automatically.

- Default persistence is the execution log, local artifact, or parent handoff.
- A repeated, high-risk, cross-repository, or reusable result may be returned as a provenance-bearing
  `PENDING` proposal. Ordinary success, failure, gate transition, or discovery does not require a KG node.
- Create a `RootCause` or `Lesson` candidate only when evidence establishes the cause and a reusable
  prevention. Do not invent `truth` or a mechanism to satisfy completion criteria.
- Skills and subagents do not directly change canon, confidence, status, config, ActionPlan, seed, or
  supersession. Such mutation needs an identified pending record, current user intent, and a separately
  authorized ratifier/writer.
- Follow-up research and re-entry are separate bounded invocations. Start them only when they block the
  current decision or the user explicitly requests them.
- Agent, lens, finding, dispatch, and scan counts are coverage/telemetry, never votes for truth,
  priority, confidence, or ratification. Preserve evidence-backed dissent.

Scientific work uses the highest applicable T0/T1/T2 tier declared before execution. T0/T1 escalate to
T2 when the result materially affects a claim, and T2 is never downgraded after the outcome is observed.
Null/multiplicity, numerical Bayes, and Lakatos checks apply only under their explicit gates; they are
not mandatory ceremony for exact algebra or ordinary engineering.

## Drift detection

```bash
python3 bin/skill-merkle-check.py            # one-shot
launchctl list | grep symposium-merkle       # 12-min cron
```

`MANIFEST.merkle_root` is `SHA256(sorted(path:git_tree_sha))`. Mismatch with live state → DRIFT exit 1.

## Supply-chain hardening

- **CODEOWNERS**: 5대 무기 + aliases + critical metadata require owner review.
- **Pre-commit hook**: rebuilds MANIFEST.json on any `SKILL.md` staged change.
- **GH Actions** (dormant until remote): drift gate → validator → SBOM/attestation rebuild → cosign keyless (Fulcio + Rekor via OIDC) → npm-style provenance → ORAS push to GHCR on tag.

## Channel policy

`channel: stable | beta | experimental` in frontmatter. See `CHANNELS.md` for promotion rules.

## Reproducibility

Every artifact includes:
- `git_head_commit` — exact source commit
- `git_tree_sha` per skill — content-addressed
- `merkle_root` — bundle integrity gate
- `kg_ref` — KG `ATOM_Skill_<x>` node (W3C PROV-O Entity)

Re-running `bin/skill-build-manifest.py` at the same `git_head_commit` produces byte-identical output (deterministic `generatedAt` = HEAD commit time).

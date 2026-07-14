# Grok worker orders

The durable split is:

> Grok does MAP · COLLECT · FILL · COMPARE · ATTACK · DRAFT.  
> The parent does DECIDE · CANONIZE · BIND · MERGE.

`grok-job` packages a self-contained prompt and calls the existing
`grok-agent` engine with a locked preset. Every catalog job is read-only; none
maps to `write`.

The executable contract is canonical:

```bash
grok-job help <job>
```

This reference explains dispatch and gives recipes; it intentionally does not
duplicate every injected prompt, which would create a second contract that can
drift from the router.

## Quick start

```bash
grok-job list
grok-job help research
grok-job scout -- "Map SKILLS/call-grok and cite important paths"
grok-job verify -- "Check every numeric claim in docs/report.md"
grok-job fanout -- "Research these four independent axes and reconcile them: ..."
```

Preview the exact order without spending quota:

```bash
grok-job video-pack --dry-run --timeout 1800 -- "9:16, 45 seconds, topic: ..."
```

`--cwd`, `--max-turns`, `--timeout`, `--json`, and `--dry-run` are the only job
options. Default wall-clock timeout is 1800 seconds; timeout exits 124. Any other
nonzero exit is failure: retain stderr, do not invent a result, and do not treat
a partial `fanout` as complete. Increase `--max-turns` only when the output shows
a real collection gap, not merely to invite more prose.

## Dispatch table

| Need | Order | Preset | Turns | Parent acceptance check |
|---|---|---:|---:|---|
| Large folder or asset inventory | `scout` | `readonly` | 15 | sample paths; gaps and unknowns present |
| Compress long notes or transcripts | `summarize` | `readonly` | 15 | decisions separated from inference |
| Check claims, counts, or links | `verify` | `readonly` | 20 | reproduce high-severity rows and k/n |
| Current external evidence | `research` | `research` | 30 | reopen final official sources and dates |
| Product or approach matrix | `compare` | `research` | 30 | peers and criteria are genuinely comparable |
| Cold attack on a pasted plan | `critique` | `chat` | 8 | each attack has a falsifiable check |
| Bugs and regressions | `review` | `review` | 20 | reproduce every blocker |
| Boundary and failure tests | `testplan` | `review` | 20 | selected tests are later executed |
| Script, shot list, prompt pack | `video-pack` | `research` | 30 | all packet sections and asset gaps exist |
| Two to four independent axes | `fanout` | `chain` | 30 | every child has a collection status |

`critique` is deliberately tool-less. Paste the full plan after `--`; a path by
itself cannot be opened by the `chat` preset.

## Minimal recipes for every order

```bash
grok-job scout -- "Scope: PATHS. Map files, roles, evidence, duplicates, gaps, unknowns."

grok-job summarize -- "Sources: PATHS_OR_PASTED_TEXT. Preserve decisions, constraints, disagreements, provenance, and open items."

grok-job verify -- "Claims/report: TARGET. Check each atomic claim and number against local or official evidence."

grok-job research -- "As of DATE, research QUESTION using current official/primary sources; include opposing evidence and open gaps."

grok-job compare -- "Compare PEER_CANDIDATES on CRITERIA for SCENARIO. Cite every scored cell; no universal winner."

grok-job critique -- "FULL PLAN TEXT: ... . Steelman it, then attack assumptions with severity and falsifiable checks."

grok-job review -- "Changed files: PATHS. Intended behavior and invariants: SPEC. Return reproducible P0/P1/P2 defects only."

grok-job testplan -- "Code: PATHS. Contract: SPEC. Design prioritized invariant, boundary, failure, concurrency, and regression tests."

grok-job video-pack -- "Platform, ratio, runtime, audience, promise, voice, references, and described asset inventory: ..."

grok-job fanout -- "Run 2-4 named independent axes: AXES. Collect every child and expose duplicates, conflicts, and failures."
```

## SYMPOSIUM-native copy-paste orders

### Nest skeleton audit

```bash
grok-job scout -- \
  "Scan one-level topic directories under THEORY and METAHUMOTONIC. Report whether INDEX.md, SOURCES.md, PROM_*_REPORT.md, and _findings exist. Skip GIT, _archive, THEORY/SEMANTIC_INDEPENDENCE, and __pycache__. Return a gap table and counts; do not create anything."
```

### Stale path and pointer sweep

```bash
grok-job verify -- \
  "Find stale Markdown links, backticked paths, and sourcePath strings after the docs/ and FINDINGS/ moves. Return referrer:line, quoted path, existence, mechanical replacement or UNKNOWN. No rewrites and no KG updates."
```

### Findings crosswalk

```bash
grok-job scout -- \
  "Crosswalk raw JSON under FINDINGS and nested _findings directories to their PROM or cycle reports. Extract findingId, cycle, axis, report path, and layer. Report orphans on both sides; disk evidence only."
```

### Longinus disk pre-check

```bash
grok-job verify -- \
  "For path:line references in TARGET_FILES, check file existence, line bounds, and the expected symbol or needle. Directories are directory-level bindings. Do not hash or write Neo4j."
```

### Harness product comparison

```bash
grok-job compare -- \
  "As of today, compare only L_IDE peers: PRODUCT_LIST. Score Inform, Constrain, Verify, Correct from 0-3 only when current official documentation supports the cell. Preserve unknowns and cite direct URLs."
```

### Post-change defect hunt

```bash
grok-job review -- \
  "Changed files: PATHS. Intended behavior: SPEC. Return only P0/P1/P2 findings with file:line, failure scenario, evidence, and a reproducing test."
```

### Completion-claim spot check

```bash
grok-job verify -- \
  "Audit REPORT_PATH. Extract every numeric, completion, and scope claim; mark supported, contradicted, partial, or unverifiable with exact evidence. Recalculate all k/n values."
```

## Video production chain

Grok is most useful before generation: research, script alternatives, asset
indexing, shot decomposition, prompts, and continuity/QC. A strong parent agent
then selects the packet, calls image/video generators, reads the actual outputs
back, and assembles them with FFmpeg or a timeline tool.

| Stage | Owner and command | Required handoff / gate |
|---|---|---|
| 1. Asset inventory | `grok-job scout` + parent visual inspection | file, duration/size, parent-written visual description, rights, usable/missing |
| 2. Facts | `grok-job research` | cited factual pack and claims to avoid |
| 3. Treatments | `grok-job fanout` | 2-4 complete directions; parent selects one |
| 4. Production packet | `grok-job video-pack` | timed script, manifest, style bible, generation order, QC list |
| 5. Packet gate | parent | runtime sums correctly; every shot has an asset or generation plan |
| 6. Source stills | parent image generator | consistent character/style; inspect actual stills before animation |
| 7. Still gate | parent, optionally `grok-job verify` on descriptions/manifest | continuity, text/facts, aspect ratio, no missing shot |
| 8. Animation | parent video generator | one simple motion/camera beat per short shot |
| 9. Assembly | parent timeline/FFmpeg/Remotion | narration, licensed music/SFX, captions, transitions, loudness |
| 10. Final QC | parent + `grok-job verify` | timing, continuity, factual claims, caption/audio, rights, missing assets |

Headless `grok-job` currently receives text and paths, not TUI image chips. The
parent must visually inspect images/video and pass accurate descriptions or a
sidecar manifest; filenames alone are not visual understanding.

One-shot packet:

```bash
grok-job video-pack --cwd "$PROJECT" --timeout 1800 -- \
  "Platform: YouTube Shorts. Ratio: 9:16. Runtime: 45 seconds. Audience: ... . Promise/CTA: ... . Voice and pacing: ... . Brand/style constraints: ... . Factual sources: ... . Existing assets with parent-written visual descriptions and rights: ... . Return: hook; timed narration; shot manifest columns [timecode, purpose, visual, existing_asset_or_MISSING, source-image prompt, motion/camera prompt, generated duration, transition, audio/SFX, caption, continuity]; global style bible; generation order; factual citations; QC checklist; asset gaps. Prefer 6-second generation shots and mark edit trims separately."
```

Before generation, the parent must confirm:

- narration and shot durations sum to the target runtime
- every shot has `existing_asset_or_MISSING` resolved or an approved prompt
- recurring characters, wardrobe, palette, lens, lighting, and aspect ratio are in the style bible
- factual statements have usable citations; music, footage, and likeness rights are known
- source-image prompts describe frame 1; motion prompts contain one simple action or camera move
- captions, narration, SFX, transitions, and final QC criteria are present

For several creative directions first:

```bash
grok-job fanout -- \
  "Create four independent treatments for a 45-second vertical video: documentary, mythic, comedic, and technical. Each axis returns hook, beat sheet, visual grammar, factual risks, and asset burden. Do not choose the winner."
```

The installed Grok TUI also exposes `/imagine` and `/imagine-video`. The latter
plans short shots, creates source images, and animates them. Keep that actual
media-generation action outside `grok-job`: it spends generation quota and
produces artifacts, so the parent or user should invoke it deliberately after
reviewing the packet.

For a controlled multi-shot handoff, map `source-image prompt` to the still-image
generator, inspect the still, then map `motion/camera prompt` plus the approved
still to image-to-video. The installed Grok guidance currently supports 6s or
10s video generations and prefers 6s; trim shots during assembly rather than
claiming a generator duration it does not expose.

Final video-QC order:

```bash
grok-job verify -- \
  "Compare the final timeline transcript and parent-written visual/audio observations against the approved shot manifest. Check total runtime, shot order, continuity bible, factual claims, captions, audio/SFX, rights fields, missing assets, and every QC checkbox. Return supported/contradicted/unverifiable with timecodes."
```

## Anti-use

Do not delegate these to the worker catalog:

- USER_PRIMARY or KG canon verdicts
- APT/TPA phase gates or contract ownership
- Lean or precision mathematical proof
- deletion, archival decisions, deployment, secrets, or database writes
- final merge decisions or unresolved mythology closure
- a trivial search that one `rg` call can answer

Direct `grok-agent write` remains available, but only for an explicitly approved,
small mechanical patch in an isolated clean worktree with an allowlist and an
exact verification command.

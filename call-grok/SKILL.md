---
name: call-grok
description: >
  Invoke Grok CLI headless as a subordinate tool so Claude Code, Codex, or other agents can spend Grok Super quota on research/review/reasoning. Use when: "call grok", "ask grok", "grok-agent", "use grok", "grok subagent", "delegate to grok", "Grok Super 사용", "/call-grok", "/grok-agent". Prefer for second-opinion reviews, deep research, multi-file exploration, or tasks the parent wants offloaded to Grok.
---

# call-grok — use Grok as a tool

Run the shared wrapper (not interactive TUI). Parent agent = Claude / Codex / etc. Child = Grok headless.

## Prerequisites

- `grok` on PATH (or `~/.grok/bin/grok`) — verified: `grok version`
- Auth: prior `grok login` **or** `XAI_API_KEY`
- Wrapper: `grok-agent` on PATH **or** full path below

Canonical script:

```text
/Users/lagyeongjun/CD/SYMPOSIUM/SKILLS/call-grok/scripts/grok_agent.sh
```

Symlink (preferred): `~/.local/bin/grok-agent`

## When to call Grok (parent decision)

| Situation | Preset |
|---|---|
| Pure reasoning / second opinion, no repo touch | `chat` |
| Explore codebase / web, no writes (default) | `readonly` or `ask` |
| Broad research, more turns | `research` |
| Adversarial / bug-hunt code review | `review` |
| Parent wants Grok to implement | `write` (rare; confirm with user if destructive) |

**Do not** use Grok for trivial greps the parent can do cheaper. **Do** use when Super quota should absorb multi-turn tool work.

### When a "one-tier-lower" Grok is useful (not for everything)

Treat Grok as **cheap parallel bandwidth / second brain**, not as the sole architect of canon.

**Useful (high ROI):**
1. **Breadth fan-out** — "scan these 8 paths and list smells" while parent holds architecture.
2. **Second opinion** — parent drafts plan; Grok critiques (adversarial lite) without eating parent context.
3. **Quota offload** — multi-turn read/web that would bloat Claude/Codex context; Super pays the tool loop.
4. **Drafting grunt** — README outlines, commit message candidates, test case lists (parent edits).
5. **Fresh eyes** — session-cold read of a module (no parent chat bias).
6. **Live web / X-adjacent** exploration when parent is code-locked.

**Not useful (low ROI / risk):**
1. **Canon / mythology verdicts** — USER_PRIMARY + KG only; Grok is secondary commentary.
2. **Precision formal / Lean / gate math** — keep on stronger/formal path.
3. **Final merge decisions** on conflicted design — parent synthesizes.
4. **Trivial one-shot** greps/file reads parent already can do in 1 tool call.
5. **Secret or irreversible write** without user intent (`write` preset).

Rule of thumb: **Grok explores and drafts; parent judges and commits.**

## How to invoke (copy-paste)

### Default (readonly)

```bash
grok-agent readonly --cwd "$PWD" -- "YOUR TASK HERE"
```

### Research

```bash
grok-agent research --cwd "$PWD" --max-turns 30 -- "Research X; return consensus / divergence / open questions"
```

### Code review (read-only)

```bash
grok-agent review --cwd "$PWD" -- "Review these paths for bugs/security: PATHS..."
```

### Chat / second opinion

```bash
grok-agent chat -- "Critically evaluate this plan: ..."
```

### Write (full autonomy — careful)

```bash
grok-agent write --cwd "$PWD" -- "Implement Y with tests; report files changed"
```

### Multi-turn resume

```bash
# first call prints sessionId on stderr
grok-agent readonly --cwd "$PWD" -- "Map the auth module"
# then:
grok-agent readonly --cwd "$PWD" --resume SESSION_ID -- "Now propose a fix for the race"
```

### Machine-readable

```bash
grok-agent readonly --json --cwd "$PWD" -- "..." | jq -r '.text'
```

### Long prompt from file

```bash
grok-agent research --prompt-file /tmp/task.md --cwd "$PWD"
```

## Parent agent protocol

1. **Write a self-contained task.** Grok does not see the parent chat. Include goal, constraints, relevant paths, and output shape.
2. **Pick a preset** (table above). Default = `readonly`.
3. **Run the wrapper** via Bash/shell tool. Capture stdout = answer; stderr may include `sessionId=...`.
4. **Synthesize** Grok's answer into the parent reply. Label: `Grok (secondary)` when it is opinion/research, not USER canon.
5. **Never** present Grok prose as USER_PRIMARY myth canon.
6. On failure (exit ≠ 0): report stderr; do not invent Grok output.

### Recommended output shape to ask Grok for

```text
## Findings
- ...
## Evidence (paths / URLs)
- ...
## Open questions
- ...
## Confidence (0-1)
```

## Safety

| Preset | Writes files? | Shell? | Web? |
|---|---|---|---|
| chat | no | no | no |
| readonly / ask | no | no | yes |
| research | no | no | yes |
| review | no | no | no |
| write | **yes** (`--yolo`) | **yes** | yes |

- Prefer `readonly` / `review` / `research` from Claude/Codex.
- Use `write` only when the user explicitly wants Grok to edit, or the parent task is clearly implementation and scoped.
- Do not pass secrets into prompts.

## Manual equivalent (if wrapper missing)

```bash
grok -p "TASK" \
  --cwd "$PWD" \
  --yolo \
  --output-format json \
  --max-turns 15 \
  --tools "read_file,grep,list_dir,web_search,web_fetch" \
  --disallowed-tools "Agent,run_terminal_cmd,run_terminal_command,search_replace" \
  --rules "You are a read-only subagent for another AI. No file writes."
```

Docs: `~/.grok/docs/user-guide/14-headless-mode.md`, `15-agent-mode.md` (ACP for IDE, not needed for Claude/Codex shell call).

## What NOT to do

- Do not start interactive `grok` TUI from automation.
- Do not pipe stdin as the prompt (headless ignores stdin for prompt — use args or `--prompt-file`).
- Do not set unlimited turns without need.
- Do not use `write` for "just thinking".
- Do not skip quoting: always `grok-agent <preset> -- "prompt..."`.

## Slash / triggers

- `/call-grok <task>`
- `/grok-agent <preset> <task>`
- User: "그록한테 물어봐", "grok으로 리뷰", "super 쿼터로 돌려"

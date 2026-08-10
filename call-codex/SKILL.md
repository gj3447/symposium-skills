---
name: call-codex
kg_ref: ATOM_Skill_call_codex
version: "1.1.0"
channel: stable
description: >-
  Invoke Codex CLI headlessly as a subordinate, isolated agent for repository exploration, code review, research, or explicitly authorized implementation through `codex-agent`. Use when: the user asks to call, ask, or delegate to Codex or requests a Codex second opinion. Do not use when: the parent agent can complete a trivial local task or the user explicitly requests Grok; use direct handling or `$call-grok` instead.
---

# Call Codex headlessly

Run the wrapper, never the interactive TUI. Treat Codex output as subordinate analysis; the parent agent remains responsible for synthesis and verification.

Canonical script:

```text
/Users/lagyeongjun/CD/SYMPOSIUM/SKILLS/call-codex/scripts/codex_agent.sh
```

Prefer `codex-agent` when `SKILLS/bin` is on `PATH`.

## Choose a preset

| Preset | Behavior |
|---|---|
| `chat` | Reasoning-oriented prompt with a read-only sandbox; avoiding tools is an instruction, not a hard tool-disable boundary |
| `readonly` / `ask` | Inspect a repository without writes; default |
| `research` | Read-only inspection plus native web search |
| `review` | Read-only bug/security/regression review |
| `write` | Workspace-write sandbox for scoped implementation |

All presets set approval policy to `never` and never use dangerous bypass flags. By default the wrapper also uses `--ignore-user-config` so broken or untrusted user MCP/plugin configuration cannot enter the child run, and `--ephemeral` so one-shot calls do not accumulate sessions. `--user-config` opts back into user configuration; use it only when the child genuinely needs those configured integrations. Use `--persist` on the first call before relying on `--resume`; resumed calls then stay persisted unless `--ephemeral` is explicit.

## Invoke

```bash
codex-agent readonly --cwd "$PWD" -- "Map the auth flow; cite file:line evidence"
codex-agent review --cwd "$PWD" -- "Review the current diff for bugs and missing tests"
codex-agent research --cwd "$PWD" -- "Compare the documented approaches and cite sources"
codex-agent write --cwd "$PWD" -- "Implement the scoped change and run focused tests"
codex-agent readonly --persist --cwd "$PWD" -- "Map this package"
codex-agent readonly --resume SESSION_ID --cwd "$PWD" -- "Now inspect the race condition"
codex-agent review --timeout 900 --cwd "$PWD" -- "Review the current diff"
codex-agent readonly --json --prompt-file /tmp/task.md --cwd "$PWD"
```

Useful options: `--model`, `--persist` / `--ephemeral`, `--user-config`, `--resume`, `--prompt-file`, `--output-schema`, `--timeout`, and `--json` / `--text`. The wall-clock timeout defaults to 1,800 seconds and is capped at 86,400 seconds.

The default text mode emits only the final Codex message. JSON mode converts Codex JSONL into one stable object with `schemaVersion`, `text`, `sessionId`, `preset`, `persisted`, and `events`. A successful CLI run with no non-whitespace final message is treated as failure. The wrapper preserves Codex's nonzero exit status while suppressing raw event content on failure. Timeout, parent cancellation, and normal lead-process exit terminate the Codex process group so MCP or subagent descendants do not linger.

## Parent protocol

1. Supply a self-contained task with goal, constraints, relevant paths, and desired output shape; the child cannot see the parent chat.
2. Prefer `readonly`, `review`, or `research`. Select `write` only when implementation is in scope.
3. Capture stdout as the result and treat stderr as diagnostics.
4. Verify claims or diffs before presenting them as final. Never present child prose as USER_PRIMARY canon.
5. Do not include secrets in prompts. Do not enable `--user-config` merely to work around unrelated MCP startup failures.

Prerequisites: an authenticated `codex` executable on `PATH` (or set `CODEX_BIN` to its path) and `python3` for JSONL normalization.

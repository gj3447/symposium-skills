#!/usr/bin/env bash
# grok_agent.sh — headless Grok wrapper for Claude / Codex / other CLI agents
#
# Usage:
#   grok-agent <preset> [options] -- <prompt...>
#   grok-agent ask [options] -- <prompt...>
#   grok-agent --help
#
# Presets:
#   chat       pure reasoning, no tools (cheap, fast)
#   readonly   read codebase + web, no writes (default for other agents)
#   research   readonly + more turns (web + deep explore)
#   chain      parallel read-only Grok subagents + web research
#   review     code review style (readonly, focused rules)
#   write      full agent autonomy (yolo write/shell) — use sparingly
#   ask        alias of readonly
#
# Examples:
#   grok-agent chat -- "Summarize CAP theorem in 5 bullets"
#   grok-agent readonly --cwd ~/proj -- "Explain auth flow"
#   grok-agent research --max-turns 25 -- "Compare APT vs TPA"
#   grok-agent chain --max-turns 30 -- "Research 3 independent axes and synthesize"
#   grok-agent write -- "Add unit tests for src/foo.ts"
#   grok-agent review -- "Review staged changes for bugs"
#
# Output:
#   default: plain text of the response (and session id on stderr)
#   --json: full headless JSON object on stdout
#
# Auth: uses cached `grok login` or XAI_API_KEY.
# Docs: ~/.grok/docs/user-guide/14-headless-mode.md
#
# KG: skill-call-grok-wrapper-2026-07-13

set -euo pipefail

VERSION="1.1.0"
GROK_BIN="${GROK_BIN:-}"
if [[ -z "${GROK_BIN}" ]]; then
  if command -v grok >/dev/null 2>&1; then
    GROK_BIN="$(command -v grok)"
  elif [[ -x "${HOME}/.grok/bin/grok" ]]; then
    GROK_BIN="${HOME}/.grok/bin/grok"
  elif [[ -x "${HOME}/.local/bin/grok" ]]; then
    GROK_BIN="${HOME}/.local/bin/grok"
  else
    echo "grok-agent: grok binary not found (install Grok CLI or set GROK_BIN)" >&2
    exit 127
  fi
fi

usage() {
  sed -n '2,35p' "$0" | sed 's/^# \{0,1\}//'
  cat <<'EOF'

Options:
  --cwd PATH           Working directory (default: $PWD)
  --model MODEL        Model id (default: grok CLI default)
  --max-turns N        Max agent turns (preset default if omitted)
  --resume ID          Resume session id
  --continue           Continue most recent session in cwd
  --rules TEXT         Extra system rules
  --prompt-file PATH   Read prompt from file (instead of trailing args)
  --json               Emit full JSON on stdout
  --text               Emit response text only (default)
  --raw-args ARGS...   Pass remaining flags to grok after --
  -h, --help           Show help
  -v, --version        Show version

Env:
  GROK_BIN             Path to grok binary
  GROK_AGENT_DEFAULT_PRESET   Default preset if first arg is not a preset (default: readonly)
  XAI_API_KEY          API key auth (optional if logged in)
EOF
}

die() { printf 'grok-agent: %s\n' "$*" >&2; exit 1; }

PRESET=""
CWD=""
MODEL=""
MAX_TURNS=""
RESUME=""
CONTINUE=0
RULES=""
PROMPT_FILE=""
OUT_MODE="text"   # text | json
EXTRA_GROK_ARGS=()
PROMPT_ARGS=()
SEEN_DD=0

if [[ $# -eq 0 ]]; then
  usage
  exit 2
fi

case "${1:-}" in
  chat|readonly|research|chain|review|write|ask)
    PRESET="$1"
    shift
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  -v|--version)
    echo "grok-agent ${VERSION}"
    exit 0
    ;;
  *)
    PRESET="${GROK_AGENT_DEFAULT_PRESET:-readonly}"
    ;;
esac

# ask == readonly
[[ "${PRESET}" == "ask" ]] && PRESET="readonly"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --)
      SEEN_DD=1
      shift
      PROMPT_ARGS+=("$@")
      break
      ;;
    --cwd)
      CWD="${2:-}"; shift 2 || die "--cwd needs PATH"
      ;;
    --model)
      MODEL="${2:-}"; shift 2 || die "--model needs MODEL"
      ;;
    --max-turns)
      MAX_TURNS="${2:-}"; shift 2 || die "--max-turns needs N"
      ;;
    --resume)
      RESUME="${2:-}"; shift 2 || die "--resume needs ID"
      ;;
    --continue)
      CONTINUE=1
      shift
      ;;
    --rules)
      RULES="${2:-}"; shift 2 || die "--rules needs TEXT"
      ;;
    --prompt-file)
      PROMPT_FILE="${2:-}"; shift 2 || die "--prompt-file needs PATH"
      ;;
    --json)
      OUT_MODE="json"
      shift
      ;;
    --text)
      OUT_MODE="text"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --raw-args)
      shift
      EXTRA_GROK_ARGS+=("$@")
      break
      ;;
    -*)
      die "unknown option: $1 (use -- before free-form prompt text)"
      ;;
    *)
      # bare tokens after preset become the prompt
      PROMPT_ARGS+=("$@")
      break
      ;;
  esac
done

# Resolve prompt
PROMPT=""
TMP_PROMPT=""
TMP_RUN_DIR=""
TIMER_PIPE=""
TIMER_FD_OPEN=0
GROK_PID=""
GROK_PGID=""
signal_grok_group() {
  local signal_name="$1"
  [[ -n "${GROK_PGID:-}" ]] || return 0
  if ! kill "-${signal_name}" -- "-${GROK_PGID}" 2>/dev/null; then
    if [[ -n "${GROK_PID:-}" ]] && kill -0 "${GROK_PID}" 2>/dev/null; then
      kill "-${signal_name}" "${GROK_PID}" 2>/dev/null || true
    fi
  fi
}
cleanup() {
  [[ -n "${TMP_PROMPT}" && -f "${TMP_PROMPT}" ]] && rm -f "${TMP_PROMPT}"
  if [[ -n "${GROK_PID:-}" ]]; then
    signal_grok_group TERM
    signal_grok_group KILL
  fi
  if [[ "${TIMER_FD_OPEN:-0}" -eq 1 ]]; then
    exec 99>&-
    TIMER_FD_OPEN=0
  fi
  [[ -n "${TIMER_PIPE:-}" && -p "${TIMER_PIPE}" ]] && rm -f "${TIMER_PIPE}"
  [[ -n "${TMP_RUN_DIR}" && -d "${TMP_RUN_DIR}" ]] && rm -rf "${TMP_RUN_DIR}"
  return 0
}
terminate_grok() {
  local exit_code="$1"
  local killer_pid=""
  trap '' HUP INT TERM
  if [[ -n "${GROK_PID:-}" ]] && kill -0 "${GROK_PID}" 2>/dev/null; then
    signal_grok_group TERM
    (
      if ! IFS= read -r -t 5 _ <&99; then
        signal_grok_group KILL
      fi
    ) &
    killer_pid=$!
    wait "${GROK_PID}" 2>/dev/null || true
    printf 'done\n' >&99 2>/dev/null || true
    wait "${killer_pid}" 2>/dev/null || true
    signal_grok_group KILL
  fi
  GROK_PID=""
  GROK_PGID=""
  exit "${exit_code}"
}
trap cleanup EXIT
trap 'terminate_grok 129' HUP
trap 'terminate_grok 130' INT
trap 'terminate_grok 143' TERM

if [[ -n "${PROMPT_FILE}" ]]; then
  [[ -r "${PROMPT_FILE}" ]] || die "prompt file not readable: ${PROMPT_FILE}"
elif [[ ${#PROMPT_ARGS[@]} -gt 0 ]]; then
  PROMPT="${PROMPT_ARGS[*]}"
else
  die "missing prompt (pass after -- or use --prompt-file)"
fi

# Preset → tool policy + defaults
DISALLOWED=""
TOOLS=""
YOLO=0
DEFAULT_TURNS=12
BASE_RULES=""
ENABLE_SUBAGENTS=0
ENABLE_WEB_FETCH=0
DISABLE_FILE_WRITE=0
SANDBOX_PROFILE=""

case "${PRESET}" in
  chat)
    # No tools: pure model reply. Use denylist of common write/shell tools.
    DISALLOWED="Agent,run_terminal_cmd,run_terminal_command,search_replace,web_search,web_fetch,image_gen,image_edit"
    DEFAULT_TURNS=3
    BASE_RULES="You are being invoked as a subordinate tool by another AI agent. Answer directly and concisely. Do not attempt tool use."
    ;;
  readonly)
    TOOLS="read_file,grep,list_dir,web_search,web_fetch"
    # Also deny write/shell explicitly in case tool names drift
    DISALLOWED="Agent,run_terminal_cmd,run_terminal_command,search_replace"
    DEFAULT_TURNS=15
    YOLO=1
    ENABLE_WEB_FETCH=1
    DISABLE_FILE_WRITE=1
    SANDBOX_PROFILE="read-only"
    BASE_RULES="You are Grok invoked as a READ-ONLY tool by another AI agent (Claude or Codex). Explore with read/search/web tools only. Do NOT edit files, run shell that mutates state, or commit. Return a crisp structured answer the parent agent can use: findings, evidence paths, open questions, confidence."
    ;;
  research)
    TOOLS="read_file,grep,list_dir,web_search,web_fetch"
    DISALLOWED="Agent,run_terminal_cmd,run_terminal_command,search_replace"
    DEFAULT_TURNS=30
    YOLO=1
    ENABLE_WEB_FETCH=1
    DISABLE_FILE_WRITE=1
    SANDBOX_PROFILE="read-only"
    BASE_RULES="You are Grok research subagent (read-only). Prefer diverse sources + local canon when in SYMPOSIUM. Structure: consensus, divergence, open questions, recommended next steps. Cite paths/URLs. No file writes."
    ;;
  chain)
    # Explicitly expose only read/web tools plus the task lifecycle needed for
    # one-level Grok subagents. The read-only sandbox protects the workspace.
    TOOLS="read_file,grep_search,list_dir,web_search,web_fetch,task,get_task_output,kill_task,todo_write"
    DISALLOWED="run_terminal_cmd,run_terminal_command,bash,search_replace"
    DEFAULT_TURNS=30
    YOLO=1
    ENABLE_SUBAGENTS=1
    ENABLE_WEB_FETCH=1
    DISABLE_FILE_WRITE=1
    SANDBOX_PROFILE="read-only"
    BASE_RULES="You are the lead Grok research agent invoked by another AI. Decompose independent research axes and dispatch 2-4 explore subagents in parallel with capability_mode read-only. Collect every result, reconcile conflicts, and synthesize an evidence-backed answer with source URLs. Do not edit files or run shell commands."
    ;;
  review)
    TOOLS="read_file,grep,list_dir"
    DISALLOWED="Agent,run_terminal_cmd,run_terminal_command,search_replace,web_search,web_fetch"
    DEFAULT_TURNS=20
    YOLO=1
    DISABLE_FILE_WRITE=1
    SANDBOX_PROFILE="read-only"
    BASE_RULES="You are Grok code-review subagent (read-only). Focus on bugs, security, regressions, missing tests. Severity-tag findings (P0/P1/P2). Include file:line evidence. No fixes unless asked — report only."
    ;;
  write)
    DEFAULT_TURNS=40
    YOLO=1
    BASE_RULES="You are Grok write-capable subagent invoked by another AI. Implement the request carefully. Prefer small diffs. State files changed and how to verify. Do not force-push or delete canon."
    ;;
  *)
    die "unknown preset: ${PRESET}"
    ;;
esac

[[ -z "${MAX_TURNS}" ]] && MAX_TURNS="${DEFAULT_TURNS}"
[[ -z "${CWD}" ]] && CWD="${PWD}"
[[ -d "${CWD}" ]] || die "cwd does not exist: ${CWD}"

MERGED_RULES="${BASE_RULES}"
if [[ -n "${RULES}" ]]; then
  MERGED_RULES="${BASE_RULES}

Additional rules from parent agent:
${RULES}"
fi

# Build command.
# Headless is triggered by --prompt-file / --prompt-json / -p <PROMPT>.
# Do NOT pass bare -p with --prompt-file (clap requires a value for -p).
CMD=("${GROK_BIN}")
if [[ -n "${PROMPT_FILE}" ]]; then
  CMD+=(--prompt-file "${PROMPT_FILE}")
else
  # Long prompts via temp file avoid shell arg limits
  TMP_PROMPT="$(mktemp -t grok-agent-prompt.XXXXXX)"
  printf '%s' "${PROMPT}" >"${TMP_PROMPT}"
  CMD+=(--prompt-file "${TMP_PROMPT}")
fi

CMD+=(--cwd "${CWD}")
CMD+=(--output-format json)
CMD+=(--max-turns "${MAX_TURNS}")
CMD+=(--no-auto-update)
CMD+=(--rules "${MERGED_RULES}")

if [[ -n "${MODEL}" ]]; then
  CMD+=(-m "${MODEL}")
fi
if [[ -n "${RESUME}" ]]; then
  CMD+=(--resume "${RESUME}")
fi
if [[ "${CONTINUE}" -eq 1 ]]; then
  CMD+=(--continue)
fi
if [[ "${YOLO}" -eq 1 ]]; then
  CMD+=(--yolo)
fi
if [[ -n "${SANDBOX_PROFILE}" ]]; then
  CMD+=(--sandbox "${SANDBOX_PROFILE}")
fi
if [[ -n "${TOOLS}" ]]; then
  CMD+=(--tools "${TOOLS}")
fi
if [[ -n "${DISALLOWED}" ]]; then
  CMD+=(--disallowed-tools "${DISALLOWED}")
fi
if [[ ${#EXTRA_GROK_ARGS[@]} -gt 0 ]]; then
  CMD+=("${EXTRA_GROK_ARGS[@]}")
fi

# Run
# JSON is captured so we can extract text. A private temp directory avoids a
# predictable shared /tmp stderr path and lets signal traps forward cancellation.
ENV_ARGS=()
[[ "${ENABLE_SUBAGENTS}" -eq 1 ]] && ENV_ARGS+=("GROK_SUBAGENTS=1")
[[ "${ENABLE_WEB_FETCH}" -eq 1 ]] && ENV_ARGS+=("GROK_WEB_FETCH=1")
[[ "${DISABLE_FILE_WRITE}" -eq 1 ]] && ENV_ARGS+=("GROK_WRITE_FILE=0")

if ! TMP_RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/grok-agent-run.XXXXXX")"; then
  die "could not create temporary run directory"
fi
RAW_FILE="${TMP_RUN_DIR}/stdout"
ERR_FILE="${TMP_RUN_DIR}/stderr"
TIMER_PIPE="${TMP_RUN_DIR}/signal-control"
if ! mkfifo "${TIMER_PIPE}"; then
  die "could not create signal control pipe"
fi
if ! exec 99<>"${TIMER_PIPE}"; then
  die "could not open signal control pipe"
fi
TIMER_FD_OPEN=1
rm -f "${TIMER_PIPE}"
TIMER_PIPE=""

set -m
if [[ ${#ENV_ARGS[@]} -gt 0 ]]; then
  (
    exec 99>&-
    exec env "${ENV_ARGS[@]}" "${CMD[@]}"
  ) >"${RAW_FILE}" 2>"${ERR_FILE}" &
else
  (
    exec 99>&-
    exec "${CMD[@]}"
  ) >"${RAW_FILE}" 2>"${ERR_FILE}" &
fi
GROK_PID=$!
GROK_PGID="${GROK_PID}"
set +m

set +e
wait "${GROK_PID}" 2>/dev/null
RC=$?
set -e
# Subagents are scoped to this invocation; none may survive the lead process.
signal_grok_group KILL
GROK_PID=""
GROK_PGID=""
RAW="$(<"${RAW_FILE}")"

if [[ ${RC} -ne 0 ]]; then
  echo "grok-agent: grok exited ${RC}" >&2
  if [[ -s "${ERR_FILE}" ]]; then
    tail -n 40 "${ERR_FILE}" >&2
  fi
  # still try to show error JSON if any
  if [[ -n "${RAW}" ]]; then
    printf '%s\n' "${RAW}" >&2
  fi
  exit "${RC}"
fi

# Parse
if ! command -v jq >/dev/null 2>&1; then
  # Fallback: dump raw
  printf '%s\n' "${RAW}"
  exit 0
fi

SESSION_ID="$(printf '%s' "${RAW}" | jq -r '.sessionId // empty' 2>/dev/null || true)"
STOP="$(printf '%s' "${RAW}" | jq -r '.stopReason // empty' 2>/dev/null || true)"
TEXT="$(printf '%s' "${RAW}" | jq -r '.text // empty' 2>/dev/null || true)"

if [[ -n "${SESSION_ID}" ]]; then
  printf 'grok-agent: sessionId=%s stopReason=%s preset=%s turns_max=%s\n' \
    "${SESSION_ID}" "${STOP:-?}" "${PRESET}" "${MAX_TURNS}" >&2
fi

if [[ "${OUT_MODE}" == "json" ]]; then
  printf '%s\n' "${RAW}"
else
  if [[ -n "${TEXT}" ]]; then
    printf '%s\n' "${TEXT}"
  else
    # Maybe error shape
    printf '%s\n' "${RAW}"
  fi
fi

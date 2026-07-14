#!/usr/bin/env bash
# Headless Codex wrapper for Claude, Grok, and other parent agents.

set -euo pipefail

VERSION="1.1.0"

usage() {
  cat <<'EOF'
Usage:
  codex-agent <preset> [options] -- <prompt...>
  codex-agent <preset> [options] --prompt-file PATH

Presets:
  chat       reasoning-oriented instruction, read-only sandbox
  readonly   repository inspection, no writes (default)
  research   read-only inspection with native web search
  review     read-only code review
  write      scoped implementation in workspace-write sandbox
  ask        alias of readonly

Options:
  --cwd PATH           Working root (default: $PWD)
  --model MODEL        Codex model id
  --resume ID          Resume a persisted session
  --persist            Persist session data (new calls default to ephemeral)
  --ephemeral          Do not persist session data (resume persists by default)
  --user-config        Load user config, including configured MCP servers
  --ignore-user-config Ignore user config (default)
  --prompt-file PATH   Read the task from a file
  --output-schema PATH Constrain the final response with a JSON Schema
  --timeout SECONDS    Wall-clock limit (default: 1800, max: 86400)
  --json               Emit one normalized JSON object
  --text               Emit final response text only (default)
  -h, --help           Show this help
  -v, --version        Show wrapper version

Environment:
  CODEX_BIN                    Path or command name for Codex CLI
  CODEX_AGENT_DEFAULT_PRESET   Preset when none is supplied (readonly)
  CODEX_AGENT_TIMEOUT_SECONDS  Default wall-clock limit
EOF
}

die() {
  printf 'codex-agent: %s\n' "$*" >&2
  exit 2
}

need_value() {
  [[ $# -ge 2 && -n "${2:-}" ]] || die "$1 needs a value"
}

PRESET=""
CWD=""
MODEL=""
RESUME=""
PROMPT_FILE=""
OUTPUT_SCHEMA=""
OUT_MODE="text"
EPHEMERAL=1
PERSISTENCE_EXPLICIT=0
IGNORE_USER_CONFIG=1
TIMEOUT_SECONDS="${CODEX_AGENT_TIMEOUT_SECONDS:-1800}"
PROMPT_ARGS=()

if [[ $# -eq 0 ]]; then
  usage
  exit 2
fi

case "${1:-}" in
  chat|readonly|research|review|write|ask)
    PRESET="$1"
    shift
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  -v|--version)
    printf 'codex-agent %s\n' "${VERSION}"
    exit 0
    ;;
  *)
    PRESET="${CODEX_AGENT_DEFAULT_PRESET:-readonly}"
    ;;
esac

[[ "${PRESET}" == "ask" ]] && PRESET="readonly"
case "${PRESET}" in
  chat|readonly|research|review|write) ;;
  *) die "unknown preset: ${PRESET}" ;;
esac

while [[ $# -gt 0 ]]; do
  case "$1" in
    --)
      shift
      PROMPT_ARGS+=("$@")
      break
      ;;
    --cwd)
      need_value "$@"
      CWD="$2"
      shift 2
      ;;
    --model)
      need_value "$@"
      MODEL="$2"
      shift 2
      ;;
    --resume)
      need_value "$@"
      RESUME="$2"
      shift 2
      ;;
    --persist)
      EPHEMERAL=0
      PERSISTENCE_EXPLICIT=1
      shift
      ;;
    --ephemeral)
      EPHEMERAL=1
      PERSISTENCE_EXPLICIT=1
      shift
      ;;
    --user-config)
      IGNORE_USER_CONFIG=0
      shift
      ;;
    --ignore-user-config)
      IGNORE_USER_CONFIG=1
      shift
      ;;
    --prompt-file)
      need_value "$@"
      PROMPT_FILE="$2"
      shift 2
      ;;
    --output-schema)
      need_value "$@"
      OUTPUT_SCHEMA="$2"
      shift 2
      ;;
    --timeout)
      need_value "$@"
      TIMEOUT_SECONDS="$2"
      shift 2
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
    -v|--version)
      printf 'codex-agent %s\n' "${VERSION}"
      exit 0
      ;;
    -*)
      die "unknown option: $1 (use -- before prompt text)"
      ;;
    *)
      PROMPT_ARGS+=("$@")
      break
      ;;
  esac
done

[[ -z "${CWD}" ]] && CWD="${PWD}"
[[ -d "${CWD}" ]] || die "cwd does not exist: ${CWD}"

if [[ -n "${RESUME}" && "${PERSISTENCE_EXPLICIT}" -eq 0 ]]; then
  EPHEMERAL=0
fi

case "${TIMEOUT_SECONDS}" in
  ''|*[!0-9]*) die "timeout must be an integer between 1 and 86400 seconds" ;;
esac
TIMEOUT_SECONDS=$((10#${TIMEOUT_SECONDS}))
(( TIMEOUT_SECONDS >= 1 && TIMEOUT_SECONDS <= 86400 )) \
  || die "timeout must be an integer between 1 and 86400 seconds"

if [[ -n "${PROMPT_FILE}" ]]; then
  [[ -r "${PROMPT_FILE}" ]] || die "prompt file not readable: ${PROMPT_FILE}"
  [[ ${#PROMPT_ARGS[@]} -eq 0 ]] || die "use either --prompt-file or trailing prompt text, not both"
elif [[ ${#PROMPT_ARGS[@]} -eq 0 ]]; then
  die "missing prompt (pass it after -- or use --prompt-file)"
fi

if [[ -n "${OUTPUT_SCHEMA}" ]]; then
  [[ -r "${OUTPUT_SCHEMA}" ]] || die "output schema not readable: ${OUTPUT_SCHEMA}"
fi

CODEX_BIN="${CODEX_BIN:-}"
if [[ -n "${CODEX_BIN}" ]]; then
  if [[ "${CODEX_BIN}" == */* ]]; then
    [[ -x "${CODEX_BIN}" ]] || die "Codex binary is not executable: ${CODEX_BIN}"
  else
    CODEX_NAME="${CODEX_BIN}"
    CODEX_BIN="$(command -v "${CODEX_NAME}" 2>/dev/null || true)"
    [[ -n "${CODEX_BIN}" ]] || die "Codex binary not found: ${CODEX_NAME}"
  fi
elif command -v codex >/dev/null 2>&1; then
  CODEX_BIN="$(command -v codex)"
elif [[ -x "${HOME}/bin/codex" ]]; then
  CODEX_BIN="${HOME}/bin/codex"
elif [[ -x "${HOME}/.local/bin/codex" ]]; then
  CODEX_BIN="${HOME}/.local/bin/codex"
else
  printf 'codex-agent: codex binary not found (install Codex CLI or set CODEX_BIN)\n' >&2
  exit 127
fi

PYTHON_BIN="$(command -v python3 2>/dev/null || true)"
if [[ -z "${PYTHON_BIN}" ]]; then
  printf 'codex-agent: python3 is required to normalize Codex JSONL\n' >&2
  exit 69
fi

SANDBOX="read-only"
SEARCH=0
BASE_RULES=""
case "${PRESET}" in
  chat)
    BASE_RULES="You are Codex invoked headlessly as a reasoning-only subordinate. Answer directly and concisely. Do not inspect files, invoke tools, edit state, or use the web."
    ;;
  readonly)
    BASE_RULES="You are Codex invoked as a read-only subordinate by another AI agent. Inspect files and run non-mutating checks only. Do not edit files, install packages, commit, or change external state. Return findings with precise evidence paths, open questions, and confidence."
    ;;
  research)
    SEARCH=1
    BASE_RULES="You are Codex invoked as a read-only research subordinate. Use local evidence and native web search where useful. Do not edit files or change external state. Separate consensus, divergence, open questions, and recommendations; cite paths and URLs."
    ;;
  review)
    BASE_RULES="You are Codex invoked as a read-only code-review subordinate. Report bugs, security risks, regressions, and missing tests in severity order with file:line evidence. Do not implement fixes or change state."
    ;;
  write)
    SANDBOX="workspace-write"
    BASE_RULES="You are Codex invoked as a scoped implementation subordinate. Make only changes required by the parent task, preserve unrelated work, run focused validation, and report files changed and tests. Do not force-push, publish, or perform destructive external actions."
    ;;
esac

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-agent.XXXXXX")"
PROMPT_TMP="${TMP_DIR}/prompt.txt"
EVENTS_TMP="${TMP_DIR}/events.jsonl"
FINAL_TMP="${TMP_DIR}/final.txt"
NORMALIZED_TMP="${TMP_DIR}/normalized.json"
SESSION_TMP="${TMP_DIR}/session.txt"
WATCHDOG_PIPE="${TMP_DIR}/watchdog-control"
GRACE_PIPE="${TMP_DIR}/grace-control"
WATCHDOG_FD_OPEN=0
GRACE_FD_OPEN=0
WATCHDOG_PID=""
CODEX_PID=""
CODEX_PGID=""
WRAPPER_PID="$$"

signal_codex_group() {
  local signal_name="$1"
  [[ -n "${CODEX_PGID:-}" ]] || return 0
  if ! kill "-${signal_name}" -- "-${CODEX_PGID}" 2>/dev/null; then
    if [[ -n "${CODEX_PID:-}" ]] && kill -0 "${CODEX_PID}" 2>/dev/null; then
      kill "-${signal_name}" "${CODEX_PID}" 2>/dev/null || true
    fi
  fi
}

stop_watchdog() {
  if [[ -n "${WATCHDOG_PID:-}" ]]; then
    printf 'done\n' >&99 2>/dev/null || true
    wait "${WATCHDOG_PID}" 2>/dev/null || true
    WATCHDOG_PID=""
  fi
}

cleanup() {
  stop_watchdog
  if [[ -n "${CODEX_PID:-}" ]]; then
    signal_codex_group TERM
    signal_codex_group KILL
  fi
  if [[ "${WATCHDOG_FD_OPEN:-0}" -eq 1 ]]; then
    exec 99>&-
    WATCHDOG_FD_OPEN=0
  fi
  if [[ "${GRACE_FD_OPEN:-0}" -eq 1 ]]; then
    exec 98>&-
    GRACE_FD_OPEN=0
  fi
  rm -rf "${TMP_DIR}"
}

terminate_codex() {
  local exit_code="$1"
  local killer_pid=""
  trap '' HUP INT TERM USR1
  stop_watchdog
  if [[ -n "${CODEX_PID:-}" ]] && kill -0 "${CODEX_PID}" 2>/dev/null; then
    signal_codex_group TERM
    (
      if ! IFS= read -r -t 5 _ <&98; then
        signal_codex_group KILL
      fi
    ) &
    killer_pid=$!
    wait "${CODEX_PID}" 2>/dev/null || true
    printf 'done\n' >&98 2>/dev/null || true
    wait "${killer_pid}" 2>/dev/null || true
    signal_codex_group KILL
  fi
  CODEX_PID=""
  CODEX_PGID=""
  if [[ "${exit_code}" -eq 124 ]]; then
    printf 'codex-agent: timed out after %s seconds\n' "${TIMEOUT_SECONDS}" >&2
  fi
  exit "${exit_code}"
}

trap cleanup EXIT
trap 'terminate_codex 129' HUP
trap 'terminate_codex 130' INT
trap 'terminate_codex 143' TERM
trap 'terminate_codex 124' USR1

if ! mkfifo "${WATCHDOG_PIPE}" "${GRACE_PIPE}"; then
  die "could not create lifecycle control pipes"
fi
if ! exec 99<>"${WATCHDOG_PIPE}"; then
  die "could not open watchdog control pipe"
fi
WATCHDOG_FD_OPEN=1
if ! exec 98<>"${GRACE_PIPE}"; then
  die "could not open termination control pipe"
fi
GRACE_FD_OPEN=1
rm -f "${WATCHDOG_PIPE}" "${GRACE_PIPE}"

{
  printf '%s\n\n' "${BASE_RULES}"
  printf '%s\n' "Parent task:"
  if [[ -n "${PROMPT_FILE}" ]]; then
    cat -- "${PROMPT_FILE}"
  else
    printf '%s\n' "${PROMPT_ARGS[*]}"
  fi
} >"${PROMPT_TMP}"

# Global safety flags precede `exec`; exec-only isolation/output flags follow it.
CMD=("${CODEX_BIN}" --ask-for-approval never --sandbox "${SANDBOX}" --cd "${CWD}")
[[ -n "${MODEL}" ]] && CMD+=(--model "${MODEL}")
[[ "${SEARCH}" -eq 1 ]] && CMD+=(--search)
CMD+=(exec)
if [[ -n "${RESUME}" ]]; then
  CMD+=(resume)
fi
[[ "${IGNORE_USER_CONFIG}" -eq 1 ]] && CMD+=(--ignore-user-config)
[[ "${EPHEMERAL}" -eq 1 ]] && CMD+=(--ephemeral)
CMD+=(--skip-git-repo-check --json --output-last-message "${FINAL_TMP}")
[[ -n "${OUTPUT_SCHEMA}" ]] && CMD+=(--output-schema "${OUTPUT_SCHEMA}")
if [[ -n "${RESUME}" ]]; then
  CMD+=("${RESUME}" -)
else
  CMD+=(-)
fi

set -m
(
  exec 99>&-
  exec 98>&-
  exec "${CMD[@]}"
) <"${PROMPT_TMP}" >"${EVENTS_TMP}" &
CODEX_PID=$!
CODEX_PGID="${CODEX_PID}"
set +m

(
  exec 98>&-
  if ! IFS= read -r -t "${TIMEOUT_SECONDS}" _ <&99; then
    kill -USR1 "${WRAPPER_PID}" 2>/dev/null || true
  fi
) &
WATCHDOG_PID=$!

set +e
wait "${CODEX_PID}" 2>/dev/null
CODEX_RC=$?
set -e
stop_watchdog
# Codex-owned MCP/subagent descendants are scoped to one wrapper invocation.
signal_codex_group KILL
CODEX_PID=""
CODEX_PGID=""

if [[ "${CODEX_RC}" -ne 0 ]]; then
  if [[ -s "${EVENTS_TMP}" ]]; then
    printf 'codex-agent: Codex emitted JSONL before failing; event content suppressed\n' >&2
  fi
  exit "${CODEX_RC}"
fi

if "${PYTHON_BIN}" - "${EVENTS_TMP}" "${FINAL_TMP}" "${NORMALIZED_TMP}" "${SESSION_TMP}" "${PRESET}" "${EPHEMERAL}" <<'PY'
import json
import pathlib
import sys

events_path, final_path, normalized_path, session_path, preset, ephemeral = sys.argv[1:]

try:
    text = pathlib.Path(final_path).read_text(encoding="utf-8")
except FileNotFoundError:
    print("codex-agent: Codex succeeded without an output-last-message file", file=sys.stderr)
    raise SystemExit(65)

if not text.strip():
    print("codex-agent: Codex succeeded but returned an empty final response", file=sys.stderr)
    raise SystemExit(65)

events = []
session_id = None
for line_number, raw in enumerate(pathlib.Path(events_path).read_text(encoding="utf-8").splitlines(), 1):
    if not raw.strip():
        continue
    try:
        event = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"codex-agent: invalid Codex JSONL at line {line_number}: {exc}", file=sys.stderr)
        raise SystemExit(65)
    if not isinstance(event, dict):
        print(f"codex-agent: non-object Codex JSONL event at line {line_number}", file=sys.stderr)
        raise SystemExit(65)
    events.append(event)
    if session_id is None:
        for key in ("thread_id", "session_id", "sessionId"):
            value = event.get(key)
            if isinstance(value, str) and value:
                session_id = value
                break

if not events:
    print("codex-agent: Codex succeeded but emitted no JSONL events", file=sys.stderr)
    raise SystemExit(65)

payload = {
    "schemaVersion": 1,
    "text": text,
    "sessionId": session_id,
    "preset": preset,
    "persisted": ephemeral == "0",
    "events": events,
}
pathlib.Path(normalized_path).write_text(
    json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
pathlib.Path(session_path).write_text(session_id or "", encoding="utf-8")
PY
then
  :
else
  NORMALIZE_RC=$?
  exit "${NORMALIZE_RC}"
fi

SESSION_ID="$(cat "${SESSION_TMP}")"
if [[ -n "${SESSION_ID}" && "${EPHEMERAL}" -eq 0 ]]; then
  printf 'codex-agent: sessionId=%s preset=%s persisted=true\n' "${SESSION_ID}" "${PRESET}" >&2
fi

if [[ "${OUT_MODE}" == "json" ]]; then
  cat "${NORMALIZED_TMP}"
else
  cat "${FINAL_TMP}"
  LAST_BYTE_LINES="$(tail -c 1 "${FINAL_TMP}" | wc -l | tr -d ' ')"
  [[ "${LAST_BYTE_LINES}" -eq 1 ]] || printf '\n'
fi

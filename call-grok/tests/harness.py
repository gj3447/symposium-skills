"""Observable harness for grok-agent — ooptdd measurement layer.

Self-report (return dict status) can lie. Evidence is only what we *read back*
from subprocess stdout/stderr and ship into the backend.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

from ooptdd import Emitter
from ooptdd.backends import Backend

SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WRAPPER = SKILL_ROOT / "scripts" / "grok_agent.sh"

# Real Grok uses UUID; fakes may use opaque ids — accept non-space tokens.
SESSION_RE = re.compile(r"sessionId=([^\s]+)")


def _ev(backend: Backend, cid: str, event: str, **attrs: Any) -> None:
    Emitter(backend, service="call-grok.agent").emit(event, cid, **attrs)


def run_grok_agent(
    backend: Backend,
    *,
    cid: str | None = None,
    preset: str = "chat",
    prompt: str | None = "Reply with exactly: OOPTDD_PROBE",
    max_turns: int = 1,
    cwd: str | None = None,
    json_out: bool = False,
    extra_args: list[str] | None = None,
    wrapper: Path | None = None,
    grok_bin: str | None = None,
    env: dict[str, str] | None = None,
    timeout_s: float = 120.0,
) -> dict[str, Any]:
    """Run grok-agent and ship only *observed* events to ``backend``.

    Returns a self-report dict (may claim ok). Gate must be evaluated on the store.
    """
    cid = cid or f"ga-{uuid.uuid4().hex[:12]}"
    wrapper = wrapper or Path(os.environ.get("GROK_AGENT_WRAPPER", DEFAULT_WRAPPER))
    cwd = cwd or os.getcwd()

    _ev(backend, cid, "grok_agent.invoked", preset=preset, wrapper=str(wrapper))

    cmd: list[str] = [str(wrapper), preset, "--max-turns", str(max_turns), "--cwd", cwd]
    if json_out:
        cmd.append("--json")
    if extra_args:
        cmd.extend(extra_args)
    if prompt is not None:
        cmd.extend(["--", prompt])

    run_env = os.environ.copy()
    if grok_bin:
        run_env["GROK_BIN"] = grok_bin
    if env:
        run_env.update(env)

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            env=run_env,
        )
    except subprocess.TimeoutExpired as e:
        _ev(backend, cid, "grok_agent.timeout", timeout_s=timeout_s)
        _ev(backend, cid, "grok_agent.failed", reason="timeout")
        return {"status": "timeout", "cid": cid, "error": str(e)}
    except FileNotFoundError as e:
        _ev(backend, cid, "grok_agent.failed", reason="wrapper_missing", detail=str(e))
        return {"status": "error", "cid": cid, "error": str(e)}

    # Observations from the process (ground truth inputs)
    exit_code = proc.returncode
    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    _ev(backend, cid, "grok_agent.process_exited", exit_code=exit_code)

    if stdout.strip():
        _ev(
            backend,
            cid,
            "grok_agent.stdout_captured",
            nbytes=len(stdout),
            nonempty=True,
        )
    else:
        _ev(backend, cid, "grok_agent.stdout_empty")

    if stderr.strip():
        _ev(backend, cid, "grok_agent.stderr_captured", nbytes=len(stderr))

    m = SESSION_RE.search(stderr)
    session_id = m.group(1) if m else None
    if session_id:
        _ev(backend, cid, "grok_agent.session_id_observed", session_id=session_id)

    text = stdout.strip()
    parsed: dict[str, Any] | None = None
    if json_out and stdout.strip():
        try:
            parsed = json.loads(stdout)
            text = (parsed.get("text") or "").strip()
            _ev(backend, cid, "grok_agent.json_parsed", has_text=bool(text))
            if parsed.get("sessionId"):
                _ev(
                    backend,
                    cid,
                    "grok_agent.session_id_observed",
                    session_id=str(parsed["sessionId"]),
                    source="json",
                )
                session_id = str(parsed["sessionId"])
        except json.JSONDecodeError as e:
            _ev(backend, cid, "grok_agent.json_parse_failed", error=str(e)[:200])

    if text:
        _ev(backend, cid, "grok_agent.response_text_observed", nchars=len(text))

    # Self-report (can lie relative to silent partial failure)
    ok = exit_code == 0 and bool(text)
    if ok:
        _ev(backend, cid, "grok_agent.self_report_ok")
    else:
        _ev(
            backend,
            cid,
            "grok_agent.failed",
            reason="nonzero_or_empty",
            exit_code=exit_code,
        )

    return {
        "status": "ok" if ok else "error",
        "cid": cid,
        "exit_code": exit_code,
        "text": text,
        "session_id": session_id,
        "stdout": stdout,
        "stderr": stderr,
        "parsed": parsed,
    }


def write_fake_grok(path: Path, *, text: str = "OOPTDD_PROBE", session_id: str = "fake-sid-001") -> Path:
    """Install a fake ``grok`` binary that mimics headless ``--output-format json``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {
            "text": text,
            "stopReason": "EndTurn",
            "sessionId": session_id,
            "num_turns": 1,
        }
    )
    # Fake grok: ignore args, always emit success JSON on stdout
    path.write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' '{payload}'\n"
        "exit 0\n",
        encoding="utf-8",
    )
    path.chmod(0o755)
    return path


def write_fake_grok_drop(path: Path) -> Path:
    """Fake that self-reports nothing useful (empty stdout) but exit 0 — silent loss."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)
    return path

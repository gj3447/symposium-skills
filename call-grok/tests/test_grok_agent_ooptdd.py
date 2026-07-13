"""ooptdd receipts for call-grok / grok-agent.

Methodology: do not trust return status alone — ship observed subprocess
signals into MemoryBackend and evaluate YAML gates.

Run (from anywhere with ooptdd importable):

  cd /Users/lagyeongjun/CD/SYMPOSIUM/PI/ooptdd
  UV_CACHE_DIR=.uv-cache uv run --extra dev pytest \\
    /Users/lagyeongjun/CD/SYMPOSIUM/SKILLS/call-grok/tests/test_grok_agent_ooptdd.py -v -s

Live Super smoke (optional, burns quota):

  OOPTDD_GROK_LIVE=1 UV_CACHE_DIR=.uv-cache uv run --extra dev pytest \\
    ... -v -s -m live
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Ensure skill tests dir on path for harness import
TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS))

from harness import (  # noqa: E402
    run_grok_agent,
    write_fake_grok,
    write_fake_grok_drop,
)
from ooptdd import assert_gate, evaluate, load_gate  # noqa: E402
from ooptdd.backends.memory import MemoryBackend, reset  # noqa: E402

GATES = TESTS / "gates"
WRAPPER = TESTS.parent / "scripts" / "grok_agent.sh"


@pytest.fixture(autouse=True)
def _reset_memory():
    reset()
    yield
    reset()


def test_wrapper_script_exists():
    assert WRAPPER.is_file() and os.access(WRAPPER, os.X_OK)


def test_happy_path_fake_grok_gate_green(tmp_path: Path):
    """Healthy fake grok → events arrive → gate GREEN. Self-report ok is not enough alone."""
    fake = write_fake_grok(tmp_path / "fake-grok", text="OOPTDD_PROBE", session_id="sid-happy-1")
    b = MemoryBackend()
    cid = "cid-happy-fake"

    report = run_grok_agent(
        b,
        cid=cid,
        preset="chat",
        prompt="Reply with exactly: OOPTDD_PROBE",
        max_turns=1,
        grok_bin=str(fake),
        wrapper=WRAPPER,
        timeout_s=30,
    )

    # Self-report (claim)
    assert report["status"] == "ok"
    assert "OOPTDD_PROBE" in report["text"]

    # Truth: store
    gate = load_gate(str(GATES / "grok_agent_happy.yaml"))
    # load_gate may expect cid via env in some layouts; evaluate with explicit events
    result = evaluate(b, gate, cid=cid)
    assert result["ok"] is True, result

    # also trajectory-style present check
    res2 = assert_gate(
        {
            "cid": cid,
            "expect": [
                {
                    "trajectory": [
                        "grok_agent.invoked",
                        "grok_agent.process_exited",
                        "grok_agent.stdout_captured",
                        "grok_agent.session_id_observed",
                        "grok_agent.response_text_observed",
                        "grok_agent.self_report_ok",
                    ],
                    "within_s": 60,
                }
            ],
        },
        backend=b,
    )
    assert res2["ok"] is True, res2


def test_silent_drop_fake_exit0_empty_stdout_gate_catches_lie(tmp_path: Path):
    """exit 0 + empty body = silent loss. Gate must RED on happy-spec; GREEN on drop-spec."""
    fake = write_fake_grok_drop(tmp_path / "fake-grok-drop")
    b = MemoryBackend()
    cid = "cid-drop"

    report = run_grok_agent(
        b,
        cid=cid,
        preset="chat",
        prompt="anything",
        max_turns=1,
        grok_bin=str(fake),
        wrapper=WRAPPER,
        timeout_s=30,
    )

    # Self-report should NOT be ok (harness already ties ok to nonempty text)
    assert report["status"] != "ok"

    happy = evaluate(b, load_gate(str(GATES / "grok_agent_happy.yaml")), cid=cid)
    assert happy["ok"] is False, "happy gate must fail when stdout empty"

    drop = evaluate(b, load_gate(str(GATES / "grok_agent_silent_drop.yaml")), cid=cid)
    assert drop["ok"] is True, drop


def test_missing_prompt_fails_observably():
    """CLI contract: no prompt → nonzero exit; failed event shipped."""
    b = MemoryBackend()
    cid = "cid-noprompt"
    report = run_grok_agent(
        b,
        cid=cid,
        preset="chat",
        prompt=None,  # omit -- prompt
        max_turns=1,
        wrapper=WRAPPER,
        timeout_s=15,
    )
    assert report["exit_code"] != 0
    res = assert_gate(
        {
            "cid": cid,
            "expect": [
                {"present": [{"event": "grok_agent.invoked"}, {"event": "grok_agent.failed"}]},
            ],
        },
        backend=b,
    )
    assert res["ok"] is True, res


def test_json_mode_observes_session_from_body(tmp_path: Path):
    fake = write_fake_grok(tmp_path / "fake-grok", text="JSON_MODE_OK", session_id="sid-json-9")
    b = MemoryBackend()
    cid = "cid-json"
    report = run_grok_agent(
        b,
        cid=cid,
        preset="chat",
        prompt="x",
        json_out=True,
        grok_bin=str(fake),
        wrapper=WRAPPER,
    )
    assert report["status"] == "ok"
    assert report["session_id"] == "sid-json-9"
    res = assert_gate(
        {
            "cid": cid,
            "expect": [
                {"event": "grok_agent.json_parsed", "op": "==", "target": 1},
                {"event": "grok_agent.session_id_observed", "op": ">=", "target": 1},
            ],
        },
        backend=b,
    )
    assert res["ok"] is True, res


@pytest.mark.live
@pytest.mark.skipif(
    os.environ.get("OOPTDD_GROK_LIVE") != "1",
    reason="set OOPTDD_GROK_LIVE=1 to burn Super on real headless",
)
def test_live_chat_super_smoke():
    """Real Grok Super path — optional. Observes live sessionId + exact token."""
    b = MemoryBackend()
    cid = "cid-live-chat"
    report = run_grok_agent(
        b,
        cid=cid,
        preset="chat",
        prompt="Reply with exactly: OOPTDD_LIVE_OK",
        max_turns=1,
        wrapper=WRAPPER,
        timeout_s=90,
    )
    assert report["status"] == "ok", (report.get("stderr"), report.get("stdout"))
    assert "OOPTDD_LIVE_OK" in report["text"]
    result = evaluate(b, load_gate(str(GATES / "grok_agent_happy.yaml")), cid=cid)
    assert result["ok"] is True, result

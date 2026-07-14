"""Contract tests for the read-only grok-job router."""

from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
import textwrap
import time
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ROUTER = SKILL_ROOT / "scripts" / "grok_job.sh"
AGENT_WRAPPER = SKILL_ROOT / "scripts" / "grok_agent.sh"
WORKER_REFERENCE = SKILL_ROOT / "references" / "worker-jobs.md"
JOBS = {
    "scout": "readonly",
    "summarize": "readonly",
    "verify": "readonly",
    "research": "research",
    "compare": "research",
    "critique": "chat",
    "review": "review",
    "testplan": "review",
    "video-pack": "research",
    "fanout": "chain",
}


class GrokJobTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.capture_args = self.root / "args.txt"
        self.capture_prompt = self.root / "prompt.txt"
        self.invoked = self.root / "invoked"
        self.fake = self.root / "fake grok-agent"
        self.fake.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                set -eu
                : >"$CAPTURE_ARGS"
                : >"$INVOKED_MARKER"
                prompt=""
                previous=""
                for arg in "$@"; do
                  printf '%s\\n' "$arg" >>"$CAPTURE_ARGS"
                  if [[ "$previous" == "--prompt-file" ]]; then
                    prompt="$arg"
                  fi
                  previous="$arg"
                done
                if [[ -n "$prompt" ]]; then
                  cp "$prompt" "$CAPTURE_PROMPT"
                fi
                printf '%s\\n' "${FAKE_OUTPUT:-FAKE_OK}"
                exit "${FAKE_RC:-0}"
                """
            ),
            encoding="utf-8",
        )
        self.fake.chmod(0o755)
        self.env = os.environ.copy()
        self.env.update(
            {
                "GROK_AGENT_BIN": str(self.fake),
                "CAPTURE_ARGS": str(self.capture_args),
                "CAPTURE_PROMPT": str(self.capture_prompt),
                "INVOKED_MARKER": str(self.invoked),
            }
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_router(self, *args: str, **env_overrides: str) -> subprocess.CompletedProcess[str]:
        env = self.env.copy()
        env.update(env_overrides)
        return subprocess.run(
            [str(ROUTER), *args],
            capture_output=True,
            text=True,
            env=env,
            timeout=20,
        )

    def assert_pid_stops(self, pid_file: Path, message: str) -> None:
        deadline = time.monotonic() + 5
        while not pid_file.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue(pid_file.exists(), f"{message}: pid was never recorded")
        pid = pid_file.read_text(encoding="utf-8").strip()
        while time.monotonic() < deadline:
            probe = subprocess.run(
                ["ps", "-o", "stat=", "-p", pid],
                capture_output=True,
                text=True,
            )
            if probe.returncode != 0 or not probe.stdout.strip() or probe.stdout.lstrip().startswith("Z"):
                return
            time.sleep(0.05)
        self.fail(f"{message}: pid {pid} is still running")

    def test_script_exists_and_catalog_is_discoverable(self) -> None:
        self.assertTrue(ROUTER.is_file() and os.access(ROUTER, os.X_OK))
        result = self.run_router("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        for job in JOBS:
            self.assertIn(job, result.stdout)
        self.assertNotIn("write", [line.split()[0] for line in result.stdout.splitlines()[1:]])
        self.assertFalse(self.invoked.exists())

    def test_every_job_has_locked_safe_preset(self) -> None:
        for job, preset in JOBS.items():
            with self.subTest(job=job):
                result = self.run_router(job, "--", f"target for {job}")
                self.assertEqual(result.returncode, 0, result.stderr)
                argv = self.capture_args.read_text(encoding="utf-8").splitlines()
                self.assertEqual(argv[0], preset)
                self.assertNotIn("write", argv)
                self.assertEqual(argv.count("--prompt-file"), 1)
        chain_jobs = [job for job, preset in JOBS.items() if preset == "chain"]
        self.assertEqual(chain_jobs, ["fanout"])

    def test_target_is_literal_prompt_data_not_command_argv(self) -> None:
        marker = self.root / "SHOULD_NOT_EXIST"
        payload = f"$(touch {marker}) ; `touch {marker}` ; --raw-args --yolo"
        result = self.run_router("verify", "--json", "--", payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())
        prompt = self.capture_prompt.read_text(encoding="utf-8")
        argv = self.capture_args.read_text(encoding="utf-8")
        self.assertIn(payload, prompt)
        self.assertNotIn(payload, argv)
        self.assertIn("FIXED AUTHORITY AND SAFETY CONTRACT", prompt)
        self.assertIn("SECONDARY_AI", prompt)
        self.assertIn("--json", argv.splitlines())

    def test_dry_run_does_not_invoke_child(self) -> None:
        result = self.run_router("video-pack", "--dry-run", "--", "a 30 second film")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PRESET: research", result.stdout)
        self.assertIn("BEGIN_PARENT_TARGET_", result.stdout)
        self.assertIn("shot manifest", result.stdout)
        self.assertFalse(self.invoked.exists())
        command_line = next(
            line[len("COMMAND: ") :]
            for line in result.stdout.splitlines()
            if line.startswith("COMMAND: ")
        )
        argv = shlex.split(command_line)
        prompt_path = Path(argv[argv.index("--prompt-file") + 1])
        self.assertFalse(prompt_path.exists(), "dry-run leaked its rendered prompt")

    def test_video_handoff_contract_and_reference_stay_aligned(self) -> None:
        help_result = self.run_router("help", "video-pack")
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        reference = WORKER_REFERENCE.read_text(encoding="utf-8")
        packet_fields = [
            "existing_asset_or_MISSING",
            "source-image prompt",
            "motion/camera prompt",
            "global style bible",
            "generation order",
            "factual citations",
            "QC checklist",
        ]
        for field in packet_fields:
            with self.subTest(field=field):
                self.assertIn(field, help_result.stdout)
                self.assertIn(field, reference)
        for stage in ["Asset inventory", "Source stills", "Still gate", "Animation", "Assembly", "Final QC"]:
            with self.subTest(stage=stage):
                self.assertIn(stage, reference)
        self.assertIn("parent must visually inspect", reference)

    def test_cwd_with_spaces_and_target_words_are_preserved(self) -> None:
        cwd = self.root / "workspace with spaces"
        cwd.mkdir()
        result = self.run_router("scout", "--cwd", str(cwd), "--", "alpha", "beta gamma")
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = self.capture_args.read_text(encoding="utf-8").splitlines()
        self.assertEqual(argv[argv.index("--cwd") + 1], str(cwd.resolve()))
        prompt = self.capture_prompt.read_text(encoding="utf-8")
        self.assertIn("alpha beta gamma", prompt)

    def test_invalid_inputs_fail_before_invocation(self) -> None:
        bad_cases = [
            ("unknown", "--", "x"),
            ("verify",),
            ("verify", "--max-turns", "0", "--", "x"),
            ("verify", "--max-turns", "101", "--", "x"),
            ("verify", "--max-turns", "abc", "--", "x"),
            ("verify", "--timeout", "0", "--", "x"),
            ("verify", "--timeout", "7201", "--", "x"),
            ("verify", "--cwd", str(self.root / "missing"), "--", "x"),
            ("verify", "target without separator"),
            ("verify", "--", "   "),
        ]
        for args in bad_cases:
            with self.subTest(args=args):
                self.invoked.unlink(missing_ok=True)
                result = self.run_router(*args)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(self.invoked.exists())

    def test_leading_zero_numeric_options_are_normalized_as_decimal(self) -> None:
        result = self.run_router(
            "verify",
            "--max-turns",
            "008",
            "--timeout",
            "0008",
            "--dry-run",
            "--",
            "x",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MAX_TURNS: 8", result.stdout)
        self.assertIn("TIMEOUT_SECONDS: 8", result.stdout)
        self.assertFalse(self.invoked.exists())

    def test_child_exit_code_propagates_and_prompt_is_cleaned(self) -> None:
        result = self.run_router("research", "--", "x", FAKE_RC="37")
        self.assertEqual(result.returncode, 37)
        argv = self.capture_args.read_text(encoding="utf-8").splitlines()
        prompt_path = Path(argv[argv.index("--prompt-file") + 1])
        self.assertFalse(prompt_path.exists())

    def test_real_engine_enforces_readonly_sandbox_end_to_end(self) -> None:
        fake_grok = self.root / "fake underlying grok"
        captured_env = self.root / "underlying-env.txt"
        fake_grok.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                set -eu
                : >"$CAPTURE_ARGS"
                for arg in "$@"; do
                  printf '%s\\n' "$arg" >>"$CAPTURE_ARGS"
                done
                printf 'GROK_WRITE_FILE=%s\\n' "${GROK_WRITE_FILE:-}" >"$CAPTURE_ENV"
                printf 'GROK_WEB_FETCH=%s\\n' "${GROK_WEB_FETCH:-}" >>"$CAPTURE_ENV"
                printf 'GROK_SUBAGENTS=%s\\n' "${GROK_SUBAGENTS:-}" >>"$CAPTURE_ENV"
                printf '%s\\n' '{"text":"ENGINE_OK","stopReason":"EndTurn","sessionId":"sid-policy-1"}'
                """
            ),
            encoding="utf-8",
        )
        fake_grok.chmod(0o755)
        result = self.run_router(
            "research",
            "--",
            "official-source check",
            GROK_AGENT_BIN=str(AGENT_WRAPPER),
            GROK_BIN=str(fake_grok),
            CAPTURE_ENV=str(captured_env),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ENGINE_OK", result.stdout)
        argv = self.capture_args.read_text(encoding="utf-8").splitlines()
        self.assertEqual(argv[argv.index("--sandbox") + 1], "read-only")
        allowed = argv[argv.index("--tools") + 1]
        self.assertEqual(allowed, "read_file,grep,list_dir,web_search,web_fetch")
        env_lines = captured_env.read_text(encoding="utf-8").splitlines()
        self.assertIn("GROK_WRITE_FILE=0", env_lines)
        self.assertIn("GROK_WEB_FETCH=1", env_lines)

    def test_wall_clock_timeout_returns_124(self) -> None:
        sleeper = self.root / "sleeping grok-agent"
        descendant_pid = self.root / "timeout-descendant.pid"
        sleeper.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                set -u
                sleep 30 &
                printf '%s\\n' "$!" >"$DESCENDANT_PID_FILE"
                wait
                """
            ),
            encoding="utf-8",
        )
        sleeper.chmod(0o755)
        started = time.monotonic()
        result = self.run_router(
            "scout",
            "--timeout",
            "1",
            "--",
            "slow task",
            GROK_AGENT_BIN=str(sleeper),
            DESCENDANT_PID_FILE=str(descendant_pid),
        )
        elapsed = time.monotonic() - started
        self.assertEqual(result.returncode, 124, result.stderr)
        self.assertIn("timed out after 1 seconds", result.stderr)
        self.assertLess(elapsed, 8)
        self.assert_pid_stops(descendant_pid, "timeout left a descendant alive")

    def test_router_termination_cancels_agent_descendants(self) -> None:
        fake_agent = self.root / "nested fake grok-agent"
        descendant_pid = self.root / "cancel-descendant.pid"
        fake_agent.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                set -u
                sleep 30 &
                printf '%s\\n' "$!" >"$DESCENDANT_PID_FILE"
                wait
                """
            ),
            encoding="utf-8",
        )
        fake_agent.chmod(0o755)
        env = self.env.copy()
        env.update(
            {
                "GROK_AGENT_BIN": str(fake_agent),
                "DESCENDANT_PID_FILE": str(descendant_pid),
            }
        )
        proc = subprocess.Popen(
            [str(ROUTER), "scout", "--timeout", "30", "--", "wait"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        deadline = time.monotonic() + 5
        while not descendant_pid.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue(descendant_pid.exists(), "fake agent never spawned its child")
        proc.terminate()
        proc.communicate(timeout=10)
        self.assertEqual(proc.returncode, 143)
        self.assert_pid_stops(descendant_pid, "router cancellation left a descendant alive")

    def test_engine_forwards_termination_to_grok_process(self) -> None:
        fake_grok = self.root / "long-running grok"
        child_pid = self.root / "child.pid"
        grandchild_pid = self.root / "grandchild.pid"
        child_stopped = self.root / "child.stopped"
        fake_grok.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                set -u
                printf '%s\\n' "$$" >"$CHILD_PID_FILE"
                trap ': >"$CHILD_STOPPED_FILE"; exit 143' TERM INT HUP
                sleep 30 &
                printf '%s\\n' "$!" >"$GRANDCHILD_PID_FILE"
                wait
                """
            ),
            encoding="utf-8",
        )
        fake_grok.chmod(0o755)
        env = os.environ.copy()
        env.update(
            {
                "GROK_BIN": str(fake_grok),
                "CHILD_PID_FILE": str(child_pid),
                "GRANDCHILD_PID_FILE": str(grandchild_pid),
                "CHILD_STOPPED_FILE": str(child_stopped),
            }
        )
        proc = subprocess.Popen(
            [str(AGENT_WRAPPER), "chat", "--", "wait"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        deadline = time.monotonic() + 5
        while not child_pid.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue(child_pid.exists(), "underlying fake Grok never started")
        proc.terminate()
        proc.communicate(timeout=10)
        self.assertEqual(proc.returncode, 143)
        self.assertTrue(child_stopped.exists(), "termination was not forwarded to Grok")
        self.assert_pid_stops(grandchild_pid, "engine cancellation left a Grok child alive")


if __name__ == "__main__":
    unittest.main()

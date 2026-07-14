import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import unittest


SKILL_DIR = Path(__file__).resolve().parents[1]
WRAPPER = SKILL_DIR / "scripts" / "codex_agent.sh"


FAKE_CODEX = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

args = sys.argv[1:]
Path(os.environ["FAKE_ARGS_FILE"]).write_text(json.dumps(args), encoding="utf-8")
Path(os.environ["FAKE_STDIN_FILE"]).write_text(sys.stdin.read(), encoding="utf-8")

descendant_pid_file = os.environ.get("FAKE_DESCENDANT_PID_FILE")
if descendant_pid_file:
    ignore_term = os.environ.get("FAKE_DESCENDANT_IGNORE_TERM") == "1"
    child_code = (
        "import signal,time;"
        + ("signal.signal(signal.SIGTERM, signal.SIG_IGN);" if ignore_term else "")
        + "time.sleep(60)"
    )
    child = subprocess.Popen([sys.executable, "-c", child_code])
    Path(descendant_pid_file).write_text(str(child.pid), encoding="utf-8")

if "--output-last-message" in args and "FAKE_TEXT" in os.environ:
    output_path = Path(args[args.index("--output-last-message") + 1])
    output_path.write_text(os.environ["FAKE_TEXT"], encoding="utf-8")

jsonl = os.environ.get(
    "FAKE_JSONL",
    '{"type":"thread.started","thread_id":"thread-test"}\n'
    '{"type":"turn.completed","usage":{"input_tokens":1,"output_tokens":1}}\n',
)
sys.stdout.write(jsonl)
sys.stdout.flush()
time.sleep(float(os.environ.get("FAKE_SLEEP_SECONDS", "0")))
sys.exit(int(os.environ.get("FAKE_RC", "0")))
'''


class CodexAgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fake = self.root / "fake-codex"
        self.fake.write_text(FAKE_CODEX, encoding="utf-8")
        self.fake.chmod(0o755)
        self.args_file = self.root / "args.json"
        self.stdin_file = self.root / "stdin.txt"
        self.cwd = self.root / "repo"
        self.cwd.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def run_wrapper(self, *args, text="done", rc=0, jsonl=None, extra_env=None):
        env = os.environ.copy()
        env.update(
            {
                "CODEX_BIN": str(self.fake),
                "FAKE_ARGS_FILE": str(self.args_file),
                "FAKE_STDIN_FILE": str(self.stdin_file),
                "FAKE_RC": str(rc),
            }
        )
        if text is not None:
            env["FAKE_TEXT"] = text
        else:
            env.pop("FAKE_TEXT", None)
        if jsonl is not None:
            env["FAKE_JSONL"] = jsonl
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            [str(WRAPPER), *args],
            text=True,
            capture_output=True,
            env=env,
            check=False,
            timeout=15,
        )

    def recorded_args(self):
        return json.loads(self.args_file.read_text(encoding="utf-8"))

    def wait_for_file(self, path, timeout=5):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if path.exists() and path.read_text(encoding="utf-8").strip():
                return
            time.sleep(0.02)
        self.fail(f"timed out waiting for {path}")

    def assert_process_gone(self, pid, timeout=5):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.02)
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            return
        self.fail(f"process {pid} survived wrapper cleanup")

    def test_readonly_defaults_are_isolated_and_prompt_uses_stdin(self):
        prompt = "Inspect $(touch SHOULD_NOT_EXIST) and report `$HOME`."
        result = self.run_wrapper("readonly", "--cwd", str(self.cwd), "--", prompt)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "done\n")
        args = self.recorded_args()
        self.assertEqual(args[:7], [
            "--ask-for-approval", "never", "--sandbox", "read-only",
            "--cd", str(self.cwd), "exec",
        ])
        self.assertIn("--ignore-user-config", args)
        self.assertIn("--ephemeral", args)
        self.assertIn("--skip-git-repo-check", args)
        self.assertIn("--json", args)
        self.assertEqual(args[-1], "-")
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", args)
        self.assertNotIn("--search", args)
        sent = self.stdin_file.read_text(encoding="utf-8")
        self.assertIn("read-only subordinate", sent)
        self.assertIn(prompt, sent)
        self.assertFalse((self.cwd / "SHOULD_NOT_EXIST").exists())

    def test_write_json_persist_user_config_model_and_schema(self):
        schema = self.root / "schema.json"
        schema.write_text('{"type":"object"}', encoding="utf-8")
        result = self.run_wrapper(
            "write", "--cwd", str(self.cwd), "--persist", "--user-config",
            "--model", "gpt-test", "--output-schema", str(schema), "--json",
            "--", "Implement one change.", text='{"ok":true}\n',
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schemaVersion"], 1)
        self.assertEqual(payload["text"], '{"ok":true}\n')
        self.assertEqual(payload["sessionId"], "thread-test")
        self.assertEqual(payload["preset"], "write")
        self.assertTrue(payload["persisted"])
        self.assertEqual(len(payload["events"]), 2)
        args = self.recorded_args()
        self.assertEqual(args[args.index("--sandbox") + 1], "workspace-write")
        self.assertEqual(args[args.index("--model") + 1], "gpt-test")
        self.assertEqual(args[args.index("--output-schema") + 1], str(schema))
        self.assertNotIn("--ignore-user-config", args)
        self.assertNotIn("--ephemeral", args)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", args)
        self.assertIn("sessionId=thread-test", result.stderr)

    def test_research_resume_prompt_file_enables_search(self):
        prompt_file = self.root / "task.md"
        prompt_file.write_text("Research this safely.\nSecond line.\n", encoding="utf-8")
        result = self.run_wrapper(
            "research", "--cwd", str(self.cwd), "--resume", "session-123",
            "--prompt-file", str(prompt_file),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        args = self.recorded_args()
        self.assertIn("--search", args)
        exec_index = args.index("exec")
        self.assertEqual(args[exec_index + 1], "resume")
        self.assertEqual(args[-2:], ["session-123", "-"])
        self.assertNotIn("--ephemeral", args)
        self.assertIn("persisted=true", result.stderr)
        sent = self.stdin_file.read_text(encoding="utf-8")
        self.assertIn("native web search", sent)
        self.assertTrue(sent.endswith("Research this safely.\nSecond line.\n"))

    def test_codex_failure_preserves_exact_exit_code(self):
        secret = "raw-event-secret-must-not-leak"
        result = self.run_wrapper(
            "readonly", "--cwd", str(self.cwd), "--", "Fail predictably.",
            text=None, rc=37,
            jsonl=json.dumps({"type": "error", "detail": secret}) + "\n",
        )

        self.assertEqual(result.returncode, 37)
        self.assertIn("Codex emitted JSONL before failing", result.stderr)
        self.assertIn("content suppressed", result.stderr)
        self.assertNotIn(secret, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_resume_can_be_explicitly_ephemeral(self):
        result = self.run_wrapper(
            "readonly", "--cwd", str(self.cwd), "--resume", "session-123",
            "--ephemeral", "--", "Continue without persistence.",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--ephemeral", self.recorded_args())
        self.assertNotIn("persisted=true", result.stderr)

    def test_wall_clock_timeout_kills_codex_process_group(self):
        descendant_file = self.root / "timeout-descendant.pid"
        started = time.monotonic()
        result = self.run_wrapper(
            "readonly", "--cwd", str(self.cwd), "--timeout", "1", "--",
            "Take too long.",
            extra_env={
                "FAKE_SLEEP_SECONDS": "60",
                "FAKE_DESCENDANT_PID_FILE": str(descendant_file),
                "FAKE_DESCENDANT_IGNORE_TERM": "1",
            },
        )
        elapsed = time.monotonic() - started

        self.assertEqual(result.returncode, 124, result.stderr)
        self.assertLess(elapsed, 8)
        self.assertIn("timed out after 1 seconds", result.stderr)
        self.wait_for_file(descendant_file)
        self.assert_process_gone(int(descendant_file.read_text(encoding="utf-8")))

    def test_parent_termination_kills_codex_process_group(self):
        descendant_file = self.root / "term-descendant.pid"
        env = os.environ.copy()
        env.update({
            "CODEX_BIN": str(self.fake),
            "FAKE_ARGS_FILE": str(self.args_file),
            "FAKE_STDIN_FILE": str(self.stdin_file),
            "FAKE_TEXT": "done",
            "FAKE_SLEEP_SECONDS": "60",
            "FAKE_DESCENDANT_PID_FILE": str(descendant_file),
            "FAKE_DESCENDANT_IGNORE_TERM": "1",
        })
        proc = subprocess.Popen(
            [str(WRAPPER), "readonly", "--cwd", str(self.cwd), "--", "Wait."],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        self.wait_for_file(descendant_file)
        proc.terminate()
        stdout, stderr = proc.communicate(timeout=10)

        self.assertEqual(proc.returncode, 143, stderr)
        self.assertEqual(stdout, "")
        self.assert_process_gone(int(descendant_file.read_text(encoding="utf-8")))

    def test_normal_codex_exit_reaps_lingering_descendants(self):
        descendant_file = self.root / "normal-descendant.pid"
        result = self.run_wrapper(
            "readonly", "--cwd", str(self.cwd), "--", "Return promptly.",
            extra_env={
                "FAKE_DESCENDANT_PID_FILE": str(descendant_file),
                "FAKE_DESCENDANT_IGNORE_TERM": "1",
            },
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.wait_for_file(descendant_file)
        self.assert_process_gone(int(descendant_file.read_text(encoding="utf-8")))

    def test_missing_python_fails_before_codex_invocation(self):
        bin_dir = self.root / "minimal-bin"
        bin_dir.mkdir()
        (bin_dir / "bash").symlink_to("/bin/bash")
        env = os.environ.copy()
        env.update({
            "PATH": str(bin_dir),
            "CODEX_BIN": str(self.fake),
            "FAKE_ARGS_FILE": str(self.args_file),
            "FAKE_STDIN_FILE": str(self.stdin_file),
        })

        result = subprocess.run(
            [str(WRAPPER), "readonly", "--cwd", str(self.cwd), "--", "Do not run."],
            text=True,
            capture_output=True,
            env=env,
            check=False,
            timeout=5,
        )

        self.assertEqual(result.returncode, 69)
        self.assertIn("python3 is required", result.stderr)
        self.assertFalse(self.args_file.exists())

    def test_timeout_validation_is_decimal_and_preflighted(self):
        result = self.run_wrapper(
            "readonly", "--cwd", str(self.cwd), "--timeout", "0008", "--",
            "Accept a decimal timeout.",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        self.args_file.unlink()
        result = self.run_wrapper(
            "readonly", "--cwd", str(self.cwd), "--timeout", "0", "--",
            "Reject before invoking Codex.",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("timeout must be an integer", result.stderr)
        self.assertFalse(self.args_file.exists())

    def test_success_with_empty_final_text_is_failure(self):
        result = self.run_wrapper(
            "readonly", "--cwd", str(self.cwd), "--", "Return nothing.",
            text="  \n\t",
        )

        self.assertEqual(result.returncode, 65)
        self.assertIn("empty final response", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_malformed_jsonl_is_rejected_instead_of_leaking_raw_stream(self):
        result = self.run_wrapper(
            "readonly", "--cwd", str(self.cwd), "--json", "--", "Answer.",
            jsonl='{"type":"thread.started"}\nnot-json\n',
        )

        self.assertEqual(result.returncode, 65)
        self.assertIn("invalid Codex JSONL at line 2", result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()

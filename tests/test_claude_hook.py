import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "collector" / "claude_hook.py"
spec = importlib.util.spec_from_file_location("claude_hook", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ClaudeHookTests(unittest.TestCase):
    def test_metadata_whitelist(self):
        item = module.normalize_hook(
            {"hook_event_name": "SessionStart", "session_id": "abc",
             "cwd": "/private/project", "transcript_path": "/secrets/log",
             "prompt": "TOP SECRET", "agent_id": "agent-1"},
            tenant="org", installation="device")
        self.assertEqual(item["session_id"], "abc")
        self.assertEqual(item["lifecycle"]["event"], "SessionStart")
        data = json.dumps(item)
        for secret in ("TOP SECRET", "/private/project", "/secrets/log"):
            self.assertNotIn(secret, data)
        self.assertIsNone(item["measurement"]["input_tokens"])

    def test_rejects_unrelated_event(self):
        self.assertIsNone(module.normalize_hook(
            {"hook_event_name": "UserPromptSubmit", "session_id": "s",
             "prompt": "private"}, tenant="org", installation="device"))

    def test_spool_private_and_nonblocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            spool = Path(tmp) / "event.jsonl"
            env = dict(os.environ, YUKH_TENANT_ID="org",
                       YUKH_INSTALLATION_ID="device", YUKH_SPOOL_PATH=str(spool))
            process = subprocess.run(
                [sys.executable, str(SCRIPT)], env=env, input=json.dumps(
                    {"hook_event_name": "SessionStart", "session_id": "abc",
                     "prompt": "DO NOT SAVE"}).encode(), capture_output=True)
            self.assertEqual(process.returncode, 0)
            self.assertEqual(process.stdout, b"")
            lines = spool.read_text().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertNotIn("DO NOT SAVE", lines[0])
            self.assertEqual(json.loads(lines[0])["session_id"], "abc")
            if os.name == "posix":
                self.assertEqual(spool.stat().st_mode & 0o777, 0o600)

    def test_not_enrolled_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            spool = Path(tmp) / "event.jsonl"
            env = dict(os.environ, YUKH_SPOOL_PATH=str(spool))
            env.pop("YUKH_TENANT_ID", None)
            env.pop("YUKH_INSTALLATION_ID", None)
            p = subprocess.run([sys.executable, str(SCRIPT)], env=env,
                input=b'{"hook_event_name":"SessionStart","session_id":"abc"}')
            self.assertEqual(p.returncode, 0)
            self.assertFalse(spool.exists())


if __name__ == "__main__":
    unittest.main()

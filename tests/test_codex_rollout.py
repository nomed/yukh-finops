import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("codex_rollout", ROOT / "collector" / "codex_rollout.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def meta(sid="thread-1"):
    return {"type": "session_meta", "payload": {"id": sid, "cwd": "/private/src"}}


def event(n, in_t, out_t, cached=None, reasoning=None):
    return {"timestamp": f"2026-10-25T00:00:{n:02d}Z", "type": "event_msg",
            "payload": {"type": "token_count", "info": {
                "total_token_usage": {"input_tokens": in_t,
                                      "output_tokens": out_t,
                                      "cached_input_tokens": cached,
                                      "reasoning_output_tokens": reasoning},
                "last_token_usage": {"input_tokens": 9999, "output_tokens": 8888}
            }}}


def parse(records):
    return list(mod.extract_events((json.dumps(r) for r in records),
                                   tenant="org", installation="device",
                                   source_key="stable-test-key"))


class CodexRolloutTests(unittest.TestCase):
    def test_cumulative_converts_to_deltas_not_last_usage(self):
        rows = parse([meta(), event(1, 100, 20, 80, 5),
                      event(2, 130, 25, 90, 7)])
        self.assertEqual(len(rows), 2)
        self.assertEqual([(e["measurement"]["input_tokens"], e["measurement"]["output_tokens"])
                          for e in rows], [(100, 20), (30, 5)])
        self.assertEqual(rows[1]["measurement"]["cache_read_tokens"], 10)
        self.assertEqual(rows[1]["measurement"]["reasoning_tokens"], 2)

    def test_repeated_snapshot_no_double_count(self):
        rows = parse([meta(), event(1, 100, 20), event(2, 100, 20)])
        self.assertEqual(len(rows), 1)

    def test_replay_has_stable_ids(self):
        records = [meta(), event(1, 100, 20), event(2, 130, 25)]
        self.assertEqual([x["event_id"] for x in parse(records)],
                         [x["event_id"] for x in parse(records)])

    def test_reset_does_not_produce_negative_deltas(self):
        rows = parse([meta(), event(1, 100, 20), event(2, 2, 1)])
        self.assertEqual([x["measurement"]["input_tokens"] for x in rows], [100, 2])

    def test_never_emits_cwd_or_transcript(self):
        rows = parse([meta(), event(1, 100, 20)])
        self.assertNotIn("/private/src", json.dumps(rows))
        self.assertNotIn("last_token_usage", json.dumps(rows))

    def test_missing_metadata_and_invalid_usage_safe(self):
        rows = parse([event(1, 100, 20), meta(), event(2, -1, 1),
                      {"type":"event_msg","payload":{"type":"token_count"}}])
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()

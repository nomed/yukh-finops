"""Minimal, dependency-free fixture validation; not a provider collector.

Run: python3 -m unittest discover -s tests -v
"""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def validate_event(event):
    required = ("schema_version", "event_id", "tenant_id", "installation_id",
                "provider", "entrypoint", "session_id", "observed_at",
                "source", "measurement")
    for field in required:
        if field not in event:
            raise ValueError(f"Missing {field}")
    if event["schema_version"] != "0.1.0":
        raise ValueError("Unsupported schema")
    if event["provider"] not in ("claude-code", "codex"):
        raise ValueError("Unsupported provider")
    if event["entrypoint"] not in ("official-vscode-extension",
                                   "vscode-terminal", "standalone-cli", "other"):
        raise ValueError("Unsupported entrypoint")
    if event["measurement"].get("semantics") not in ("delta", "cumulative", "unknown"):
        raise ValueError("Unknown measurement semantics")
    for name in ("input_tokens", "output_tokens", "cache_read_tokens",
                 "cache_write_tokens", "reasoning_tokens"):
        val = event["measurement"].get(name)
        if val is not None and (type(val) is not int or val < 0):
            raise ValueError(f"Invalid {name}")
    if event["source"].get("evidence_status") not in (
        "verified", "documented", "unverified", "synthetic"
    ):
        raise ValueError("Invalid evidence status")


def ledger_delta(events):
    """Dedupe by stable ID; reject conflicting replay; never sum cumulative counts.

    This helper deliberately refuses cumulative/unknown semantics rather than
    silently corrupting the ledger. Financial allocation is out of scope.
    """
    seen = {}
    totals = {"input_tokens": 0, "output_tokens": 0}
    for event in events:
        validate_event(event)
        if event["measurement"]["semantics"] != "delta":
            raise ValueError("Cannot sum cumulative/unknown events as deltas")
        identity = (event["tenant_id"], event["installation_id"],
                    event["provider"], event["event_id"])
        canonical = json.dumps(event, sort_keys=True, separators=(",", ":"))
        if identity in seen:
            if seen[identity] != canonical:
                raise ValueError("Conflicting event replay")
            continue
        seen[identity] = canonical
        for field in totals:
            value = event["measurement"].get(field)
            if value is not None:
                totals[field] += value
    return totals


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.event = json.loads((ROOT / "fixtures" / "usage-event.synthetic.json").read_text())

    def test_synthetic_fixture_contract(self):
        validate_event(self.event)
        self.assertEqual(self.event["source"]["evidence_status"], "synthetic")

    def test_deduplication(self):
        self.assertEqual(ledger_delta([self.event, self.event]),
                         {"input_tokens": 100, "output_tokens": 50})

    def test_conflicting_replay_is_error(self):
        copy = json.loads(json.dumps(self.event))
        copy["measurement"]["input_tokens"] = 999
        with self.assertRaises(ValueError):
            ledger_delta([self.event, copy])

    def test_cumulative_rejected(self):
        self.event["measurement"]["semantics"] = "cumulative"
        with self.assertRaises(ValueError):
            ledger_delta([self.event])

    def test_missing_tokens_are_not_zeroed_in_payload(self):
        self.assertIsNone(self.event["measurement"]["cache_read_tokens"])
        validate_event(self.event)

    def test_negative_usage_rejected(self):
        self.event["measurement"]["input_tokens"] = -1
        with self.assertRaises(ValueError):
            validate_event(self.event)


if __name__ == "__main__":
    unittest.main()

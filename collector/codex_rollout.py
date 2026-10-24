#!/usr/bin/env python3
"""Read-only Codex rollout usage adapter (experimental).

Reads explicit rollout JSONL paths, emits ONLY normalized usage events to stdout.
No network, no auth, no prompts, no tool content, no raw rollout records.

Counts from total_token_usage are CUMULATIVE and converted to non-negative deltas.
A counter reset creates a new epoch rather than a negative delta. Never combines
last_token_usage with total_token_usage. Fixtures do not certify editor support.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

USAGE_KEYS = {
    "input_tokens": "input_tokens",
    "output_tokens": "output_tokens",
    "cached_input_tokens": "cache_read_tokens",
    "reasoning_output_tokens": "reasoning_tokens",
}
MAX_LINE_BYTES = 2 * 1024 * 1024


def counts(obj: object) -> dict | None:
    if not isinstance(obj, dict):
        return None
    selected = {}
    for source, target in USAGE_KEYS.items():
        value = obj.get(source)
        if value is not None and (type(value) is not int or value < 0):
            return None
        selected[target] = value
    if selected["input_tokens"] is None or selected["output_tokens"] is None:
        return None
    return selected


def extract_events(lines, *, tenant: str, installation: str, source_key: str):
    """Yield normalized usage delta events, never raw transcript metadata.

    source_key must be a stable non-sensitive identifier for this rollout,
    e.g. opaque persisted file fingerprint from the caller. No filenames
    are included in events.
    """
    session = None
    previous = None
    epoch = 0
    for ordinal, raw in enumerate(lines, start=1):
        if len(raw) > MAX_LINE_BYTES:
            continue
        try:
            record = json.loads(raw)
        except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
            continue
        if not isinstance(record, dict):
            continue
        payload = record.get("payload")
        if not isinstance(payload, dict):
            continue
        if record.get("type") == "session_meta":
            # Read only id; NEVER persist entire session_meta (contains cwd, etc.)
            sid = payload.get("id")
            if isinstance(sid, str) and 0 < len(sid) <= 256:
                session = sid
            continue
        if session is None or record.get("type") != "event_msg" or payload.get("type") != "token_count":
            continue
        info = payload.get("info")
        if not isinstance(info, dict):
            continue
        cumulative = counts(info.get("total_token_usage"))
        if cumulative is None:
            continue
        if previous is None:
            # First observation represents lifetime usage *to this point*.
            # If original log starts in the middle, this is not a turn delta.
            delta = cumulative
        else:
            core = ("input_tokens", "output_tokens")
            reset = any(cumulative[k] < previous[k] for k in core)
            if reset:
                epoch += 1
                delta = cumulative
            else:
                delta = {
                    k: (None if v is None or previous.get(k) is None
                        else v - previous[k])
                    for k, v in cumulative.items()
                }
                # Optional counters may reset independently; unknown rather than negative.
                delta = {k: (None if v is not None and v < 0 else v)
                         for k, v in delta.items()}
        previous = cumulative
        if not any((v or 0) > 0 for v in delta.values()):
            continue
        timestamp = record.get("timestamp")
        if not isinstance(timestamp, str) or len(timestamp) > 64:
            continue
        event_hash = hashlib.sha256(
            f"{source_key}:{session}:{ordinal}:{epoch}".encode("utf-8")
        ).hexdigest()
        yield {
            "schema_version": "0.1.0",
            "event_id": event_hash,
            "tenant_id": tenant,
            "installation_id": installation,
            "provider": "codex",
            "entrypoint": "other",
            "session_id": session,
            "turn_id": None,
            "observed_at": timestamp,
            "source": {"kind": "local-session-event",
                       "source_version": "codex-rollout-cumulative-v0",
                       "evidence_status": "unverified"},
            "measurement": {
                "semantics": "delta",
                "input_tokens": delta["input_tokens"],
                "output_tokens": delta["output_tokens"],
                "cache_read_tokens": delta["cache_read_tokens"],
                "cache_write_tokens": None,
                "reasoning_tokens": delta["reasoning_tokens"]
            },
            "project_reference": None
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse local Codex token counters (experimental)")
    parser.add_argument("rollout", type=Path, help="Existing rollout JSONL path")
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--installation", required=True)
    args = parser.parse_args()
    if not args.rollout.is_file() or args.rollout.is_symlink():
        parser.error("Expected regular non-symlink rollout file")
    # The name/path is used only for deterministic local event IDs.
    # Never send it as a field in the output.
    key = hashlib.sha256(str(args.rollout.resolve()).encode()).hexdigest()
    with args.rollout.open("r", encoding="utf-8", errors="replace") as handle:
        for event in extract_events(handle, tenant=args.tenant,
                                    installation=args.installation,
                                    source_key=key):
            sys.stdout.write(json.dumps(event, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Capture Claude Code lifecycle hook metadata locally, without prompts or API keys.

This is a prototype. It does NOT claim to record token usage. User-level Claude
settings and the official VS Code extension require hands-on compatibility tests.

Usage:
  Configure a Claude Code hook to invoke this script (see docs/adapters/claude.md).
  The hook JSON arrives on stdin; the collector appends a whitelisted event locally.

No network connections are made. Failure is non-blocking (exit 0).
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone


ALLOWED_HOOK_EVENTS = {"SessionStart", "SessionEnd", "SubagentStart", "SubagentStop"}
MAX_INPUT_BYTES = 64 * 1024
DEFAULT_SPOOL = Path.home() / ".local" / "state" / "yukh-finops" / "claude-hooks.jsonl"


def normalize_hook(payload: object, *, tenant: str, installation: str) -> dict | None:
    """Only non-sensitive identifiers: never persist raw payload, cwd or transcript."""
    if not isinstance(payload, dict):
        return None
    event = payload.get("hook_event_name")
    session = payload.get("session_id")
    if event not in ALLOWED_HOOK_EVENTS or not isinstance(session, str) or not session:
        return None
    if len(session) > 256:
        return None

    # Subagent agent_id is optional and version dependent.
    agent_id = payload.get("agent_id")
    if not isinstance(agent_id, str) or len(agent_id) > 256:
        agent_id = None

    # A hook can fire multiple times legitimately. Event ID incorporates an
    # individual invocation nonce, so no false dedupe is claimed.
    import uuid
    event_id = str(uuid.uuid4())
    return {
        "schema_version": "0.1.0",
        "event_id": event_id,
        "tenant_id": tenant,
        "installation_id": installation,
        "provider": "claude-code",
        "entrypoint": "other",  # Hook alone cannot authenticate GUI vs CLI.
        "session_id": session,
        "turn_id": None,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source": {"kind": "hook", "source_version": "claude-hook-v0",
                   "evidence_status": "unverified"},
        "measurement": {"semantics": "unknown", "input_tokens": None,
                        "output_tokens": None, "cache_read_tokens": None,
                        "cache_write_tokens": None, "reasoning_tokens": None},
        "project_reference": None,
        "lifecycle": {"event": event, "agent_id": agent_id},
    }


def secure_append(path: Path, item: dict) -> None:
    """Private local queue; no cwd/transcript, no source content."""
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.exists() and path.is_symlink():
        raise OSError("Symlink spool path rejected")
    import os
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as file:
            file.write(json.dumps(item, separators=(",", ":")) + "\n")
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        raise


def main() -> int:
    try:
        data = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        if len(data) > MAX_INPUT_BYTES:
            return 0
        payload = json.loads(data)
        tenant = os.environ.get("YUKH_TENANT_ID", "").strip()
        installation = os.environ.get("YUKH_INSTALLATION_ID", "").strip()
        if not tenant or not installation or len(tenant) > 256 or len(installation) > 256:
            return 0  # Explicit enrollment is required; don't forge anonymous identities.
        event = normalize_hook(payload, tenant=tenant, installation=installation)
        if event:
            secure_append(Path(os.environ.get("YUKH_SPOOL_PATH") or DEFAULT_SPOOL), event)
    except (OSError, ValueError, TypeError, UnicodeDecodeError):
        # Hooks must not interrupt the user's agent. Diagnostics to be implemented.
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

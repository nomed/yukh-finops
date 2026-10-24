# Codex local rollout adapter — experimental

The read-only parser `collector/codex_rollout.py` consumes **explicit** Codex rollout JSONL files and writes **only token usage events** to stdout, for integration tests and eventual ingestion.

```bash
python3 collector/codex_rollout.py \
  "$HOME/.codex/sessions/YYYY/MM/DD/rollout-EXAMPLE.jsonl" \
  --tenant example --installation device-123
```

For a user who configured `CODEX_HOME`, the session directory may differ. The tool does not crawl the disk or upload information; caller must supply the path. Test with a throwaway session or redacted synthetic fixture.

## Observed upstream format (not validated against a local authenticated session yet)

A session metadata event provides an ID. Later `event_msg` / `token_count` events may contain `info.total_token_usage` (cumulative counters) and `last_token_usage`. The adapter intentionally uses **only cumulative counters**, computes deltas, and never adds `last_token_usage`. Duplicate snapshots with unchanged counters are ignored. Missing optional counters remain null.

Important limits:
- This is **not** a proof that the official Codex VS Code extension stores identical rollouts. That must be tested.
- Only input/output counter decreases trigger a new counter epoch; resets or corrections may require further version-specific handling.
- First cumulative observation assumes the file contains its initial history. Truncated files can overcount.
- Event IDs are stable for a snapshot of the same file (path hash, session, line, epoch). File rewrites/compaction or moves can cause changes. Ingestion needs a stronger persisted source identity.
- Some token categories are **subsets**: cached input tokens are generally included in reported total input and reasoning output in output; don't blindly sum the fields. Semantics require provider-version verification.
- No cost equivalence, SSO, project resolution, live tailing, server sync, durable cursor or security hardening yet.
- A real editor/CLI verification and fixtures with explicit consent are required before marking support VERIFIED.

Upstream research: [OpenAI Codex](https://github.com/openai/codex); see [compatibility matrix](../COMPATIBILITY.md) and [research notes](../research/2026-10-24-provider-surfaces.md).

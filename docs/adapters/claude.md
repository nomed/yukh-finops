# Claude Code lifecycle hook prototype

**Status:** code committed; compatibility with official Claude Code VS Code extension **not yet tested**. No token usage is measured by this hook. Hook events only establish session/lifecycle identities.

## How to exercise in a disposable account

1. Enroll this installation with unique tenant and installation identifiers. These identifiers are supplied by the organization; do **not** derive them from computer username or Claude email.
2. Install Python 3, clone the repo, and configure your personal Claude Code settings with a **SessionStart** and **SessionEnd** command hook. Follow Anthropic's [current hook configuration docs](https://code.claude.com/docs/en/hooks); validate the syntax against your installed version.
3. Use the following example after replacing `/absolute/path` and environment values. Set the environment in your shell or managed process launcher; graphical VS Code may have a different environment.

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "python3 /absolute/path/yukh-finops/collector/claude_hook.py"
      }]
    }],
    "SessionEnd": [{
      "hooks": [{
        "type": "command",
        "command": "python3 /absolute/path/yukh-finops/collector/claude_hook.py"
      }]
    }]
  }
}
```

4. Start Claude Code from CLI, then from the official VS Code extension; compare `session_id` and the private `~/.local/state/yukh-finops/claude-hooks.jsonl` spool. Test resume, subagents, and workspaces. **Neither case has been verified here**.
5. Check token-usage separately with Anthropic's [OpenTelemetry guide](https://code.claude.com/docs/en/monitoring-usage). Do not claim it is covered by the hook.

## Scope and limits

- Only accepted lifecycle events + session and optional agent ID are written; never prompt, cwd or transcript path.
- No network, no credentials or API billing, no project selection yet, no SSO, no cost aggregation.
- Event `entrypoint=other` because a hook cannot reliably tell whether the invocation came from VS Code or standalone CLI.
- Missing enrollment -> no file written. Failures are non-blocking and currently silent; an enterprise build must have visible health diagnostics.
- Spool uses owner-only permissions on POSIX. This is **not** encrypted persistence, production queueing, device attestation or anti-tampering. Windows ACL and enterprise rollout remain untested.
- Hook IDs are generated per invocation; duplicate hook delivery can produce duplicate lifecycle events. Usage-ledger idempotency requires stronger source-specific identity rules.

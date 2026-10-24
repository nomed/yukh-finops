# Compatibility matrix — evidence status

All rows begin **UNVERIFIED** until reproducible hands-on tests are committed. 'Available documentation' is not proof of coverage of a particular extension release.

| Agent | Entrypoint | Session identity | Per-turn tokens | Subagents | Attribution hooks | Status |
|---|---|---|---|---|---|---|
| Claude Code | CLI | Investigate hooks/OTel | Investigate OTel/token categories | Investigate nested sessions | Investigate SessionStart/cwd | UNVERIFIED |
| Claude Code | Official VS Code extension | Verify same session/OTel surface | Verify native extension mode | Verify | Verify hook invocation | UNVERIFIED |
| Claude Code | VS Code integrated terminal | Verify CLI equivalence | Verify | Verify | Verify | UNVERIFIED |
| Codex | CLI | Investigate session JSONL/events | Investigate token_count and cache/reasoning fields | Investigate | Investigate local event surfaces | UNVERIFIED |
| Codex | Official VS Code extension | Investigate app-server/session store | Verify token event availability | Verify | Verify without replacing extension | UNVERIFIED |
| Codex | VS Code integrated terminal | Verify CLI equivalence | Verify | Verify | Verify | UNVERIFIED |

## Investigation surfaces (not yet certified)
- Claude Code: Agent SDK (for sessions **we create**, not automatic instrumentation of third-party sessions); CLI lifecycle hooks; optional native OTel.
- Codex: TypeScript SDK and app-server (for controlled clients); CLI/session logs and locally emitted usage events. SDK availability does **not** demonstrate passive observation of the official extension.
- VS Code telemetry: feature- and version-specific; never assume that VS Code's generic agent observability captures both extensions.

## Verification log template
| Date | OS | VS Code | Extension | CLI version | Auth | Fixture | Expected | Observed | Evidence | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | Subscription | TBD | TBD | TBD | TBD | PENDING |

Track unsupported values as `null` with a reason; never silently treat a missing token category as zero.

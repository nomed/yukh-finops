# Provider surfaces — 2026-10-24 desk research

**Evidence level: documented, NOT hands-on verified.** No local VS Code instance or authenticated provider session was run for this investigation. Links are primary/official references unless noted.

## Claude Code

- Claude Code official VS Code extension: https://code.claude.com/docs/en/vs-code
- Claude Code lifecycle hooks: https://code.claude.com/docs/en/hooks and https://claude.com/resources/articles/how-to-configure-hooks
- Claude Code official telemetry: https://code.claude.com/docs/en/monitoring-usage

**Documented**: hook payloads include `session_id`, `transcript_path`, `cwd`, `hook_event_name`. Settings can be applied at user level (`~/.claude/settings.json`) or project scope. This makes session attribution plausible without custom SDK-managed execution. Need to independently test whether every interaction in the **official graphical VS Code extension** fires those same hooks and exports token metrics.

**Key caveat**: Claude Agent SDK is for sessions an SDK client initiates. It does not, by itself, attach to an arbitrary already-open Claude Code editor session. OpenTelemetry token/cost metrics are not the same as subscription invoices.

## Codex

- OpenAI Codex app-server: https://developers.openai.com/codex/app-server
- Codex open source: https://github.com/openai/codex
- Codex SDK: https://developers.openai.com/codex/sdk
- Codex IDE extension: https://developers.openai.com/codex/ide

**Documented**: Codex app-server underpins rich clients including the VS Code extension, with thread/turn/events. SDK/app-server integrations orchestrate controlled sessions; they are not proof of a supported, passive metering API for another client's sessions. Inspect app-server notifications and local session files for token usage and stable event IDs, then **verify empirically** on both CLI and VS Code with a subscription account.

## VS Code is not a universal telemetry source

- https://code.visualstudio.com/docs/agents/guides/monitoring-agents
- https://code.visualstudio.com/docs/agent-customization/hooks
- https://code.visualstudio.com/docs/configure/telemetry

**Critical distinction**: VS Code's OpenTelemetry documentation describes its supported agent runtimes/harnesses, including Claude in some Copilot-managed workflows. It does **not** certify telemetry for the separate official Anthropic Claude Code extension or OpenAI Codex extension. Provider hooks differ. VS Code explicitly notes that third-party extensions may send independent telemetry.

## Implications for engineering

1. Prioritize non-invasive **user-level hook/OTel configuration for Claude**; prove official extension coverage with real sessions.
2. For Codex, prefer supported local emission/session events; read local JSONL only if permitted by documented schema and privacy constraints. Version-pin parsers and track provenance.
3. Build a local integration diagnostic: source detected, version, session observation, usage event count, completeness, and last sync.
4. Avoid relying on editor settings for mandatory enforcement; personal configurations may be removed. Separate supported visibility from managed-policy enforcement.
5. Store anonymized counts and stable IDs, not transcripts, inputs, tool outputs, secrets or developer source code. Local transcript parsing, if required, must be strictly whitelist-only.

## Reproducibility checklist for each spike
```
OS/version:
VS Code/version:
Extension identifier/version:
Claude or Codex CLI/version:
Authentication: subscription / API
Entrypoint: official GUI extension / integrated terminal / terminal
Settings/hook effective source:
Session/thread ID visible:
Usage counter types actually visible:
Resumed session: same or new ID:
Subagent attribution:
Raw metadata fixture (redacted):
Observed gaps:
Reviewer + date:
```

Result statuses: **DOCUMENTED** (upstream only), **VERIFIED** (real, evidenced session), **BLOCKED** (cannot access/observe), **UNSUPPORTED** (explicitly absent), **UNKNOWN**. No production claim on DOCUMENTED status.

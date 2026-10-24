# Yukh FinOps

Open-source, self-hostable metering and cost attribution for AI coding agents, part of the Yukh suite.

## Product principles

- **Works where developers already work:** official Claude Code and Codex experiences in VS Code **and** their CLIs; no mandatory replacement UI or launcher.
- **Subscription-friendly:** no provider API key or pay-per-token API requirement for telemetry. Token usage is measured separately from allocated subscription spend.
- **Local-first collection:** credentials remain with the user; a local agent buffers usage offline and sends metadata to the control plane.
- **Identity and attribution:** business identity comes from organizational SSO; repo/issue/session and project references support attribution.
- **Pluggable business systems:** projects, commesse and cost centers originate from an external Project Provider contract, not an embedded ERP.
- **Privacy by default:** do not ingest source code, prompts, conversation content or secrets.
- **Evidence before enforcement:** compatibility with particular editor/CLI/provider versions and bypass resistance must be demonstrated by tests, not assumed.

## Status

**Planning / technical discovery. Not production-ready.** Neither official VS Code extension has yet been validated end-to-end by this project. Enterprise enforcement is a research milestone, not a current claim.

See [Sprint 0 plan](docs/SPRINT-0.md), [architecture ADR](docs/adr/0001-boundaries.md), [provider contract](docs/contracts/project-provider.md), and [compatibility matrix](docs/COMPATIBILITY.md).

## Planned components

`collector` (local adapters and offline spool), `server` (ingestion, session registry, immutable usage ledger, cost allocation), `dashboard` (RBAC-scoped views), `contracts` (versioned schemas and APIs), and example `project-provider` adapters.

Apache-2.0 vs other license: **not yet decided**; choose explicitly before accepting contributions.

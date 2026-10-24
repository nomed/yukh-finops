# Sprint 0 — Evidence-led discovery and contracts

## Goal
Demonstrate whether we can observe **real use** of **Claude Code and Codex**, launched both in official VS Code extensions and in terminals, on user-owned subscription accounts, without proxies, per-token APIs, or changes to user workflows.

## In-scope acceptance experiments
For **each** provider × entrypoint (official VS Code extension, standalone CLI, VS Code integrated terminal) × platform (macOS, Windows native/WSL as applicable, Linux):
1. Start fresh session; record actual CLI/extension and OS versions, authentication mode, repository root and identity.
2. Generate controlled prompt and tool activity; collect session/thread ID, turn ID, model, input/output/cache/reasoning token availability, and timestamps.
3. Resume session and start subagents where supported; verify no duplicates and understand missing coverage.
4. Switch repo or working directory; verify project mapping and ambiguity handling.
5. Disconnect network; recover offline buffer, replay and verify idempotent ingestion.
6. Change provider account; ensure local agent identity remains organizational and mismatches are auditable.
7. Disable/modify instrumentation; assess bypass paths and classify enforcement capabilities honestly.
8. Compare native counters versus observed events; record completeness, source and confidence.

## Evidence requirements
Store redacted, reproducible fixtures (never prompts or secrets), documented commands, exact versions, OS, configuration, expected and actual counters. Grade: **verified** (hands-on evidence), **documented** (upstream docs only), **hypothesis** or **unsupported**. No default 'supported' statuses.

## Deliverables / gates
- D0: reference source inventory and measurement schema; no provider assumptions.
- D1: verified provider/entrypoint compatibility matrix and gaps; demonstrate unattended extension observation or document blockers.
- D2: versioned external Project Provider contract plus reference static adapter design.
- D3: spike collector/ingestion with idempotency, durable queue and provenance.
- D4: enterprise policy threat model (observe vs enforce) plus GDPR/employee monitoring assessment.
- Go/no-go: no 'mandatory' enterprise rollout until session attribution, reliability, privacy, update strategy, and bypass controls have been validated.

## Suggested sequence
P0 inventory and fixtures → P1 Claude CLI/VS Code spike → P2 Codex CLI/VS Code spike → P3 schema/Project Provider contract → P4 local collector prototype → P5 ingestion/ledger → P6 identity and attribution → P7 cost models → P8 enterprise pilot.

## Explicit non-goals
Running or replacing Claude/Codex; shared provider credentials; scraping prompts; inventing token counts; claiming token-based charges for subscriptions; implementing a company's ERP.

## Initial definition of done
A user opens official Claude Code/Codex in VS Code and works normally; the test proves what metadata is and is not collected, and whether an SSO-linked session is assigned to a project or flagged as unassigned. Production enforcement is excluded until independently validated.

# ADR-0001: Separate local metering, central ledger and external business reference data

Status: **Proposed** · Date: 2026-10-24

## Context
Developers use Codex and Claude Code via official VS Code extensions or CLI with subscription accounts. Organizations need named attribution to commessa/cost center while retaining control of their business reference data.

## Decision
1. **Local agent + provider adapters** observe native telemetry/event surfaces and buffer encrypted-at-rest where available. They do not broker LLM requests, touch account credentials or require users to launch the AI from Yukh.
2. **Central ingestion + immutable event ledger** deduplicate by provider-specific stable event ID or canonical content identity, store provenance and completeness, then derive session aggregates.
3. **Identity layer** binds local installation/device to verified organizational subject (OIDC subject + issuer); never trust OS username or provider email as authoritative.
4. **External Project Provider** is a separately deployable HTTP service under a versioned contract; every company implements its own adapter to ERP, Jira, GitHub, CSV, etc. Yukh retains references and historical snapshots only.
5. **Cost semantics** distinguish provider API invoiced cost, list-price-equivalent estimate, and subscription spend allocated using explicit policy. Never present estimates as actual invoices.
6. **Policy modes** Observe warns on unknown association; Enforce requires independently verified technical chokepoints and managed controls. An easily removable editor plugin is not sufficient enforcement.
7. **Privacy** no prompt/code payloads by default; event collection is minimal, access-scoped, retention-configurable and subject to appropriate employee-data governance.

## Trade-offs
Passive collection minimizes developer friction but can lose coverage after upstream version changes; adapters must declare version compatibility and data completeness. Subscription consumption cannot directly determine actual monetary spend.

## Deferred decisions
Runtime language, transport details, SQLite vs alternative local spool, OIDC provider, UI framework, deployment topology, licensing. Determine via spikes rather than assumptions.

# ADR-0002: Normalize usage provenance, not provider prices

Status: **Proposed** · 2026-10-24

- Events are **append-only**, with stable event IDs and idempotent server ingestion; corrections append adjustments, not edits.
- `delta` and `cumulative` observations must never be added together blindly. The adapter must identify semantics and aggregation scope before ledger materialization.
- Unknown/unavailable token categories are `null`, not 0. Cache/reasoning counts might overlap provider-defined input/output categories; expose separately, with provenance, and don't sum into a grand total without a documented model.
- Treat actual API billed spend, public list-price-equivalent estimates, and allocated subscription cost as **three different financial measures**.
- Model costs are revision-dependent and subscription spend depends on enterprise allocation policy, not token price.
- Privacy: forward whitelisted usage fields and identifiers only. No prompts, full transcripts, path details or provider auth material are required in the central ledger.
- Synthetic fixtures prove the schema shape, **not** provider support or production accuracy.

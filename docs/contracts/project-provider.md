# Project Provider Contract v0 (proposal)

Yukh FinOps does **not** own enterprise commesse. Each tenant configures a trusted external Project Provider URL and authentication mechanism; it can be a company's microservice or a demo static adapter. Names and examples below are **draft**, not implemented endpoints.

## Resource model

`ProjectRef`: { provider_id, external_project_id, code, display_name, status, cost_center_id?, valid_from?, valid_to?, updated_at }.

`CostCenterRef`: { provider_id, external_cost_center_id, code, display_name, status, updated_at }.

`Assignment`: { issuer, subject, external_project_id, role?, valid_from?, valid_to? } (optional; user authorization may instead reside in the enterprise IAM).

`ContextMapping`: { vcs_remote?, repository_id?, path_pattern?, issue_key?, external_project_id, priority }.

Stable IDs are namespaced by provider/tenant; codes and display names may change. Preserve attribution history with a reference and snapshot timestamp.

## Read API (proposal)
- `GET /v1/capabilities`: version, pagination, features and health.
- `GET /v1/projects?cursor=&limit=&updated_since=`: paged active and inactive projects.
- `GET /v1/projects/{project_id}`: stable project reference.
- `GET /v1/cost-centers?cursor=&limit=`: paged centers.
- `GET /v1/assignments?subject=&issuer=`: optional project eligibility.
- `POST /v1/resolve`: determine project candidates from VCS remote, repository identifier, cwd and issue references. The provider returns ranked candidates and `requires_user_choice`; never guess from ambiguous context.

Response metadata: `schema_version`, `provider_id`, `request_id`, `retrieved_at`. Required stable pagination/sorting; ETag or modified-since caching where offered. Auth: tenant-managed service credentials (mTLS or OAuth2 client credentials), TLS in transit; minimum scopes; no end-user Claude/OpenAI credentials.

## Failure semantics
When the provider is offline, use last verified mappings with expiry and record a provenance flag, or classify the session **unattributed**. Never silently map an unknown project to a default commessa. Provider responses cannot rewrite immutable past session attribution; corrections require an auditable adjustment.

## Example resolve exchange
```json
{
  "context": {
    "vcs_remote": "https://github.com/acme/example.git",
    "issue_key": "CDS-123"
  },
  "subject": {"issuer":"https://sso.example.com","sub":"00u123"}
}
```

```json
{
  "schema_version":"0.1",
  "provider_id":"acme-erp",
  "candidates":[{"external_project_id":"cds-2026","confidence":"rule-match","reason":"repository mapping"}],
  "requires_user_choice":false
}
```

**Security:** treat paths and VCS URLs as sensitive metadata; minimize, normalize and redact before export as configured. Provider cannot receive prompts, source files or secrets.

## Next steps
Write OpenAPI 3.1 and JSON Schema; add conformance fixture tests; build reference static-file provider and a sample enterprise adapter; version independently of collector.

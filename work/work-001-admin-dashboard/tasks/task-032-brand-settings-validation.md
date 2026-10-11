# Task 1.10.1 — Brand settings validation and persistence
**Owner:** Gemini
**Status:** Completed
**Work item:** Work 001
## Objective/context
Harden existing GET/PUT /api/v1/admin/storefront/brand for the Settings UI. Read work/GEMINI_WORKFLOW_PROMPT.md, then this work's README/tasks/decisions/coordination. Reuse existing model, routes and schema; no new settings architecture.
## Scope/contract
- Names: trim, nonempty, max120 characters (align DB constraints), reject control characters and unknown payload fields. ownerName/name required for full UI PUT, retain documented omitted-field semantics for other callers.
- Optional instagramUrl/whatsappUrl: blank or null explicitly clears; omitted preserves. Validate absolute HTTP(S) URLs with host, reject credentials, javascript/data/file/relative links and oversized values (max2048 or DB-safe limit). HTTPS preferred by UI; server must at least reject unsafe schemes.
- GET must not fabricate demo WhatsApp/Instagram values or mutate on a read; return actual persisted record or documented safe missing-record response. No secrets/provider configuration in this endpoint.
- Maintain existing aliases/auth. Response returns canonical persisted data. No changes to frontend, deployments or unrelated campaigns.
## Dependencies and files
Depends on: 1.10
Dependency context: Existing BrandSettingsOut/Update and model; frontend template uses current API already.
Relevant: backend/app/schemas/storefront.py, backend/app/api/v1/admin.py, backend/app/models/storefront.py, backend/tests/, docs/api-admin.md.
## Tests/security
- TC01: Valid update persists trimmed values and public brand reads reflect update (`test_admin_get_and_update_brand_settings`). Pass.
- TC02: Blank/null optional clears, omitted preserves; invalid empty/too-long names rejected with 422. Pass.
- TC03: Unsafe/malformed URLs (javascript:, relative, embedded auth credentials) and extra payload fields rejected with 422. Pass.
- TC04: Unauthenticated (401) and non-admin customer (403) GET/PUT rejected with unchanged DB. Pass.
- TC05: GET on missing record returns safe defaults without inserting rows or fabricating fake contact links. Pass.

All 3 targeted tests passing in `tests/test_storefront.py -k "brand"`. No push or deployment. Ready for Codex 1.10.2 UI integration.

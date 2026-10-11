# Task 1.10 — Settings V1 scope/API audit
**Owner:** Codex
**Status:** Completed
**Work item:** Work 001
## Objective and scope
Replace the unfinished Settings placeholder with supported persisted brand profile settings, preserving supplied admin shell. V1 fields: store name, owner name, Instagram URL and WhatsApp URL. Payment credentials, admin roles, shipping rules, notifications and vault secrets are out of scope until separately contracted; do not imply those controls exist.
## Dependencies
Depends on: None
Dependency context: Existing GET/PUT /admin/storefront/brand and BrandSettings model. Both endpoints require administrator authorization.
## Audit and decisions
Existing endpoint accepts unbounded/unvalidated names/URLs; PUT ignores null optional links; GET inserts demo contact values if brand missing. UI should load API data and never supply business defaults. Gemini backend hardening contract1.10.1; Codex UI1.10.2 can develop against current valid payload while backend acceptance waits.
## Verification
Read routes, schema and placeholder; no runtime mutation for audit. Completed scope and pickup-ready contracts; no push.

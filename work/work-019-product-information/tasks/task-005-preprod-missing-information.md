# Task 19.5 — Diagnose missing preprod product information

**Owner:** Codex
**Status:** Completed

## Scope / dependencies
- Depends on: 19.4
- Blocked by: None
Compare local/preprod Heart Bear detail data and UI. Identify stale backend deployment versus missing DB-managed defaults. No frontend hardcoded copy or unapproved DB/deployment changes.

## Verified evidence
2026-10-24: localhost product3 supplies all six resolved defaults; browser-visible preprod /api/v1/products/3 returns null for all six. Actual dev product page omits disclosures; existing accordion filters empty fields as intended. Direct CLI public HTTP is Cloudflare403, browser API inspection succeeds.

## Acceptance / next action
Read-only VPS inspection to distinguish code/defaults mismatch; report exact repair/dependency. Retain19.4 API/SEO/no-write tests as regression requirements if code changes needed. No security-boundary change for diagnosis; never print env secrets/customer DB data. Public product fields only. Next action: inspect preprod container revision/resolver/default-row availability, report findings.

## Return — 2026-10-24
Root cause confirmed by read-only VPS inspection: sulocraft-preprod-api-1 lacks /app/app/services/product_information.py, while ProductInformationDefaults row exists with all6 nonblank fields. Local19.4 resolver supplies those defaults; preprod product3 API still returns all6 null. No frontend regression/content loss; running preprod backend is older than19.4.
Repair: deploy tested backend revision through existing preprod deployment automation, then verify public product API and visible six accordions. Do not hardcode UI fallback text, overwrite products/defaults or manually copy individual Python files. GitHub backend workflow only auto-runs for backend/docker/secrets/workflow path changes; recent frontend-only pushes do not trigger it.
Security: read-only public API and boolean-only default-row presence check; no secrets/customer data printed, no DB writes/services/revision changes. No new code/tests necessary for diagnosis;19.4 test evidence retained, not rerun. Remote deploy/repair acceptance NOT performed. Evidence reports/task-005-preprod-diagnosis.json. No Gemini code task needed.

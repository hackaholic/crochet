# Task 1.10.2 — Settings brand profile UI
**Owner:** Codex
**Status:** Completed
**Work item:** Work 001
## Objective/scope
Replace Settings placeholder with reusable API-loaded brand form (name, ownerName, instagramUrl, whatsappUrl). Preserve supplied admin design. No business defaults, secret forms, roles/payment/shipping controls.
## Dependencies
Depends on: 1.10
Dependency context: Existing valid GET/PUT brand API supports implementation. Final backend validation/clear-link acceptance depends on1.10.1 return; do not declare it complete early.
## Relevant files
src/admin/pages/SettingsPage.tsx, src/admin/services/brandSettings.ts, src/admin/AdminApp.tsx; focused tests.
## Tests/security
TC01 API values load; trim validated names/URLs and save canonical response.
TC02 empty/oversized/control names, unsafe URL blocked without request.
TC03 loading/retry/save failure safe; dirty inputs retained after failure.
TC04 credentialed request and administrator guard retained; backend negative evidence in1.10.1.
Local frontend rebuild/browser verify; real mutations limited to no-change save. Final field clearing tests after Gemini return. No push.

## Local return / remaining dependency
Frontend implementation complete:11 focused tests and typecheck pass; Docker rebuilt/restarted. Real local Settings loads persisted brand/owner/contact fields, trim-only no-change save succeeds and returns canonical Sulocraft.390px viewport/pagewidth390. Screenshot /tmp/sulocraft-admin-settings.png. Raw errors hidden, fields escaped, credentialed existing transport retained. Final acceptance awaits Gemini1.10.1 server validation/optional-link behavior; no backend validation claimed from UI tests. No push. Codex can proceed with independent test coverage.

## Final frontend return after Gemini1.10.1
Server return reviewed; actual DB limits100 names/255 links centralized and used by form/validation. Current tests:3 Settings component tests plus9 validation/transport tests pass, typecheck passes. API/frontend Docker rebuilt/restarted. Real Settings optional Instagram clearing saved and persisted after re-entering page, then original link restored with success; mobile390/page390, actual maxLength100/255 verified. No provider secrets exposed, raw errors hidden, dirty edits retained. Gemini reports3 backend brand tests passing; not rerun unnecessarily. Server null-name/internal-control gap tracked separately in1.10.3; broader admin acceptance must retain that open backend finding. Frontend complete; no push/deploy.

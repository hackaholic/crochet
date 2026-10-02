# Task 10.9 — Evergreen occasion rules

**Owner:** Gemini (backend/admin API), Codex (frontend admin controls and integration)  
**Status:** Completed (Implementation verified locally with full backend test suite, frontend unit tests, and automated API verification suite `scripts/verify_api.py`)

## Requirement

> **Superseded on 2026-10-03 by Task 10.18 / DEC-010-010:** the owner now requires exactly five initial enabled occasions (Birthday, Just Because, Anniversary, Baby Shower, Wedding), and admin must be able to toggle every occasion. This file records the earlier implementation contract only; do not use it as the current behavior spec.

Keep **Birthday**, **Anniversary**, **Wedding**, and **Baby Shower** visible all year. They are evergreen core occasions. Other occasions such as Valentine's Day, Diwali, Mother's Day, Father's Day, Christmas, Decor, and future campaigns remain admin-controlled and may be enabled, disabled, or scheduled.

## Backend requirements (Gemini)

1. Treat the existing stable database IDs `birthday`, `anniversary`, `wedding`, and `babyshower` as evergreen. Preserve these IDs so existing product associations and links keep working; do not create a duplicate `baby-shower` row.
2. Repair existing database seed records so these four are active year-round with no `starts_at`/`ends_at` schedule. Create any missing core records idempotently without overwriting admin-authored copy, image, ordering, or product associations.
3. Ensure public `occasion_grid` resolution always includes the four evergreen records and applies enabled/schedule filtering only to non-evergreen occasions. Keep the existing admin ordering and API response contract.
4. Prevent admin API updates from disabling, deleting, or assigning seasonal date windows to the evergreen records. Return a clear validation error for prohibited changes. Keep seasonal records fully manageable.
5. Add tests for existing-DB seed repair, repeat seeding, evergreen visibility across schedule boundaries, prohibited admin mutations, seasonal enable/disable/schedule behavior, and no duplicate product/SKU creation. Update OpenAPI/API docs and report test results.
6. Include an `isEvergreen` property in the admin occasion response (derived from the backend's core occasion rule) so frontend controls do not duplicate business rules by hardcoded occasion names.
7. Update Birthday, Anniversary, and Wedding image keys to the newly uploaded distinct assets: `occasions/birthday-gifting-v2.png`, `occasions/anniversary-gifting-v2.png`, and `occasions/wedding-gifting-v2.png`. Preserve all product associations and other admin-authored fields.
8. In public `occasion_grid` results, return enabled and currently in-season seasonal occasions first, then evergreen occasions. Preserve admin `displayOrder` within each group. Enabling a seasonal occasion should move it ahead of the evergreen cards without requiring frontend sorting; disabling it or moving it out of season should move it out of the seasonal group. Cover this ordering in API tests.
9. Allow an admin to clear a seasonal start/end date by explicitly sending `null`; update only fields present in the request so omitted values remain unchanged.

## Frontend requirements (Codex)

- Update the occasion admin UI to identify backend-marked evergreen records as “Always on” and disable the visibility/schedule controls that the backend rejects; keep order/image/product associations editable.
- Ensure seasonal occasions expose the existing enable/schedule controls.
- Render exactly the backend response; do not hardcode four occasion cards in the storefront.
- Add tests for admin control behavior and public grid rendering.

## Acceptance

- Birthday, Anniversary, Wedding, and Baby Shower are present year-round even when every seasonal occasion is off or out of season.
- Seasonal occasions appear only when admin enables them and their schedule is active.
- Active seasonal occasions appear before evergreen cards; both groups preserve admin display order.
- Existing occasion records and product associations are preserved by upgrades/repeated startup.
- Backend and frontend tests pass; verify with the integrated local Docker stack and browser before release.
- Do not push/deploy until the owner approves the local result.

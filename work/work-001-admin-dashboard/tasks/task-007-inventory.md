# Task 1.8 — Inventory integration

**Owner:** Codex
**Status:** Completed
**Work item:** Work 001

## Objective and scope
Replace Inventory placeholder within the supplied admin shell. List persisted product variants with SKU/status/stock, search and product pagination, and relative stock adjustments. No backend redesign, fabricated stock, bulk changes, release or deployment.

## Dependencies and blueprint
Existing GET /admin/products and PATCH /admin/variants/{id}/inventory available in backend/app/api/v1/admin.py. Reuse adminRequest. Add services/inventory.ts, components/StockAdjustment.tsx and pages/InventoryPage.tsx with focused tests; wire AdminApp. Relative deltas avoid absolute overwrites based on stale displayed quantities. Backend remains authoritative for stock validation.

## Substeps
- Completed: API service and paginated list/search.
- Completed: adjustment form, integer validation, busy/error/success handling.
- Completed: regression tests, typecheck, Docker rebuild and local browser verification.

## Acceptance/tests/security
- API-backed variants and pagination; stale requests aborted; loading/error/empty states.
- Submit integer delta only to selected variant; reject zero/noninteger/negative resulting preview; prevent duplicate submissions; failed request preserves input.
- Successful save reloads authoritative stock; no prices/categories changed.
- Tests cover fetch/filter/page, save success/failure and invalid quantity. Existing admin authorization and credential transport retained; no secrets or business fixtures in runtime.
- Local desktop/mobile browser review required; stock test uses reversible local delta then restores original quantity.

## Handoff back
Update tasks.md, notes.md and coordination with exact test/browser results and blockers. Self-review explicitly recorded. No push until user review.

## Verification — 2026-10-10
Docker frontend rebuilt/restarted. TypeScript passed; 23 tests across 7 admin files passed, including 3 Inventory cases. Local authenticated browser verified SKU search, current stock 14, successful +1 to 15 and -1 restoration to 14. Mobile 390px document width remains 390px; adjustment form inspected. Self-review: narrow service uses adminRequest credentials and existing admin authorization; UI prevents duplicate submissions and preserves errors. No application image change. No push/deployment.

## Remaining backend dependency
Existing inventory route uses a read-modify-write sequence; simultaneous adjustments can overwrite one another. Frontend portion complete, final concurrency acceptance pending Gemini 1.8.4 in task-008-inventory-concurrency.md. This is an existing backend issue exposed by the new management flow.

## Final integrated acceptance — 2026-10-10
Gemini1.8.4 returned Completed; prior dependency is resolved. Running API/database healthy and current local frontend built. Verified supplied Inventory screen with persisted sunflower SKU:14→15 through +1, then15→14 through -1, confirming authoritative refresh and restoration. Mobile390×844 adjustment rejects -15 from14 without mutation; document width390. Product image and SKU remain rendered.

Inventory regression suite in frontend Docker:5/5 passed. TypeScript and34 admin regressions passed in preceding Customers integration on the same frontend revision. Gemini backend return records6/6 isolated concurrency/security tests and live API negative-stock rejection. Self-review confirms narrow relative delta payload and retained authorization; no new code required for closure. Firefox remains in broader1.6 acceptance because no Firefox browser surface is available. No push/deployment. Task1.8 Completed; no outstanding Gemini dependency.

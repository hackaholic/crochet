# Work 001 tasks

## In Progress
*(None)*

## Pending
- [ ] 1.7.6 Codex: [Catalogue final local acceptance](tasks/task-018-catalogue-local-acceptance.md) — unblocked by 1.7.12 for real browser upload/save/reopen verification.
- [ ] 1.17 Codex: Audit API support and define scoped integration for private internal notes and real shipment creation; UI controls explicitly disabled until implemented.
- [ ] 1.6.1 Codex: Firefox rendering verification — Pending; Firefox is not available through current enabled browser tools.
- [ ] 1.12 Codex (delivery owner; user provides final acceptance): Prepare the local review and obtain user acceptance. The user reviews the locally verified admin experience and decides whether any additional sections or visual changes are required; only then consider a dev push/deploy.


### 1.14 — Finance and sales analytics (Codex work lead)


## Completed
- [x] 1.18 Gemini + Codex: [Top bar dynamic order search](tasks/task-045-topbar-dynamic-order-search.md) — Completed. Dynamic debounced search across order number, numeric order ID, customer email, customer phone, and customer name with interactive quick-results dropdown, one-click order preview dialog, Enter key navigation to filtered Orders page, and cross-view search synchronization. Backend and frontend tests (TC01–TC08) and local Docker verification passed.
- [x] 1.7.12 Gemini: [Upload persistence](tasks/task-044-upload-persistence.md) — durable LocalStorageProvider, honest 404s on missing keys, 5/5 storage and 2/2 media tests passing.
- [x] 1.6 Codex: [Local admin verification](tasks/task-043-local-admin-verification.md) — desktop/mobile audit done; findings recorded in1.7.12 and1.17; Firefox follow-up1.6.1 remains Pending.
- [x] 1.7.11 Gemini: [Seeded catalogue ID sequences](tasks/task-041-seeded-catalogue-sequences.md) — durable PostgreSQL sequence alignment via align_postgres_sequences in seed_catalogue, 4/4 tests pass in test_seeded_sequences.py.

- [x] 1.16 Codex: [Activity Feed order navigation](tasks/task-039-activity-order-navigation.md) — seven focused cases/typecheck; rebuilt local desktop/mobile verified.
- [x] 1.15 Codex: [Clickable pipeline status filters](tasks/task-038-dashboard-pipeline-navigation.md) — six focused tests/typecheck; rebuilt local desktop/mobile verified.
- [x] 1.9.3 Codex: [Clickable customer names/full profile](tasks/task-036-customer-profile-navigation.md) —8 tests/typecheck, local desktop/mobile verified.
- [x] 1.9.3 Codex: [Clickable customer names/full profile](tasks/task-036-customer-profile-navigation.md) — Customer name opens profile, Actions column removed, saved addresses rendered with default badge, 6/6 tests pass.
- [x] 1.14.7 Codex: [Local analytics reconciliation and acceptance](tasks/task-027-finance-local-acceptance.md) —21 PostgreSQL checks pass; rebuilt API and local desktop/mobile verified.
- [x] 1.14.8 Gemini: [Finance accounting reconciliation](tasks/task-040-finance-accounting-reconciliation.md). (Unpaid prepaid and failed payments excluded from recognized sales, gross sales corrected to subtotal without double discount addition, 19/19 tests pass in test_admin_dashboard.py).
- [x] 1.9.4 Gemini: [Customer saved-address detail API](tasks/task-037-admin-customer-addresses-api.md). (Saved addresses in customer profile detail, deterministic default-first order, distinct account phone, 6/6 tests pass).
- [x] 1.10.2 Codex: [Settings brand profile UI](tasks/task-033-brand-settings-ui.md) — 12 focused tests/typecheck and real local save/clear/restore/mobile verified; server edge follow-up1.10.3 stays pending.
- [x] 1.11.1 Codex: [Orders error/race regression coverage](tasks/task-034-orders-resilience-tests.md) — 3 regressions/typecheck passed, local empty search verified.
- [x] 1.10.3 Gemini: [Brand name edge validation](tasks/task-035-brand-settings-edge-validation.md). (Explicit null names and internal control characters including tab/newline/DEL rejected 422, unchanged brand row verified, 3/3 tests pass).
- [x] 1.10.1 Gemini: [Brand settings validation](tasks/task-032-brand-settings-validation.md). (Strict name/owner length and control char checks, safe http/https URL validation, clear/preserve semantics via exclude_unset, forbid extra fields, 3/3 tests pass).
- [x] 1.10 Codex: [Settings scope/API audit](tasks/task-031-settings-scope-audit.md).
- [x] 1.14.6 Codex: [Finance analytics panels](tasks/task-026-finance-analytics-ui.md). 19 frontend tests/typecheck, 10 backend tests and local desktop/mobile verified; final reconciliation remains 1.14.7.
- [x] 1.14.2 Gemini: [Sales by category](tasks/task-022-sales-category-api.md). (Single-accounting category allocation via primary category/fallback/Uncategorized, shares and order counts, 2/2 tests pass).
- [x] 1.14.3 Gemini: [Sales by country and Indian region](tasks/task-023-sales-country-api.md). (Immutable shipping address snapshot aggregation, Indian state breakdown, UNKNOWN fallback, 2/2 tests pass).
- [x] 1.14.4 Gemini: [Top-selling products and variants](tasks/task-024-top-products-api.md). (Date/eligible status filtered top products by revenue or units with deterministic tie-breaks, 2/2 tests pass).
- [x] 1.14.5 Gemini: [Finance trends and operational indicators](tasks/task-025-finance-trends-api.md). (Equal-length prior period comparison, null baseline growth on 0 prior sales, operational counts for pending payments/cancellations/fulfillment, 2/2 tests pass).
- [x] 1.14.6.2 Codex — [Finance summary contract UI](tasks/task-030-finance-summary-contract-ui.md). 13 targeted tests/typecheck passed; Docker rebuilt and local Finance reporting dates verified.
- [x] 1.14.1 Gemini: [Define finance analytics contract](tasks/task-021-analytics-metric-contract.md). (Shared IST date window, gross product sales vs order receipts vs net revenue without double discount deduction, cancellation & unpaid exclusion, zero-order AOV, null baseline comparison, untracked gateway fees explicit, 8 backend/security/frontend contract checks pass).
- [x] 1.14.6.1 Codex — [Finance period alignment](tasks/task-028-finance-period-alignment.md).40 admin tests/typecheck,8 backend tests, local desktop/mobile verified.

- [x] 1.13 Codex: Repair workflow contract ID/status/link warnings; WorkWeave parser reports zero Work001 warnings.

- [x] 1.8 Codex: [Inventory integration](tasks/task-007-inventory.md) — atomic API integrated; local14→15→14 roundtrip, mobile validation and5 Inventory tests passed.

- [x] 1.9.2 Codex: [Customers UI](tasks/task-011-customers-ui.md) — API-backed list/search/profile/history; 34 admin tests and typecheck pass; local desktop/mobile verified.

- [x] 1.9.1 Gemini: [Read-only Customers API](tasks/task-010-customers-api.md) — Completed. Added `list_admin_customers`, `get_admin_customer`, `get_admin_customer_orders` services in `backend/app/services/admin_customers.py`, schemas `AdminCustomerOut`/`AdminCustomerListOut`, routes `GET /api/v1/admin/customers`, `GET /api/v1/admin/customers/{id}`, `GET /api/v1/admin/customers/{id}/orders`. 5/5 tests passing in isolated test container, documented in `docs/api-admin.md`, verified against live local API container. Unblocks 1.9.2.

- [x] 1.8.4 Gemini: [Atomic inventory adjustments](tasks/task-008-inventory-concurrency.md) — Completed. Added `adjust_variant_inventory_atomic()` service with multi-tier concurrency protection (in-process mutex + row-level with_for_update + PostgreSQL advisory xact lock + non-negative rollback), 6 integration/concurrency tests passing in isolated test container, and live Docker verification on variant 1382 (+1/-1 and -50 negative rejection).

- [x] 1.7.10 Codex: [Product enable/disable](tasks/task-013-product-visibility.md). — local disable/restore and28 tests verified.

- [x] 1.8.5 Codex: [Inventory product thumbnails](tasks/task-012-inventory-product-images.md). — Docker/typecheck/5 tests and local image render verified.

- [x] 1.9 Codex: [Customers scope/API audit](tasks/task-009-customers-audit.md). — scope audit and dependent contracts complete.

- [x] 1.7.9 Gemini: [Fix case-insensitive concurrent tag creation](tasks/task-019-tag-concurrency.md) — Completed. Added `uq_tags_name_lower` functional unique index & Alembic migration `b2c3d4e5f6a7`, multi-layered concurrency serialization (in-process lock + postgres advisory xact lock + savepoint IntegrityError catch), 8-thread concurrency integration test, and verified against live local Docker API container.

- [x] 1.7.1 Codex: [Catalogue list and filters](tasks/task-014-catalogue-list-filters.md) — database list and editor verified locally; list/filter/page regression tests pass.
- [x] 1.7.7 Codex: Backend-resolved admin media URLs preserve storage keys; both local sunflower photos render; 2 backend tests pass.
- [x] 1.7.8 Codex: Compact mobile admin sidebar and constrained content width; local 390px viewport has no page overflow.
- [x] 1.7.4 Codex: [Photo upload/gallery management](tasks/task-017-catalogue-media.md) — implementation and scoped tests complete; remaining end-to-end acceptance in 1.7.6.
- [x] 1.7.3 Codex: [Variant pricing and stock editing](tasks/task-016-variant-pricing.md) — implementation and scoped tests complete; remaining end-to-end acceptance in 1.7.6.
- [x] 1.7.2 Codex: [Product create/edit and categories](tasks/task-015-product-editor-categories.md) — implementation and scoped tests complete; remaining end-to-end acceptance in 1.7.6.
- [x] 1.1 Inspect the provided `/home/anu/Downloads/admin.zip` export and current implementation. The source includes a `mockData.ts`; it is not present in the app runtime. The supplied shell, dashboard, orders, order detail, finance, returns, and placeholder page structure exists under `src/admin/`.
- [x] 1.2 Integrate the supplied admin layout/navigation into the existing `/admin` route without replacing it with a new design.
- [x] 1.3 Wire the implemented dashboard, orders/order detail, finance, and returns screens to typed API service calls; retain loading/empty states and remove prototype records from runtime rendering.
- [x] 1.4 Keep the admin route behind an administrator access check with sign-in, loading, and API error states.
- [x] 1.5 Gemini: [Core admin backend return](tasks/task-020-core-backend-return.md) — returned original API scope; historical evidence retained.
- [x] 1.7.5 Gemini: [Tag-management API](tasks/task-006-tags-api.md) — Completed. GET /admin/tags, POST /admin/tags, and product tagIds validation implemented, tested (6/6 tests passing), documented in `docs/api-admin.md`, verified against live local API. Returned to Codex for 1.7.6.

## Pending test coverage

- [x] 1.11 Codex: [Admin screen regressions](tasks/task-042-screen-regression-acceptance.md) —91 admin tests/typecheck pass; safe async failures and working tracking Save.
- The previous host Node blocker is resolved for current work by running checks in the supported Node Docker image.
- Superseded backend test blocker:10 dashboard/finance tests passed in isolated Docker on2026-10-11.

## Blocked
- [ ] 1.7.6 Codex: [Catalogue/tag local acceptance](tasks/task-018-catalogue-local-acceptance.md) — frontend checks passed; sequence fix returned; final acceptance waits for Gemini1.7.12 actual upload persistence.

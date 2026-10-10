# Work 001 tasks

## In Progress






## Pending

- [ ] 1.7.6 Codex: [Tag integration and local acceptance](tasks/task-018-catalogue-local-acceptance.md) — live tag discovery verified; tag tests and final local acceptance pending; temporarily queued while 1.8 is implemented.

- [ ] 1.6 Codex: Verify the integrated admin in local Docker/browser, including API-backed data, error/empty/mutation states, and desktop/mobile rendering; record defects before marking the integration accepted.

- [ ] 1.10 Codex: Define which Settings belong in V1 and audit existing admin APIs; write a separate Gemini contract before adding backend capability.
- [ ] 1.12 Codex (delivery owner; user provides final acceptance): Prepare the local review and obtain user acceptance. The user reviews the locally verified admin experience and decides whether any additional sections or visual changes are required; only then consider a dev push/deploy.

## Completed

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

## Blocked



- [ ] 1.11 Codex: Add screen-level UI tests for the dashboard, order list/detail, finance, returns, and any newly implemented pages; run the suite in the supported Node/Docker environment. Catalogue/admin tests run successfully in Docker; broader dashboard/finance/returns coverage remains pending.
- The previous host Node blocker is resolved for current work by running checks in the supported Node Docker image.
- A direct run of `backend/tests/test_admin_dashboard.py` produced no result before it was interrupted; backend tests need rerunning in the project Docker/test environment before acceptance.

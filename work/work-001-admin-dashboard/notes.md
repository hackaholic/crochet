# Work 001 notes

- Current implementation inventory and remaining work are tracked in `tasks.md`; the main delivered UI scope is Dashboard, Orders, Order Detail, Finance, and Returns. Products, Inventory and Customers now have API-backed implementations; Settings remains a placeholder.
- Existing backend product/variant CRUD and inventory adjustment endpoints are documented; the dashboard backend handoff also includes global customer search, but no full customer-management or settings API contract has been confirmed for the admin UI.
- Gemini's backend-completion handoff reports 126 tests passing. This session did not independently complete local integration verification.
- Verification attempts: host Vitest could not start because the active Node runtime lacks `node:util.styleText`; backend dashboard tests yielded no output and were interrupted. Re-run both under the supported Node/Docker test environment.
- Task 1.7.5 backend tag management completed by Gemini:
  - Added `GET /api/v1/admin/tags` and `POST /api/v1/admin/tags` with case-insensitive deduplication and concurrency protection via savepoint rollback.
  - Added strict `tagIds` validation to `POST /api/v1/admin/products` and `PATCH`/`PUT /api/v1/admin/products/{id}` rejecting non-existent tag IDs with 400 Bad Request while keeping existing associations intact.
  - Created service `backend/app/services/admin_tags.py`, schemas `AdminTagCreate` and `AdminTagOut` in `backend/app/schemas/admin.py`.
  - Added test suite `backend/tests/test_admin_tags.py` (6 tests passing). Regression suites `test_admin.py` (7 tests) and `test_occasions_admin.py` (15 tests) pass cleanly.
  - Rebuilt and restarted `docker-api-1` in Docker; verified live behavior on `http://localhost:8000` via curl with admin cookies.
  - Updated `docs/api-admin.md` with contracts and rules. Returned to Codex for Task 1.7.6 (tag integration and local acceptance).
- Next action: Codex to pick up Task 1.7.6 / catalogue tag integration on the frontend. Do not push/deploy before local verification is complete.

## 2026-10-09 — Catalogue integration
Codex owns Work001. Added catalogue list/search/category/status filters/pagination, create/edit fields, primary category, photo upload/gallery and variant pricing/stock editing inside supplied admin shell. Existing tags are preserved while tag endpoint is unavailable. Gemini 1.7.5 ready: authenticated tag list/create and association validation.

Added backend computed primaryImageUrl/galleryImageUrls after browser inspection found keys rendered as relative URLs. UI persists upload keys and consumes backend URLs. No storage paths or business content constructed in frontend. Added mobile compact sidebar/min-width fix and removed irrelevant order-search field on Products.

Verification: Docker frontend build and API build succeeded; TypeScript passes; 18 affected frontend/admin tests pass; 2 database-free backend media regression tests pass. Local browser displayed 24 products, loaded Sunflower Bouquet editor with real categories, SKU, price and stock; no-change Save product succeeded; primary/gallery images both loaded. At 390px viewport, sidebar width 64px and content width 326px; document width matches viewport. Firefox and end-to-end create/upload/tag acceptance remain pending under 1.7.6. No push/deployment performed.

Self-review: write keys preserved, primary category preserved/explicitly selectable, session credentials retained, multipart header corrected, stale list requests aborted, failures retain form fields. Existing admin authorization unchanged; auth transport failure tested. Tag API unavailable is explicit rather than simulated. Next: Gemini returns 1.7.5, then Codex completes 1.7.6 and owner local review.

## 2026-10-09 — Returned tag API integration
Codex verified local database tags in Products editor, reused the existing sunflowers tag and saved successfully. Existing associations unchanged. Typecheck/18 existing tests pass; ProductEditor now 6/6 with duplicate-return and creation-failure coverage. Gemini 1.7.9 follow-up: case-sensitive Tag.name unique index does not guarantee case-insensitive concurrent deduplication. Pending final create/upload roundtrip and Firefox acceptance. No push/deployment.

## 2026-10-09 — Task 1.7.9 case-insensitive concurrent tag creation fix completed (Gemini)
- Database schema: Added `Index("uq_tags_name_lower", func.lower(name), unique=True)` to `Tag` model (`backend/app/models/catalogue.py`).
- Migration: Created Alembic migration `backend/alembic/versions/b2c3d4e5f6a7_case_insensitive_tag_uniqueness.py`. Deduplicated existing case-variant rows by merging `product_tags` references to canonical tag IDs and removing duplicate tag records before establishing the functional unique index `uq_tags_name_lower`. Applied migration cleanly in PostgreSQL container.
- Concurrency serialization: In `backend/app/services/admin_tags.py`, implemented:
  1. In-process lock `_tag_creation_lock` across concurrent worker threads.
  2. Transactional advisory lock `SELECT pg_advisory_xact_lock(hashtext('admin_tag_creation'))` across multi-process uvicorn workers.
  3. Database-level `uq_tags_name_lower` uniqueness constraint.
  4. Nested transaction savepoint `db.begin_nested()` to safely catch `IntegrityError` and query/return the existing canonical tag.
- Testing & Verification:
  - Added `test_concurrent_tag_creation_case_insensitive` in `backend/tests/test_admin_tags.py` using `ThreadPoolExecutor` with 8 concurrent threads requesting case/whitespace variants.
  - All 7 tests passed in `test_admin_tags.py` (25.62s).
  - Regression test suites `test_admin.py` (7/7) and `test_occasions_admin.py` (15/15) passed.
  - Rebuilt and restarted `docker-api-1`. Verified live behavior against `http://localhost:8000/api/v1/admin/tags` using admin session cookies: verified single persisted tag across case/whitespace mutations (`LiveTestConcurTag` vs ` livetestconcurtag ` vs `LIVETESTCONCURTAG`).
- Returned to Codex for Task 1.7.6.

2026-10-10 Task1.8: API-backed Inventory screen, relative stock adjustment form and focused tests implemented. Frontend Docker rebuilt/restarted; typecheck and23 tests passed. Local stock14→15→14 verified; mobile390px no document overflow. Self-review found existing backend lost-update risk; Gemini1.8.4 contract ready. No push.

2026-10-10 Task1.9 Completed: audited supplied ZIP placeholder, global search limits/role scope and persisted user/order fields. Defined read-only Customers V1; Gemini 1.9.1 API contract ready, Codex 1.9.2 UI waits on it. Documentation-only; no runtime changes, no Docker rebuild or push.

2026-10-10 Task1.8.5 Completed: reusable ProductThumbnail in Inventory, backend URLs, fixed64px contain-fit and neutral missing/failed fallback. Typecheck/5 Inventory tests passed; local sunflower loaded64×64, mobile no overflow. Frontend rebuilt/restarted. No backend requirement or push.

2026-10-10 Customers1.9.2 pickup: backend1.9.1 still Pending, dedicated GET routes absent. Added seven UI acceptance/regression/failure/security cases and marked exact dependency Blocked. Gemini can start existing1.9.1 contract. Documentation-only; no runtime changes/rebuild/push.

2026-10-10 Task1.7.10 Completed: Products Enable/Disable uses existing ACTIVE/DRAFT status, only status PATCHed, archived untouched. Local storefront visibility0→1 verified and original status restored. Frontend rebuilt; typecheck/28 admin tests passed. No Gemini dependency or push.

2026-10-10 Task 1.8.4 Completed (Gemini): Atomic inventory adjustments with multi-tier concurrency protection.
- Created `backend/app/services/admin_inventory.py` with `adjust_variant_inventory_atomic()` combining:
  1. In-process mutex `_inventory_adjust_lock`.
  2. Database row-level locking via `with_for_update()` on PostgreSQL / supported engines.
  3. Transaction-level advisory lock `SELECT pg_advisory_xact_lock(hashtext('admin_variant_inventory'), :var_id)` in PostgreSQL.
  4. Validation preventing negative resulting stock (400) before commit; transactional rollback on error.
- Refactored `adjust_variant_inventory` in `backend/app/api/v1/admin.py` to delegate to the atomic service.
- Created test suite `backend/tests/test_admin_inventory.py` covering RBAC (401/403/200), input validation (404/400/negative bounds), absolute/relative compatibility, concurrent additions (10 threads), concurrent mixed additions/subtractions (8 threads), and competing withdrawals (5 threads preventing negative stock). All 6 tests pass in `backend/scripts/run_isolated_tests.sh` against isolated test database container (8.43s). Regression tests pass.
- Docker API service rebuilt and restarted; live API on variant 1382 verified via admin session cookies (+1 to 17, -1 restoration to 16, and negative overage withdrawal returning 400 with stock unchanged).
- Returned to Codex for integrated Task 1.8 local acceptance.

## 2026-10-10 — Task 1.9.1 Completed (Gemini): Read-only customer administration API
- Endpoints implemented in `backend/app/api/v1/admin.py` and service `backend/app/services/admin_customers.py`:
  1. `GET /api/v1/admin/customers`: Bounded pagination (`page >= 1`, `pageSize` 1–100 default 20), query `q` trimmed/validated (max 200 chars, parameterized ILIKE against name, email, phone). Strictly filtered by `User.role == UserRole.CUSTOMER` (excludes admins). Deterministic sort: `created_at desc nullslast, id desc`. Returns `{items, total, page, pageSize}` where `orderCount` reflects persisted orders linked by `user_id`.
  2. `GET /api/v1/admin/customers/{id}`: Returns profile fields with `orderCount`. Non-customer or nonexistent ID returns 404.
  3. `GET /api/v1/admin/customers/{id}/orders`: Returns `AdminOrderListOut` paginated history strictly filtered by `Order.user_id == customer.id`. Guest orders are never linked.
- Schemas: Added `AdminCustomerOut` and `AdminCustomerListOut` to `backend/app/schemas/admin.py`. No credentials, session tokens, passwords, or auth identities exposed.
- Tests & Verification:
  - Created `backend/tests/test_admin_customers.py` covering TC01–TC05 (RBAC 401/403, list pagination & admin exclusion, boundary validation 422/404, parameterized injection safety & guest order isolation, nullable contacts and all order statuses).
  - All 5 tests passed in isolated test container: `bash backend/scripts/run_isolated_tests.sh backend/tests/test_admin_customers.py` (5 passed in 5.83s).
  - Rebuilt and restarted `docker-api-1`. Verified live behavior against `http://localhost:8000/api/v1/admin/customers`: 401 unauthenticated, 404 admin/unknown ID, 422 oversized query string, 200 list returning 4 customers, 200 customer 2 profile and order history matching exact database counts.
- Documentation: Updated `docs/api-admin.md` with endpoints, TypeScript schemas, and customer administration security rules.
- Returned to Codex for Task 1.9.2 (Customers UI).


2026-10-10 Codex1.9.2 Completed: Customers search/list/profile/order history integrated with returned API and existing order detail navigation. Docker rebuilt; typecheck and34 admin tests passed (single worker after an existing parallel Inventory timeout). Real local desktop/mobile acceptance passed, including empty/nullable states and no390px page overflow. No records mutated, PII logged, push or deployment. Firefox not available in enabled browser surfaces.

2026-10-10 Inventory1.8 final acceptance Completed: healthy local services; sunflower14→15→14 via UI, mobile invalid withdrawal rejected with stock unchanged;390px document has no overflow.5/5 Inventory tests passed in frontend Docker. Gemini atomic backend return accepted; no further backend dependency. No code change, push or deployment.

2026-10-10 Task1.13 Completed: created individual matching contracts014–020 for catalogue subtasks, tag concurrency and original backend return. Corrected checklist links; original parent contracts and archive preserved. WorkWeave parse_work_directory reports0 Work001 work/subtask warnings; Work001 documentation whitespace check passes. Documentation only; no runtime tests/rebuild/deployment required.

- 2026-10-10: User requested Finance category/country/product analytics and creative useful indicators. Defined1.14.1–1.14.7 with owners, dependency gates, frontend/backend tests and security. Repository audit: Finance shows summary/series only; existing topSellingProducts query sums all order items without payment/date filter. Finance UI maps non7d chart period to30d, requiring shared range correction. Planning only; no code/deploy/push.

## Return 2026-10-11
Completed1.14.6.1: shared IST calendar date utility, yesterday single-day range, all six presets preserved, summary/chart resolve one identical range per refresh, safe retry. Existing dashboard date users now share the same corrected utility. No accounting formula or eligibility changes.
40 admin tests passed (includes8 date/transport and2 finance UI tests); typecheck passed.8 existing backend dashboard/finance tests passed in isolated SQLite test container; warnings only. Frontend Docker rebuilt/restarted. Actual admin Finance Yesterday rendered only2026-10-10; Previous Month chart rendered September dates rather than last30days. Mobile390 content width390: no overflow. Screenshot /tmp/sulocraft-finance-period.png. Self-review: credentialed admin requests unchanged; safe errors; stale results ignored; read-only API preserved.

2026-10-11: Task 1.14.1 Completed (Gemini): Defined comprehensive finance analytics metric and breakdown contract in `work/work-001-admin-dashboard/tasks/task-021-analytics-metric-contract.md`. Established shared Asia/Kolkata (IST) calendar range policy, unified revenue accounting without double-discount deduction, order status/payment eligibility (COD vs prepaid vs unpaid/cancelled), zero-order AOV and null baseline comparisons, explicit unavailable indicators for untracked gateway fees, and specifications for downstream subtasks (1.14.2 Categories, 1.14.3 Destinations, 1.14.4 Top Products, 1.14.5 Trends). 8 backend/security/frontend contract checks pass. Unblocks Gemini pickup of 1.14.2–1.14.5. No push or deployment.

2026-10-11: Tasks 1.14.2, 1.14.3, 1.14.4, and 1.14.5 Completed (Gemini):
- Implemented 4 finance analytics endpoints in `backend/app/api/v1/admin.py`:
  1. `GET /api/v1/admin/finance/categories` (1.14.2): Single accounting attribution policy using product primary category -> lowest assigned category -> Uncategorized bucket; prevents multi-category duplicate revenue counting.
  2. `GET /api/v1/admin/finance/destinations` (1.14.3): Aggregation based strictly on immutable `Order.shipping_address_json` with Indian state breakdown and UNKNOWN destination fallback.
  3. `GET /api/v1/admin/finance/top-products` (1.14.4): Period and eligible order filtered top selling products by revenue or units with deterministic tie-breaks and variant snapshots.
  4. `GET /api/v1/admin/finance/trends` (1.14.5): Equal-length prior period comparison with null baseline growth handling, plus operational indicators (pending payments, cancellations, fulfillment counts).
- Schemas added to `backend/app/schemas/admin.py` and documented in `docs/api-admin.md`.
- Test suite: Added comprehensive integration tests in `backend/tests/test_admin_dashboard.py` (`test_admin_finance_categories_destinations_products_and_trends`). 2/2 tests pass cleanly (23.99s).
- Coordination updated: Tasks 1.14.2–1.14.5 marked Completed; returned to Codex for Task 1.14.6 UI panel integration. No push or VPS deployment performed.

### 1.14.6.2 return
Completed finance summary reporting-period presentation; 13 targeted frontend tests and typecheck passed, Docker frontend rebuilt/restarted and local Finance browser verified. No backend changes or push. Gemini 1.14.2 is active; remaining analytics panels wait for returned APIs.

2026-10-11 Codex 1.14.6 returned: four API-backed finance analytics panels integrated, independent retry/loading, shared ranges, ranking, bounded more results, paise formatting and null-baseline handling. 19 targeted frontend tests/typecheck and 10 isolated SQLite backend tests passed. Invalid supplied backend dates now reject422 after regression found silent fallback. Docker API/frontend rebuilt; local real API category/country totals reconcile ₹8,697 and two product photos load;390px populated/empty page has no overflow. Final fixture-based PostgreSQL acceptance and query performance remain1.14.7. No push/deploy. Exact evidence in task026.

2026-10-11 Task 1.10.1 Completed (Gemini):
- Brand settings validation and persistence hardened in `backend/app/schemas/storefront.py` and `backend/app/api/v1/admin.py`:
  1. `BrandSettingsUpdate`: Configured `extra="forbid"` to reject unknown payload fields; added strict length limits (100 chars), whitespace trimming, and control character rejection for `name` and `owner_name`.
  2. Safe URL validation on `instagram_url` and `whatsapp_url`: Enforces http/https schemes, validates host presence, rejects embedded user credentials, and limits length to 255 chars. Whitespace-only strings or explicit null clear values; omitted fields preserve existing values via `model_dump(exclude_unset=True)`.
  3. `GET /api/v1/admin/storefront/brand`: Read-only without mutation side effects or demo contact injection on missing records.
- Testing: Hardened `test_admin_get_and_update_brand_settings` in `backend/tests/test_storefront.py` covering TC01–TC05 (unauthenticated 401, customer 403, 422 validations for empty names, control chars, unsafe schemes, embedded credentials, extra fields, and clearing vs preserving fields). All 3 brand tests passing in `tests/test_storefront.py -k "brand"` (25.25s).
- Returned to Codex for Task 1.10.2 (Settings brand profile UI). No push or VPS deployment performed.

Settings1.10 scope audit completed;1.10.1 Gemini pickup-ready.1.10.2 frontend implemented,11 tests/typecheck passed, Docker/localdesktop/mobile/no-change save verified. Final server-validation acceptance pending backendreturn; independent1.11.1 picked. Existing Orders request has no rejection handler, causing permanent spinner; contract034 covers correction and regressions.

2026-10-11 Task 1.10.3 Completed (Gemini):
- Addressed follow-up regression in `backend/app/schemas/storefront.py` `_validate_name_field`:
  1. Explicitly rejects `None` with `ValueError("{field_label} cannot be null")` returning 422 Unprocessable Entity, preventing database `NOT NULL` constraint violations.
  2. Broadened control character check to reject all characters with `ord(c) < 32` or `ord(c) == 127` (DEL), without exempting tabs, newlines, or carriage returns.
- Added regression tests in `backend/tests/test_storefront.py`:
  - Verified `PUT {"name": None}` and `PUT {"ownerName": None}` return 422 without writing to the database or changing existing brand attributes.
  - Verified control character variants (`\x00`, `\t`, `\n`, `\r`, `\x7f`) return 422.
- Verified test suite: all 3 brand tests passing in `tests/test_storefront.py -k "brand"` (25.29s).
- Returned to Codex. No push or deployment performed.

2026-10-11 Codex Settings1.10.2 Completed: API/form integrated, canonical trim/save, optional link clear persisted and original restored,12 focused tests/typecheck, DockerAPI/frontend and390px local browser verified. Gemini1.10.1 return accepted for implemented semantics; code review identified explicit null name/internal-control gap assigned1.10.3. Orders1.11.1 Completed: failure/retry/stale-response correction and3 regressions/typecheck, local no-match search verified. No push/deploy.

2026-10-11 User requested customer-name links/full profile, clickable pipeline filters and activity-order links. Defined1.9.3/1.9.4,1.15,1.16 with owners/dependencies/test contracts. Customer addresses missing from current profile API: Gemini1.9.4 ready. Pipeline statuses/date filters and activity source order IDs already exist, so no new backend endpoints needed for those. Documentation only.

2026-10-11 Task 1.9.4 Completed (Gemini):
- Extended customer profile detail in `backend/app/schemas/admin.py`, `backend/app/services/admin_customers.py`, and `backend/app/api/v1/admin.py`:
  1. Added `AdminCustomerAddressOut` and `AdminCustomerDetailOut` schemas. Listings retain lightweight `AdminCustomerOut`, while detail endpoint `GET /api/v1/admin/customers/{id}` returns `AdminCustomerDetailOut` with `addresses: list[AdminCustomerAddressOut]`.
  2. Addresses are sorted deterministically: `Address.is_default.desc(), Address.id.asc()`.
  3. Strict isolation by `Address.user_id == customer.id`; account phone is preserved separately from address phone.
- Updated `docs/api-admin.md` with typed contracts.
- Testing: Added `test_admin_customer_saved_addresses_detail` in `backend/tests/test_admin_customers.py` covering TC01–TC04 (multiple/default address order, zero-address empty list `[]`, cross-customer address isolation, and 401/403 security). All 6 integration tests passing (35.96s).
- Returned to Codex for Task 1.9.3 (Customer profile UI navigation). No push or deployment.

2026-10-11 Finance1.14.7: isolated PostgreSQL seven new accounting cases:1 passed/6 failed. Unpaid recognition and discounted-gross inflation proven. Tests retained, no server implementation changed;1.14.8 Gemini handoff ready. Remaining acceptance not claimed.

2026-10-11 Task 1.14.8 Completed (Gemini):
- Corrected shared finance accounting and recognized order eligibility across finance summary, sales series, categories, destinations, top-products, and trends:
  1. `_get_eligible_finance_orders()` now filters orders by commerce commitment: excludes `CANCELLED` orders; includes active `COD` orders (regardless of payment status); requires prepaid orders (`UPI`, `CARD`, `NETBANKING`, etc.) to have `payment_status` in (`PAID`, `PARTIALLY_REFUNDED`, `REFUNDED`). Unpaid prepaid orders (`PENDING`, `FAILED`) are excluded from recognized sales and counted under operational indicators.
  2. Fixed gross sales formula across `summary`, `sales`, `destinations`, and `trends`: checkout in `orders.py` stores `subtotal` before discount; gross sales is computed as `sum(o.subtotal for o in orders)` without double-counting discounts (`o.subtotal + o.discount_amount` eliminated).
  3. Reconciled net revenue calculation: `net_revenue = gross_sales - discounts + shipping_collected + stored_tax - refunds`.
  4. Preserved operational indicators: `pendingPaymentCount` and `pendingPaymentTotal` track unpaid prepaid orders without inflating recognized revenue.
- Verification:
  - Verified 7 acceptance checks in `test_admin_dashboard.py` (TC-FIN-27-01 and TC-FIN-27-02 parameterizations).
  - Added reconciliation regression tests TC-FIN-27-03 and TC-FIN-27-04.
  - Ran `backend/scripts/run_isolated_tests.sh backend/tests/test_admin_dashboard.py -v`: 19/19 tests pass against disposable PostgreSQL container.
  - Verified local API health on port 8000: `GET /health` returns `200 OK`.
- Returned to Codex for Task 1.14.7 local Docker/browser verification. No push or deployment.

2026-10-11 Finance1.14.7 Completed:21 PostgreSQL checks pass; IST boundaries and20-order2-query smoke added. Rebuilt API and localhostFinance desktop/mobile real totals6098gross/2599refund/3499net verified; image, unit ranking, keyboardregions, Septemberempty period checked. Firefox unavailable; no capacity/load claim. No push.

2026-10-11 Task 1.9.3 Completed (Codex):
- Implemented clickable customer names and full customer profile with saved addresses:
  1. Updated `src/admin/pages/CustomersPage.tsx`: customer names render as accessible keyboard-focusable buttons opening the customer profile; removed the redundant "Actions" column and generic "View" buttons.
  2. Updated `src/admin/services/customers.ts`: typed `CustomerAddress` and `CustomerDetail` with `addresses: CustomerAddress[]`.
  3. Updated `src/admin/components/CustomerProfile.tsx`: added "Saved addresses" section rendering recipient name, address phone, address line1/line2, landmark, city, state, postalCode, country, and `Default` badge for primary address. Distinguishes account phone from address contact phone. Displays "No saved addresses" when empty.
  4. Updated `src/admin/pages/CustomersPage.test.tsx`: added TC01–TC04 coverage (name button selection, absence of Actions column, multiple saved addresses with default label and distinct phone numbers, empty addresses state, and resilient error/retry).
- Verification:
  - 6/6 tests passing in `CustomersPage.test.tsx`.
  - 64/64 tests passing across all 14 admin test suites (`npx vitest run src/admin`).
  - Production build (`npm run build`) and TypeScript typecheck (`tsc --noEmit`) passing with 0 errors.
  - Restarted `docker-frontend-1` and verified live response at `http://localhost:8080/admin` (HTTP 200 OK). No push or deploy.

2026-10-11:1.9.3 Completed,8 UI tests/typecheck and actual local customer name/Enter/profile/address/phone/default/order-history/mobile checks passed. Reused Gemini1.9.4 ownership tests; no backend changes/push. Next ready Codex task1.15.

2026-10-11 — Task1.15 completed: pipeline status/date navigation with server pagination and sidebar reset; six focused cases and typecheck passed, Docker frontend rebuilt and actual desktop/390px local behavior verified. Return evidence in task-038. Next1.16; nothing pushed.

2026-10-11 — 1.16 completed: activity-to-order navigation, real numeric IDs, safe missing/denied detail feedback. Seven focused tests/typecheck passed; rebuilt frontend and actual desktop/mobile verified. See task-039. Nothing pushed.

2026-10-11 — 1.7.6 acceptance:16 focused tests/typecheck pass, actual upload/tag/create/reopen/mobile verified after local ID-sequence repair. Found durable seed sequence bug; pickup-ready Gemini1.7.11 in task-041. QA listing archived. No push.

2026-10-11 — 1.7.11 completed: Gemini implemented durable PostgreSQL sequence synchronization via align_postgres_sequences in backend/app/db/seed.py, executed automatically at the end of seed_catalogue. Dynamically queries all serial/identity columns and sets each sequence to GREATEST(MAX(col), last_value) with is_called=true to prevent rewinding or primary key collisions. Safe no-op on SQLite/non-PostgreSQL. Added 4 regression tests in backend/tests/test_seeded_sequences.py (4/4 pass against PostgreSQL sulocraft_test; 3 pass/1 skip on SQLite). Rebuilt/restarted docker-api-1 and verified all live sequences aligned. Task 1.7.6 unblocked for Codex local acceptance. No push.

2026-10-11 —1.11/1.6 Completed: added dashboard/returns/order-detail failure/retry/confirmation coverage and fixed caught async failures, stale dashboard responses, tracking persistence/response rendering.91admin suite checks passed; additional transport/access6and detail4checks/typecheck passed. Rebuilt API/frontend, desktop9pages and390px9pages verified; storefront still renders. Actual upload fallback defect handed to Gemini1.7.12;1.7.6Blocked. Inert shipment/private note controls now explicitly disabled; follow-up1.17. Firefox1.6.1Pending; owner1.12Pending. No push/deployment.

2026-10-11 — 1.7.12 Completed (Gemini):
- Implemented durable `LocalStorageProvider` in `backend/app/services/storage/local.py` ensuring uploaded files are persisted to `public/images/` and survive service recreation without relying on ephemeral in-memory dicts. Included path traversal containment checks.
- Updated storage factory `backend/app/services/storage/factory.py` so uncredentialed environments default to durable `LocalStorageProvider` instead of `MockStorageProvider`.
- Eliminated silent Unsplash fallback: updated `resolve_mock_image_source()` in `backend/app/core/images.py` to return `None` for unmapped keys; updated `/static/images/{image_path:path}` in `backend/app/main.py` to raise HTTP 404 (`Image not found`) when images are not on disk and not in `MOCK_IMAGE_MAP`.
- Automated test suite: `backend/tests/test_storage.py` verified (5/5 tests passing for 1.7.12-TC01 to TC04 and Cache-Control headers). `backend/tests/test_admin_product_media.py` (2/2) and regression suites `test_admin.py` (7/7) and `test_occasions_admin.py` (15/15) all pass cleanly.
- Live Docker verification: Rebuilt and restarted `docker-api-1`. Verified live `/health` (200), nonexistent image keys returning 404, seeded images returning 200, and authenticated admin upload returning live URL with exact matching binary bytes.
- Task 1.7.6 unblocked and returned to Codex for real browser upload/save/reopen verification. No push/deployment.

2026-10-20 — Task 1.18 Completed (Gemini + Codex):
- User requirement: Dynamic search in admin dashboard top bar when an order number, numeric order ID, email, or phone is typed or pasted.
- Backend implementation:
  - Extended `list_admin_orders` in `backend/app/api/v1/admin.py` to support numeric `Order.id == int(q.strip())` when digits are supplied, matching internal primary keys directly, alongside case-insensitive `Order.order_number`, `Order.customer_email`, `Order.customer_phone`, and `Order.customer_name`.
  - Added backend integration test `test_1_18_admin_orders_dynamic_search` in `backend/tests/test_admin_dashboard.py` verifying exact/partial order numbers, numeric ID, email, phone, customer name, whitespace trimming, and unauthorized RBAC rejection (401/403). Test passed 100%.
- Frontend implementation:
  - `src/admin/layout/AdminTopBar.tsx`: Debounced dynamic order search calling `api.getOrders({ search, pageSize: 6 })` on 250ms delay, request sequence counter preventing out-of-order stale responses, outside-click and Escape key listeners, clear button, and quick-results dropdown rendering status badge, order number, customer name, contact info, date, and formatted INR total. Added one-click preview via `onSelectOrder` and Enter key / "View all" navigation via `onNavigateToOrders`.
  - `src/admin/layout/AdminLayout.tsx`: Passed `onSelectOrder`, `onNavigateToOrders`, and `initialSearch` to `AdminTopBar`.
  - `src/admin/AdminApp.tsx`: Wired `navigateToOrdersWithSearch` and `setSelectedOrder` to `AdminLayout`, showing `OrderPreview` dialog directly on result click and switching tabs to Orders on Enter.
  - `src/admin/pages/OrdersPage.tsx`: Added `useEffect` to synchronize search query state when navigating from the top bar search input.
- Testing & Verification:
  - Added unit/integration test suite `src/admin/layout/AdminTopBar.test.tsx` (7/7 passing: debounced search, phone/email search, click selection, Enter navigation, empty results state, request race condition prevention, 10-digit phone query).
  - Updated `src/admin/AdminApp.test.tsx` (all passing).
  - Full admin Vitest suite (`npx vitest run src/admin`): 139/139 tests passing across 35 test files.
  - TypeScript typecheck (`npx tsc --noEmit`): 0 errors.
  - Live Docker verification: Rebuilt and restarted `docker-api-1` and `docker-frontend-1`. Health check `http://localhost:8000/health` (HTTP 200 OK) and admin dashboard `http://localhost:8080/admin` (HTTP 200 OK) verified.
- 2026-10-20 Post-Delivery Fix (10-Digit Phone Search & Integer Range Boundary):
  - Issue: Searching a 10-digit phone number like `9999900991` succeeded when typing up to 9 digits (`999990099`), but failed with "No matching orders found" upon typing the 10th digit.
  - Root Cause: In PostgreSQL, `Order.id` is a 32-bit signed `INTEGER` (`max = 2,147,483,647`). When the query string had 9 digits, `999990099 <= 2,147,483,647`, so `Order.id == 999990099` was valid in SQL and `Order.customer_phone.ilike` matched. When the 10th digit was entered (`9999900991`), `9999900991 > 2,147,483,647`, causing PostgreSQL to raise `psycopg.errors.NumericValueOutOfRange: integer out of range`. This 500 error caused the UI to show an empty result state.
  - Fix:
    1. In `list_admin_orders`, `admin_global_search`, and `get_admin_order` / `update_order_status`, bounded `Order.id == int(q)` check strictly to the 32-bit signed range `1 <= int(q) <= 2_147_483_647`.
    2. Added phone digit normalization using `func.replace(func.replace(func.replace(Order.customer_phone, ' ', ''), '-', ''), '+', '')` to match formatted phones (`+91`, spaces, dashes) against raw and formatted inputs.
    3. Added test coverage in `test_admin_dashboard.py` (`test_1_18_admin_orders_dynamic_search` covering 9-digit, 10-digit, formatted phone with `+91`, dashed phone, and 15-digit overflow safety) and `AdminTopBar.test.tsx` (1.18-TC07).
    4. Verified live against `docker-api-1` on order `QA-W018-GUEST` (`phone='9999900991'`): returned HTTP 200 with 1 match for both `999990099` and `9999900991`, as well as `+919999900991` and `99999-00991`.
- Status: Completed. No push or deployment performed.
2026-10-29 product-entry audit: ProductEditor already captures title/description, taxonomy tags/categories, photos, customization, and Work019's six public detail fields. Variant backend already persists per-SKU cost and weight, but current variant UI does not expose them. Occasion association exists in ProductOccasion/admin occasion APIs, but product create/update does not accept occasion IDs. New 1.7.13/1.7.14 contracts reuse these fields and add a generic private production profile for every catalogue category. Public product name and existing customer-facing summary remain unchanged; no internal profile/cost is public.
2026-10-29 owner scope review: Full production recipe/profile and cost breakdown are deferred as overkill for V1. Keep existing catalogue and product detail fields; do not start Gemini 1.7.13 or Codex 1.7.14 until the owner chooses a smaller scope. Preserve contracts for later rather than deleting them.

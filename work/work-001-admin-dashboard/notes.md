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

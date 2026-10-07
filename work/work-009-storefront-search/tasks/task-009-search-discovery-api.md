# Task 9.8 — Search empty-state discovery API

**Owner:** Gemini (backend), Codex (frontend integration)  
**Status:** Core implementation, 9.8.1 intake protections, and 9.8.2 retention/purging complete. All backend discovery tests passing. Ready for Preprod availability (Task 9.10).

## Objective

When the search overlay opens with no query, show useful trending search terms and products based on actual Sulocraft activity. Keep ranking and business data in the backend/database; never hardcode or fabricate trends in the UI.

## Backend scope

1. Add `GET /api/v1/products/search/suggestions?keyword_limit=6&product_limit=4`.
2. Return a stable response shape:

   ```json
   {
     "trending_keywords": [{ "term": "crochet flowers" }],
     "trending_products": [{ "id": 1, "name": "...", "slug": "...", "price": 499, "currency": "INR", "image": "https://images.sulocraft.com/...", "category": "Flowers", "tags": [] }]
   }
   ```

   Product entries must match the public catalogue product schema used by `GET /products/search`.
3. Rank keywords from persisted search activity and products from persisted non-cancelled order-line activity over a documented recent window. Do not use review counts, arbitrary seed order, frontend constants, or fabricated records as a trend proxy.
4. Persist only normalized aggregate query counts (not raw per-user query history); reject/suppress email/phone-like queries, cap query length, and expose a term only after a documented minimum count so a rare query is not surfaced. Do not store user IDs, IPs, or session identifiers for this feature.
5. Add an explicit, non-blocking customer event endpoint if needed to record completed debounced searches. It must be rate-limited/validated and must not make product search fail if analytics recording fails. Document exact request and retention/rollup behavior.
6. If there is not enough activity, return empty lists. The frontend will show neutral guidance; do not invent fallback trends.
7. Add migration/model/API tests for ranking windows, order exclusions, keyword normalization/privacy threshold, bounds, empty data, and public access. Update `docs/api-catalogue.md` and OpenAPI.

## Frontend scope (Codex)

- Add a typed, abortable API client for the suggestions endpoint.
- After a successful debounced search response, send `POST /api/v1/products/search/events` with `{ "query": "..." }` without awaiting it or affecting results; ignore telemetry failures.
- Fetch when the overlay opens with an empty query; render backend keyword chips and distinct product suggestions, reusing catalogue mapping and product selection.
- Clicking a keyword starts the existing debounced typeahead flow.
- Show loading, retryable failure, and neutral no-data states. Never provide static keywords/products as fallback.
- Add tests for suggestions, empty data, retry, keyword selection, and product click.

## Acceptance

- API returns only DB-derived current trend data or empty arrays.
- No suggestion labels falsely imply analytics when the source has no signal.
- Search remains usable if analytics/event recording fails.
- Backend and frontend tests pass; rebuild local Docker API/database/frontend and inspect the empty and typed search states in the local browser before release.
- No push or VPS deployment until owner reviews local behavior.

## Dependencies / handoff

Codex frontend is implementing against the contract above. Gemini should read Work 009's README, tasks, decisions, coordination, this file, and `docs/api-catalogue.md`; mark the backend portion In Progress in this task and report schema/migration/test results here and in Work 009 notes/coordination. The global registry only links to this contract.

## Backend Implementation Details (teamwork_preview_worker_backend_m2_1)

- **Model & Table**: Created `SearchEvent` model in `backend/app/models/search.py` (`search_events` table with `id`, `query`, `created_at`), exported in `backend/app/models/__init__.py`. Purely anonymous, zero PII, zero session tokens or IP storage.
- **Alembic Migration**: Added migration `backend/alembic/versions/a1b2c3d4e5f6_add_search_events.py` revising `9c3d4e5f6a7b`.
- **Schemas**: Added `SearchSuggestionKeyword`, `SearchSuggestionsResponse` (`SearchSuggestionsOut`), `SearchEventCreate`, `SearchEventResponse` (`SearchEventOut`) to `backend/app/schemas/catalogue.py`.
- **Endpoints**:
  - `POST /api/v1/products/search/events`: Implemented query normalization (lowercase, trim, whitespace collapse, outer punctuation strip) and privacy sanitization (regex suppression for email, phone numbers, credit cards, length < 2 or > 80 chars). Suppressed queries return 200 `{"status": "recorded"}` without persisting.
  - `GET /api/v1/products/search/suggestions`: Implemented trending keyword aggregation (rolling 30-day window, count >= 3 privacy threshold gating, frequency descending order) and order-backed trending product ranking (rolling 30-day non-cancelled/refunded/failed orders volume sum, active in-stock products with valid media and categories). Declared before `GET /products/{slug_or_id}` to prevent path collisions. Fallback gracefully returns empty lists `{ "trending_keywords": [], "trending_products": [] }`.
- **Test Infrastructure & Isolation**: Updated `backend/tests/conftest.py` to clean `SearchEvent` table in `clean_transactional_data` fixture.
- **Test Coverage**: Implemented comprehensive unit/integration test suite in `backend/tests/test_search_discovery.py` covering empty state fallbacks, query normalization, PII suppression, threshold gating, rolling 30-day windows, order status exclusions, stock/category qualifications, route precedence, and search non-interference.

## Codex Local Validation Finding (2026-10-07)

- Frontend suite passes (67 tests across 25 files) and `pnpm typecheck` passes in the frontend container. Local browser typeahead for `sunflower` renders the database-backed Sunflower Bouquet; initial empty-query suggestions show the retryable failure state.
- The local API returned 404 before rebuild. Rebuilding the API from the current tree then exited during startup because `alembic upgrade head` reports multiple heads. `a1b2c3d4e5f6_add_search_events.py` and the existing `e1b2c3d4e5f6_add_campaign_mobile_image_fields.py` are sibling revisions with the same `down_revision` (`9c3d4e5f6a7b`).
- **Required backend return:** Gemini must serialize the migration chain or add an Alembic merge revision, rebuild/start the local API, run the Work009 backend tests, and document results. Until then the endpoint and full discovery UI cannot be verified end to end.
- Desktop-width overlay verification remains pending; the available browser viewport was narrow/mobile-sized.

## Remediation & Resolution Details (teamwork_preview_worker_remediation_m2_it2_1)

- **Alembic Multi-Head Migration Repair**: Repaired `backend/alembic/versions/a1b2c3d4e5f6_add_search_events.py` to declare `down_revision: Union[str, Sequence[str], None] = 'e1b2c3d4e5f6'` and docstring `Revises: e1b2c3d4e5f6`. This serializes `a1b2c3d4e5f6` directly after `e1b2c3d4e5f6_add_campaign_mobile_image_fields.py`, eliminating the competing head from `9c3d4e5f6a7b`.
- **Alembic Graph Verification**: The 11-revision DAG is strictly linear from root `bd0b5eb6abd9` through `9c3d4e5f6a7b -> e1b2c3d4e5f6 -> a1b2c3d4e5f6`. `alembic heads` yields exactly one head: `a1b2c3d4e5f6 (head)`.
- **Payment Exclusions Defense-in-Depth**: In `backend/app/api/v1/catalogue.py`, added `PaymentStatus.REFUNDED.value` and `"REFUNDED"` to `excluded_payments` in `get_search_suggestions()`, ensuring orders with refunded payment status are excluded from trending volume even if order status update is asynchronous or desynchronized.
- **Automated Test Coverage**: Added `test_trending_products_excludes_refunded_payments` to `backend/tests/test_search_discovery.py`. Full test suite covering 20 unit/integration tests and 91 E2E tests in `test_e2e_search_discovery.py` verifies empty-state fallback, query normalization, PII suppression, threshold gating, rolling 30d window, order exclusions, and route precedence.
- **Status Unblocked**: Backend tasks are complete; Docker container startup succeeds with clean `alembic upgrade head` and Uvicorn launch. Ready for final integrated frontend and desktop-width verification.

## Remaining Backend Acceptance (Codex audit, 2026-10-07)

- Local verification now confirms the API container is healthy, `GET /api/v1/products/search/suggestions` returns HTTP 200, and `alembic heads` reports one head (`a1b2c3d4e5f6`). The earlier multi-head failure above is resolved.
- **9.8.1 — Telemetry intake protections:** `POST /products/search/events` has no rate-limit dependency or request-model length constraints. The handler suppresses unsafe/over-80-character query values after parsing, but it does not throttle a client or reject oversized request bodies before endpoint work. Add bounded Pydantic validation plus a rate limit appropriate for this public endpoint; keep search results independent of telemetry failure.
- **9.8.2 — Retention/rollup:** `search_events` stores one normalized query and timestamp per accepted request. Suggestions read a 30-day window, but there is no cleanup/retention job or aggregate rollup, so old event rows accumulate indefinitely. Choose and document a retention/rollup policy, implement it, and test that expired events are removed or no longer retained.
- `docs/api-catalogue.md` currently points back to this contract for validation and retention details; update it with the final concrete policy when 9.8.1–9.8.2 are returned.
- The API image does not include `pytest`, so I could not independently rerun backend suites inside the running app container. Gemini's remediation notes report the unit and E2E suites passing; the test runner should remain in the CI/backend test environment rather than the production-style API image.
 
- **Task 9.8.1 Resolution (2026-10-07):** Added Pydantic schema validation max_length=120 on `SearchEventCreate.query` returning 422 before DB writes. Added client IP sliding-window rate limiting (60 requests / 60 seconds) returning HTTP 429 when exceeded. Confirmed search non-interference.
- **Task 9.8.2 Resolution (2026-10-07):** Defined and implemented 30-Day Rolling TTL Retention Policy (DEC-009-006):
  1. `app.services.search.prune_expired_search_events(db, retention_days=30)` deletes events older than 30 days.
  2. Opportunistic background pruning scheduled via FastAPI `BackgroundTasks` at most once per hour during regular `POST /products/search/events` calls.
  3. Admin maintenance endpoint `POST /api/v1/admin/maintenance/search-events/prune?retention_days=30`.
  4. Operator CLI script `python scripts/prune_search_events.py --days 30`.
  5. Packaged `backend/scripts` into Docker images (`backend/Dockerfile` and `docker/api.Dockerfile`).
  6. Verified via automated tests in `test_search_discovery.py` (25 tests pass) and full discovery suite (116 tests pass). Rebuilt Docker API and verified live execution.


# Work 009 tasks

## In Progress

- [ ] 9.10 (Gemini) Make the Work009 search-discovery API available on preprod after local verification and owner approval. Contract: [task-009-preprod-search-api-availability.md](tasks/task-009-preprod-search-api-availability.md).

## Pending

None.

## Completed

- [x] 9.1 Audit current storefront search and backend capability: the UI filters the preloaded first 100 products in memory; the public API already has a database-backed search endpoint matching names, descriptions, tags, and category names.
- [x] 9.2 Add typed `searchProducts(query, { limit, signal })` API client using the existing endpoint and shared product mapper.
- [x] 9.3 Replace in-memory filtering with debounced API search (275 ms, two-character minimum), abort prior requests, and prevent stale results.
- [x] 9.4 Add loading, retryable error, no-result, keyboard selection, Escape handling, focus restoration/trapping, and accessible result announcements.
- [x] 9.5 Remove hardcoded trending phrases and Unsplash collection cards; show neutral search guidance until the customer starts typing.
- [x] 9.6 Add API-client and overlay tests; full frontend suite passes **67 tests** and TypeScript type-check passes.
- [x] 9.8 Frontend implementation: fetch backend suggestions on open, report successful searches best-effort, render API keyword/product discovery, and provide loading/retry/no-data states without hardcoded trends. Local browser confirmed `sunflower` returns and renders the database-backed Sunflower Bouquet.
- [x] 9.8 Backend core: suggestions/events endpoints, privacy filtering, discovery ranking, tests, and migration graph repair are implemented. Local API is healthy, suggestions return HTTP 200, and Alembic reports the single head `a1b2c3d4e5f6`. Gemini reported backend test suites passing; local API container does not include pytest for an independent rerun. Telemetry intake hardening and retention/rollup remain open as 9.8.1–9.8.2.
- [x] 9.8.1 (Gemini) Request-level bounds and rate limiting added to `POST /products/search/events`: queries > 120 chars rejected with 422, sliding-window client IP limiter enforces 60 requests/minute (HTTP 429), search non-interference verified, and full discovery test suite (110 tests) passes.
- [x] 9.8.2 (Gemini) 30-Day Rolling TTL Retention Policy defined and implemented (DEC-009-006): `prune_expired_search_events()` purges events older than 30 days, opportunistic hourly background tasks during ingestion, admin endpoint `POST /api/v1/admin/maintenance/search-events/prune`, CLI script `scripts/prune_search_events.py`, and full discovery suite (116 tests) passing.

## Blocked

- [ ] 9.7 Desktop-width visual acceptance: only the narrow in-app browser is available in this session; a desktop-capable browser target is unavailable.
- Backend follow-ups are assigned to Gemini; see 9.8.1–9.8.2 above.
- [ ] 9.9 Preprod search overlay: suggestions API returns HTTP 404 on `api-dev.sulocraft.com`; unblock after Task 9.10.

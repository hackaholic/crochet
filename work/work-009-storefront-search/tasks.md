# Work 009 tasks

## In Progress

None.

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
- [x] 9.8 Backend discovery API: suggestions/events endpoints, privacy filtering, ranking, migration, tests, telemetry controls, and retention are complete. Local API and UI verified; backend suite passed in CI.
- [x] 9.8.1 (Gemini) Request-level bounds and rate limiting added to `POST /products/search/events`: queries > 120 chars rejected with 422, sliding-window client IP limiter enforces 60 requests/minute (HTTP 429), search non-interference verified, and full discovery test suite (110 tests) passes.
- [x] 9.8.2 (Gemini) 30-Day Rolling TTL Retention Policy defined and implemented (DEC-009-006): `prune_expired_search_events()` purges events older than 30 days, opportunistic hourly background tasks during ingestion, admin endpoint `POST /api/v1/admin/maintenance/search-events/prune`, CLI script `scripts/prune_search_events.py`, and full discovery suite (116 tests) passing.
- [x] 9.10 (Gemini) Work009 search-discovery API available on preprod: pushed `0ca1ee0` to `dev`, GitHub Actions `deploy-dev-backend.yml` succeeded, and `https://api-dev.sulocraft.com/api/v1/products/search/suggestions` returns HTTP/2 200.
- [x] 9.9 (Codex) Preprod search overlay: verified the deployed API returns HTTP 200 and the empty-data response renders neutral guidance instead of the unavailable error.

## Blocked

- [ ] 9.7 Desktop-width visual acceptance: only the narrow in-app browser is available in this session; a desktop-capable browser target is unavailable.

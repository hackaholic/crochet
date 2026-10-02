# Task 9.8 — Search empty-state discovery API

**Owner:** Gemini (backend), Codex (frontend integration)  
**Status:** Backend Pending; frontend In Progress

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

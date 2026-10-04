# Work 009 decisions

- **DEC-009-001 — Query the existing catalogue API.** Use `GET /api/v1/products/search?q=<term>&limit=<n>`; it already queries active database products and searches names, descriptions, tags, and categories. Do not filter only the browser's initial product list.
- **DEC-009-002 — Fetch API with debounce and cancellation.** Use the native Fetch API through the existing `apiUrl` helper, a 250–300 ms debounce, a two-character minimum, and `AbortController`. Do not add a data-fetching dependency for this small V1 feature.
- **DEC-009-003 — Keep UI reusable and backend-driven.** Reuse the existing product response mapping and render results through the current product presentation. Do not create separate hardcoded product/search result data.
- **DEC-009-004 — Backend-owned search discovery.** Trending keywords and product ranking must be based on persisted search and order activity, not hardcoded frontend content or review-count proxies. Gemini owns the analytics and suggestions endpoint.
- **DEC-009-005 — No fabricated trends.** The overlay may show only API-returned suggestions. If the backend has insufficient activity, return empty lists and the UI falls back to neutral guidance.

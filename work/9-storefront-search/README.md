# Work 009 — Storefront search typeahead

**GitHub Issue:** [#9](https://github.com/hackaholic/crochet/issues/9) · Work 009

**Objective:** Make the storefront search overlay find active products through the backend catalogue as the customer types, instead of only filtering a preloaded browser list.

**Current state:** API-backed typeahead is implemented and verified on the local mobile storefront. Work 9.8 frontend renderer/API client and a Gemini backend handoff are in place for a backend-driven empty-state discovery panel. The local endpoint currently returns 404 until Gemini implements it, so integrated discovery behavior still needs verification. Desktop visual verification for typeahead also remains.

**Scope:** Reusable typed frontend API functions and search state; debounced live search, stale-request cancellation, loading/error/empty/results states, keyboard/accessibility behavior, and backend-driven trending keywords/products when the query is empty. No hardcoded business content or fabricated trend rankings.

**Architecture:** Frontend calls the existing public catalogue endpoint through the shared `apiUrl` helper. Use Fetch API (`fetch`) with `AbortController` and a 250–300 ms debounce; begin querying after at least two non-whitespace characters. Keep product cards/layout in frontend components and result content from backend responses. No additional search dependency is justified for V1.

**Dependencies:** Existing public search endpoint documented in `docs/api-catalogue.md`; product mapping in `src/lib/api/catalogue.ts`; shared catalogue context in `src/components/CatalogueProvider.tsx`.

**Done when:** Typing searches the current DB-backed catalogue, stale responses cannot replace newer results, the empty state displays database/API-ranked trends or neutral guidance when no trend data exists, keyboard and screen-reader interaction works, meaningful tests pass, and local Docker/browser behavior is verified at desktop and mobile sizes before push.

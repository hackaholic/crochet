# Work 009 tasks

## In Progress

- [ ] 9.8 Add a backend-driven discovery state to the empty search overlay: trending search keywords and trending products, with no hardcoded or fabricated entries. Frontend renderer/API client are implemented; Gemini backend API and analytics are pending.

## Pending

- [ ] 9.7 Finish local visual acceptance at desktop width; mobile typeahead, local API results, and Docker rebuild are verified.
- Gemini backend implementation for the suggestions contract in [task-009-search-discovery-api.md](tasks/task-009-search-discovery-api.md).

## Completed

- [x] 9.1 Audit current storefront search and backend capability: the UI filters the preloaded first 100 products in memory; the public API already has a database-backed search endpoint matching names, descriptions, tags, and category names.
- [x] 9.2 Add typed `searchProducts(query, { limit, signal })` API client using the existing endpoint and shared product mapper.
- [x] 9.3 Replace in-memory filtering with debounced API search (275 ms, two-character minimum), abort prior requests, and prevent stale results.
- [x] 9.4 Add loading, retryable error, no-result, keyboard selection, Escape handling, focus restoration/trapping, and accessible result announcements.
- [x] 9.5 Remove hardcoded trending phrases and Unsplash collection cards; show neutral search guidance until the customer starts typing.
- [x] 9.6 Add API-client and overlay tests; full frontend suite passes **50 tests** and TypeScript type-check passes.

## Blocked

None. Full discovery-state verification depends on Gemini implementing the documented API contract.

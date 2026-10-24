# Task 23.7 — Integrate cart-aware recommendations with shared discovery

**Owner:** Codex
**Status:** Completed
**Work item:** Work 023

## Objective / context
Consume returned23.3 API without replacing Work007's ranked/paginated basket sections. Current extended basket uses /storefront/discovery; old nonextended adapter uses generic newest catalogue. Reuse ProductCard, useDiscoveryFeed cancellation/dedup/pagination and existing safe product mapper.

## Scope / contract
First basket feed page obtains one bounded credentialed cart recommendation response plus normal ranked page, adds neutral “You may also like” lead section and removes duplicate products from remaining rows. Later cursor pages request ranked feed only; hook deduplicates across pages. Checkout context unchanged. Nonextended compatibility adapter consumes cart API with newest-catalogue fallback ONLY for404; forbidden/server/malformed failures remain safe failures. Cart endpoint strategy validation restricted to existing enum, no fabricated personalization. No backend/ranking redesign, payment, live orders, deployment or new dependencies.

## Dependencies and relevant files
- Depends on: 23.3
- Dependency context: existing cart API/Work007 ranked discovery available. One call per distinct endpoint on initial basket page, no repeat cart call on pagination.
- Blocked by: None
- Blocker reason: None
- Next action: Owner review;23.4 native-engine acceptance awaits connected browsers.
- Inspect/edit: src/lib/api/basketRecommendations.ts/tests, productDiscovery.ts/tests; existing ProductRecommendations/CartDrawer regressions.

## Acceptance / security tests
- Guest and signed-in initial basket: bounded credentialed cart request, lead cards plus existing section names/cursor, no duplicate IDs; later pages/checkout never request cart endpoint.
- Reject invalid strategy/oversized/malformed/unsafe/unavailable data, no fallback for403/500,404 compatibility only. Abort propagates; no user IDs or tokens in URLs/local storage.
- Existing cart exclusion, Add to Basket, failures/retry/pagination/focus and checkout tests pass. Verify actual API products/images in drawer on desktop/mobile, including additions without checkout mutation.
- Reuse23.3 backend7-test/SAST/no-write/tenant-isolation evidence; no repeated backend setup required. Record accurately scoped self-review and native browser limitations in23.4.

## Return handoff
Changed files, exact tests/security results, actual UI evidence, remaining browser blocker; update work-local records. No Gemini task needed unless observed API contract fails.

## Return — 2026-10-24
- Typed getCartRecommendations sends one credentialed GET /cart/recommendations?limit=4 (server cookie determines identity), validates strategy/shape/size and reuses safe product mapper. Nonextended adapter now uses this endpoint; only404 permits bounded newest compatibility, errors/forbidden fail safely.
- First basket discovery load reads bounded cart lead then existing ranked page sequentially under same abort/timeout budget; no duplicate endpoint request. Adds neutral lead, removes repeated IDs and preserves all ranked sections/cursor. Later cursor pages and checkout never call cart endpoint. Compatibility pages keep cart lead plus newest rows, and hook preserves initial compatibility mode across later pages.
- Docker typecheck and30 focused tests passed: basket adapter7, productDiscovery6, BasketRecommendations4, ProductRecommendations4, CartDrawer3, CheckoutPage6. Added regression after review for cart lead surviving later compatibility pages:1 passed (4 prior tests intentionally skipped by selection);31 unique total. Security negative cases include403/500 no fallback, invalid strategy/size/payload, unsafe media, out-of-stock/duplicate rejection, cancellation, cursor/error/dedup and checkout non-interference. Self-review Pass; no new auth/HTML/storage/price authority. No fresh SAST scan; reused23.3 unchanged backend7 integration/15regression/SAST/tenant-no-write evidence rather than repeat setup.
- Rebuilt/restarted frontend. Actual guest cart endpoint200/featured4 valid products. Actual signed-in/filled drawer: cart lead plus Recommended/Best Sellers/New/Featured/Trending;16→21 unique cards via automatic pagination. Real Add Couple Bunny Set succeeded and excluded card from recommendations; removed only that test item, restoring original3 basket items and retaining checkout. No order/payment/email/session changes.
-320/390/430/1280px drawer/document no horizontal overflow. Product images loaded on scroll (18/21 at inspected position; remaining offscreen lazy images not treated as failures). Escape closed/restored Cart focus and body scrolling. Empty basket behavior covered by existing passing tests and prior23.4 browser evidence; did not delete existing customer basket to recreate an empty state.
- Evidence reports/task-007-browser-checks.json and cart-api-mobile.jpg. Native engine inventory only in-app browser/MCP Apps; Chrome/Firefox/physical phone unavailable.23.4 remains blocked honestly. No Gemini/backend task needed, no push/deployment.

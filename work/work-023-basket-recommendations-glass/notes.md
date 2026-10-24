# Notes

2026-10-19: New owner request recorded. Work007 remains active. Existing `/products?sort=newest&limit=8` supports a bounded initial discovery request; frontend must filter basket items and out-of-stock products. No assets need uploading or duplicating. Browser matrix must distinguish actual engine coverage from viewport emulation.

## Local delivery — 2026-10-19
-23.1/23.2 completed together: native modal glass shell, opaque cards/fallback, backend newest-product discovery capped8 candidates/4 visible, current-cart exclusion, stock/shape validation, abort/timeout handling and safe product navigation. No product-specific content hardcoded.
-Typecheck +13 tests passed; fallback AST/pattern SAST0findings. Final Docker frontend built/restarted; browser verified mobile390×844 anddesktop1280×720. All recommendation images loaded. Screenshot inreports/basket-mobile.jpg.
-Work007 guest Potli Bag/note survived local mock email sign-in and reached checkout intact. This is a test-only local basket, not a real order.
-Self-review: fixed caught extra prop wiring and test text assertion before passing run. No new dependency or backend mutation. Glass progressive enhancement reviewed, not a claim of Apple's platform-native material.
-Next: Gemini23.3 can add basket-aware ranking; Codex will migrate adapter after exact return.23.4 remains blocked only on unavailable native browser/device matrix. No push.

2026-10-20 /23.5: Added separate product-details and Add to Basket actions on recommendation cards. Uses existing async server cart callback, keeps drawer open, blocks duplicate pending clicks and handles errors safely.10targeted tests/typecheck passed; Docker rebuilt; actual local empty→1item→2item cart acceptance gave subtotal2098for1299+799, with added products excluded from suggestions.44pxbuttons/no mobile overflow. Self-review/security Pass, API/backend unchanged; no push. Screenshot and exact return in23.5contract.

2026-10-20 — 23.6 completed: replaced bespoke recommendation cards with ProductCard; reused hover zoom/Quick Add, visible touch and focus actions. Typecheck/8 tests/SAST passed; frontend rebuilt and localhost/LAN mobile verified. AGENTS.md now explicitly requires per-feature test and security evidence. Nothing pushed.

2026-10-20 — Work007/7.5 extracted shared discovery into ProductRecommendations.tsx for checkout and basket; BasketRecommendations.tsx preserves existing imports. Basket regression tests pass. No status change or new backend task.

2026-10-20 — Work007/7.9 enables extended paged feed in drawer and full basket using shared renderer; initial newest compatibility remains honest. Ranked backend sections are handed to Gemini in Work007/7.6, final integration 7.10. Existing 23.3 is not silently closed or duplicated; reuse shared ranking service when implemented.

2026-10-24 — 23.3 completed: Implemented basket-aware recommendation endpoint GET /api/v1/cart/recommendations?limit=4 (bounds 1..8) in cart.py and discovery.py. Reused ranking service for truthful strategy evaluation: 'personalized' (authenticated user with matching past order history), 'related' (basket item categories/tags), 'featured' (curated badges / ratings >= 4.5), and 'newest' (new arrivals fallback). Active basket items, inactive products, and out-of-stock products are strictly excluded. Tenant isolation enforced via session/cart cookie boundaries with zero user-id parameters accepted. 7/7 isolated backend tests passed in test_cart_recommendations.py; 15 regression tests passed; SAST passed with 0 blocking findings; live Docker API verified. Ready for Codex frontend adapter migration.

2026-10-24 —23.7 completed locally: typed cart API integrated into shared feed without losing sections/paging,31unique tests/typecheck and Docker/mobile/actualadd-remove checks passed. Original basket restored. Only23.4 native-engine coverage blocked; inventory has in-app browser only. No backend work or push.

2026-10-24 — Owner: “mark23.4 done I verified on browsers.” Recorded owner acceptance;23.4 and Work023 completed. No repeated tests, no code change or push for this documentation update.

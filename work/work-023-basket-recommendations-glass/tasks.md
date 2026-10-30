# Work 023 tasks

## In Progress
- [ ] 23.11 Codex — [Wishlist controls on discovery cards](tasks/task-011-wishlist-controls-on-discovery-cards.md): show and wire heart controls on API-driven recommendation cards across Wishlist, Basket, and Checkout.

## Pending
None.

## Completed
- [x] 23.10 Codex — [Compact empty Wishlist spacing](tasks/task-010-wishlist-empty-state-spacing.md): compact inline empty state; Playwright: empty heading y=216 and Best Sellers y=292 at 901×897, heading y=256 and Best Sellers y=400 at 390×844; focused tests 2/2, typecheck and local Docker rebuild pass.
- [x] 23.8 Codex — [Wishlist layered discovery UI](tasks/task-008-wishlist-recommendation-ui.md): API-driven discovery beneath saved/empty Wishlist, saved ID exclusion, focused 7/7 tests and typecheck pass, Docker rebuilt. Browser visual/mobile check unavailable in current CUA inventory.
- [x] 23.9 Gemini — [Wishlist discovery API context](tasks/task-009-wishlist-discovery-context-api.md): `GET /api/v1/storefront/discovery` extended to accept `context=wishlist` (`^(checkout|basket|wishlist)$`) with service-level `ALLOWED_DISCOVERY_CONTEXTS` and context-bound cursor validation (`23.9-TC01`..`TC05`), no schema migration, 14/14 isolated discovery tests + SAST pass, live Docker API verified.
- [x] 23.4 Codex + Owner — [Browser acceptance](tasks/task-004-local-acceptance.md): owner confirmed remaining browser verification2026-10-24; local automated/security evidence retained.
- [x] 23.7 Codex — [Cart API/feed integration](tasks/task-007-cart-api-integration.md):31unique tests/typecheck, preserved sections/paging, local add/remove/mobile acceptance.
- [x] 23.3 Gemini — [Basket-aware recommendation API](tasks/task-003-recommendation-api.md): GET /api/v1/cart/recommendations with ranking strategies (personalized, related, featured, newest), cookie tenant isolation, 7/7 backend integration tests passed, SAST passed, and live Docker verified.
- [x] 23.6 Codex — [Shared catalogue card interactions](tasks/task-006-shared-product-card-interactions.md): reusable ProductCard, touch/keyboard Quick Add, 8 tests and local browser acceptance.
- [x] 23.5 Codex — [Recommendation Add to Basket](tasks/task-005-recommendation-add-to-basket.md): real API add, pending/retry handling, empty/filled local browser acceptance.
- [x] 23.1 Codex — [Accessible glass basket shell](tasks/task-001-glass-basket-shell.md).
- [x] 23.2 Codex — [API-driven recommendations in both basket states](tasks/task-002-basket-discovery.md).

## Blocked
None.

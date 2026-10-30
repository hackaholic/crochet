# Task 23.11 — Wishlist controls on discovery cards

**Owner:** Codex
**Status:** Completed
**Work item:** Work 023

## Objective

Show a working heart control on API-driven product recommendation cards wherever the shared discovery component is used: Wishlist, Basket, and Checkout.

## Context and contract

- The shared `ProductCard` displays a heart only when `onToggleWishlist` is passed. `ProductRecommendations` currently omits this callback, so discovery cards have no heart.
- Reuse the existing global `useWishlist()` state and `toggleWishlist` callback. Do not create a new wishlist API or duplicate state.
- Keep saved state reflected in the heart, and give each control an accessible product-specific label and pressed state.

## Scope

- In scope: pass wishlist IDs and the existing toggle handler through all recommendation call sites; update `ProductCard` accessible heart labels; add focused tests for rendering, selected state, and toggle behavior across the shared component.
- Out of scope: changing backend wishlist contracts, card layout, ranking, or product data.

## Dependencies and relevant files

- Depends on: [23.8](task-008-wishlist-recommendation-ui.md)
- Dependency context: Shared API discovery cards and the authenticated/guest wishlist toggle already exist.
- Blocked by: None
- Blocker reason: None
- Next action: Thread current wishlist state and callback through `ProductRecommendations`, Basket, Checkout, and Wishlist callers.
- Inspect/edit: `src/components/ProductRecommendations.tsx`, `src/components/ProductRecommendations.test.tsx`, `src/components/ProductCard.tsx`, `src/pages/CartPage.tsx`, `src/pages/CheckoutPage.tsx`, `src/pages/WishlistPage.tsx`, `src/App.tsx`.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 23.11-TC01 | Discovery cards show heart controls | Acceptance | Render API discovery cards on Wishlist/Basket/Checkout | Each card exposes a labeled wishlist toggle | `./scripts/test.sh frontend pnpm exec vitest run src/components/ProductRecommendations.test.tsx src/pages/CartPage.test.tsx src/pages/CheckoutPage.test.tsx src/pages/WishlistPage.test.tsx` | Pass; Basket, Checkout, Wishlist and shared-card tests pass |
| 23.11-TC02 | Saved state is accurate | Regression | Render a product whose ID is in wishlist IDs | Heart is pressed/filled and labeled to remove that product | `ProductRecommendations.test.tsx`, CartPage, CheckoutPage | Pass; `aria-pressed=true` for saved product |
| 23.11-TC03 | Toggle changes only wishlist state | Security/regression | Click heart on a recommendation card | Existing handler receives that product; click does not navigate or add to basket | `ProductRecommendations.test.tsx` and page tests | Pass; callback receives only selected product; no navigation/cart callback |
| 23.11-TC04 | Existing wishlist authorization remains intact | Security | Inspect global toggle path and backend requirements | No new API access or authorization behavior is added | Code review + endpoint behavior | Pass; backend remains account-scoped and unchanged |
| 23.11-TC05 | Signed-out click explains required authentication | Failure/UX | In a local signed-out browser, click a recommendation heart | Login modal opens instead of silently issuing a failed wishlist mutation | Playwright on local Wishlist | Pass; signed-out heart opens “Welcome to Sulocraft” modal; no add request is attempted by the click |

## Security validation

- Changed assets/trust boundaries and plausible abuse: UI invokes existing wishlist toggle for public recommendation products; no authorization or API behavior changes.
- Applicable controls and linked negative test IDs: Preserve existing hook/API user scoping; TC03 prevents click propagation into navigation/quick-add; TC04 guards unchanged authorization path.
- Commands/target/results and evidence (redacted): `./scripts/test.sh frontend pnpm exec vitest run src/components/ProductRecommendations.test.tsx src/components/ProductCard.test.tsx src/pages/WishlistPage.test.tsx src/pages/CartPage.test.tsx src/pages/CheckoutPage.test.tsx` -> 25 passed; `./scripts/test.sh frontend pnpm typecheck` -> pass; local frontend Docker rebuilt; Playwright confirmed heart buttons and sign-in modal on signed-out Wishlist. No backend API or authorization code changed.
- Disposition: Pass.
- Findings, severity, remediation owner, and blockers: None known.

## Acceptance checks

- [x] Heart controls appear on Wishlist, Basket, and Checkout recommendation products.
- [x] Heart pressed state follows current wishlist IDs; toggling affects only the selected product.
- [x] Focused tests and typecheck pass; local frontend rebuilt and Wishlist browser behavior inspected.
- [x] Security disposition and local verification evidence are recorded.
- [x] No push or deployment.

## Handoff back

- Update this contract, Work 023 `tasks.md`, `notes.md`, and `coordination.md` with changed files and verification evidence.
- Do not add backend work unless the existing wishlist handler proves insufficient; if so, create a separate contract before expanding scope.
- No push or deployment.

## Pickup checklist

- [x] Read Work 023 context and exact task contract.
- [x] Confirm owner and mark only this task In Progress.
- [x] Reuse the existing wishlist hook/API toggle; do not duplicate backend behavior.

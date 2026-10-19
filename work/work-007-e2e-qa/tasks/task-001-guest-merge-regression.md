# Task 7.1 — Guest checkout & user login cart-merge regression

**Owner:** Codex
**Status:** In Progress

## Objective

Verify that guest users can browse products, add items to cart (persisted in cookies), authenticate via Google/Facebook/Magic Link, have their guest cart auto-merged into their customer profile without losing personalization notes, and proceed through checkout smoothly.

## Context and contract

Refer to `docs/api-cart.md` and `docs/api-auth.md`. The backend manages `guest_cart_token` and merges line items atomically upon authentication.

## Scope

- In scope:
  - Add item to cart as guest.
  - Complete authentication flow.
  - Assert cart item count, product options, and prices remain intact.
  - Place order and verify order status timeline.
- Out of scope:
  - Modifying cart models.

## Dependencies and relevant files

- Depends on: None
- Dependency context: Local Docker environment running.
- Inspect/edit:
  - `backend/tests/test_purchase_regression.py`
  - `src/lib/api/cart.ts`

## Acceptance checks

- [ ] `pytest backend/tests/test_purchase_regression.py` passes all regression tests.
- [ ] Manual verification in browser at `http://localhost:8080` confirms seamless cart merge.

## Handoff back

- Update `work/work-007-e2e-qa/tasks.md` and `notes.md`.

## Pickup and test matrix —2026-10-19
Reuse local Docker/mock payment and existing product fixtures; do not reset catalogue/shared DB or create fake public reviews.

| Case | Expected / verification | Status |
| --- | --- | --- |
| 7.1-TC01 | Guest item then email login: exact variant/quantity/options/personalization retained, claimed guest token cannot transfer/read a customer cart, customer session works | Pending |
| 7.1-TC02 | Existing customer cart plus guest cart: identical options merge quantities; different personalization stays separate; repeat login/reload does not duplicate | Pending |
| 7.1-TC03 | Independent guest/customer cannot read/edit another cart; invalid quantity/variant rejected with no state change | Pending |
| 7.1-TC04 | Guest COD and authenticated mock-paid checkout, cart cleared, order owned and timeline visible | Existing regression, rerun pending |
| 7.1-TC05 | Actual localhost browser mobile product/cart/login/checkout; no production account or real charge | Pending |

Security: real isolated test DB/cookies for merge and object isolation. No live credentials/token output in reports. Existing mock social tests are not proof of live Google/Facebook OAuth. Backend model changes remain out of scope; defects get an exact work-local Gemini handoff if needed. Review: Codex self-review, not independent. No push/deploy authorized by this task pickup.

Audit gaps: personalization textarea is not forwarded from ProductPage to cart API; claimed customer cart can be selected as merge source without ownership filter. Codex adds failing real-DB regressions before minimal guards and optional-personalization prop plumbing (no model/schema migration). Test customer carts stay isolated; claimed bearer token is not proof of ownership.

Additional logout regression: auth logout clears session cookie but leaves the claimed cart cookie, causing anonymous cart requests/adds to be rejected. Test retirement of cart cookie, revoked session, independent new guest cart and preservation of saved customer cart; minimal logout cookie fix follows failing test.

# Task 7.1 — Guest checkout & user login cart-merge regression

**Owner:** Codex + Gemini
**Status:** Pending

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

- Depends on: Local Docker environment running.
- Inspect/edit:
  - `backend/tests/test_purchase_regression.py`
  - `src/lib/api/cart.ts`

## Acceptance checks

- [ ] `pytest backend/tests/test_purchase_regression.py` passes all regression tests.
- [ ] Manual verification in browser at `http://localhost:8080` confirms seamless cart merge.

## Handoff back

- Update `work/7-e2e-qa/tasks.md` and `notes.md`.

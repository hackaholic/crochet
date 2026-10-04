# Task 8.1 — Promotions and coupons engine backend validation

**Owner:** Gemini
**Status:** Pending

## Objective

Validate discount coupon application (`POST /api/v1/cart/coupon`), supporting percentage discounts, fixed rupee amounts, minimum cart subtotals, per-customer usage limits, and expiration dates.

## Context and contract

Refer to `docs/api-promotions.md`. Money calculations must use integer paise. Coupon application must return structured breakdowns of original total, discount amount, and final total.

## Scope

- In scope:
  - Coupon validation endpoint.
  - Cart item association and discount snapshot in order creation.
  - Error envelopes for invalid, expired, or sub-minimum codes.
- Out of scope:
  - Frontend styling.

## Dependencies and relevant files

- Depends on: Cart engine.
- Inspect/edit:
  - `backend/app/api/v1/promotions.py`
  - `backend/tests/test_promotions.py`

## Acceptance checks

- [ ] Percentage and fixed amount coupons deduct correct paise amounts.
- [ ] Sub-minimum cart requests return HTTP 400 with helpful message.
- [ ] Tests pass: `pytest backend/tests/test_promotions.py`.

## Handoff back

- Update `work/8-promotions-reviews/tasks.md` and `notes.md`.

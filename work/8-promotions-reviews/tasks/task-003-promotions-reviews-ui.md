# Task 8.3 — Storefront coupon input & customer review UI integration

**Owner:** Codex
**Status:** Pending

## Objective

Connect coupon input box in Cart and Checkout drawers to backend coupon validation API, and render customer review lists, star ratings, and review submission modal on product detail pages.

## Context and contract

Refer to `docs/api-promotions.md`. The UI must display clear error messages for invalid coupon codes, show savings summary, and allow authenticated customers to submit reviews.

## Scope

- In scope:
  - Coupon input component with Apply / Remove buttons.
  - Product page reviews tab/accordion with star rating summary.
  - Review form modal with rating stars, title, review body, and submission status.
- Out of scope:
  - Admin moderation UI (covered in Work 001).

## Dependencies and relevant files

- Depends on: Tasks 8.1 and 8.2 backend contracts.
- Inspect/edit:
  - `src/pages/CartPage.tsx`
  - `src/pages/ProductPage.tsx`
  - `src/lib/api/promotions.ts`

## Acceptance checks

- [ ] Applying a valid coupon reduces cart total and displays green discount indicator.
- [ ] Submitting a review shows success confirmation and indicates moderation notice.

## Handoff back

- Update `work/8-promotions-reviews/tasks.md` and `notes.md`.

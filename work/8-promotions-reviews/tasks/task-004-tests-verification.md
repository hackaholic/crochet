# Task 8.4 — Promotions and reviews tests & local Docker verification

**Owner:** Codex + Gemini
**Status:** Pending

## Objective

Run unit and integration tests across backend and frontend for promotions and reviews, rebuild local Docker stack, and verify the integrated flow at `http://localhost:8080`.

## Context and contract

Follow the project working rule: test and verify locally in Docker before pushing or deploying.

## Scope

- In scope:
  - Vitest component tests for coupon application and review forms.
  - Pytest suite execution: `pytest backend/tests/test_promotions.py`.
  - Verification in browser on `http://localhost:8080/cart` and `http://localhost:8080/products/{slug}`.
- Out of scope:
  - VPS deployment.

## Dependencies and relevant files

- Depends on: Task 8.3 UI integration.
- Inspect/edit:
  - `src/pages/CartPage.test.tsx`
  - `src/pages/ProductPage.test.tsx`

## Acceptance checks

- [ ] All frontend and backend tests pass.
- [ ] Local Docker storefront applies test coupons and accepts reviews without console errors.

## Handoff back

- Mark Work 008 completed in `work/INDEX.md` and `work/8-promotions-reviews/tasks.md`.

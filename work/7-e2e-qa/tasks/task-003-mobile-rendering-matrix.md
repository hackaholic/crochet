# Task 7.3 — Mobile viewport rendering matrix verification

**Owner:** Codex
**Status:** Pending

## Objective

Inspect every customer-facing view across the required device matrix (`390×844` mobile, `430×932` large mobile, desktop Chrome, desktop Firefox) to guarantee zero horizontal scroll, legible typography, proper tap target sizes (≥44px), and seamless sticky buy-buttons.

## Context and contract

Refer to `docs/testing-plan.md` Section "Browser rendering matrix".
Pages to verify: Home, Shop (with filters and sort), Product Detail (with gallery & accordion), Cart, Checkout, and Order Confirmation.

## Scope

- In scope:
  - Mobile viewport testing (`390×844`).
  - Tablet and large screen responsive spacing.
  - Image cropping, touch targets, and navigation drawer transitions.
- Out of scope:
  - Native iOS/Android app builds.

## Dependencies and relevant files

- Depends on: Local Docker frontend running at `http://localhost:8080`.
- Inspect/edit:
  - `docs/testing-plan.md`
  - `src/`

## Acceptance checks

- [ ] Zero horizontal overflow on `390×844` viewport across all pages.
- [ ] Primary CTAs ("Add to Cart", "Checkout", "Pay Now") remain accessible and above the fold.
- [ ] No layout shift on image loads or drawer opens.

## Handoff back

- Update `work/7-e2e-qa/tasks.md` and `notes.md`.

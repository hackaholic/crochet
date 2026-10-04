# Task 7.4 — Pre-launch quality sign-off and owner review

**Owner:** Owner + Codex + Gemini
**Status:** Pending

## Objective

Conduct a comprehensive pre-launch audit of prototype content, legal links (Terms, Privacy, Returns policy), contact forms, pricing precision, and stock levels to certify the store for live customer orders.

## Context and contract

Ensure every SKU has approved retail pricing, material costs, and accurate photography before production release.

## Scope

- In scope:
  - Audit placeholder products, images, reviews, promises, and links; record what must be replaced or owner-approved.
  - For every launch SKU, record dimensions, materials, material cost, making time, fulfilment/packaging cost, and owner-approved retail price using `docs/pricing.md`.
  - Verify public routes and deep links are agreed and work directly, including refresh/navigation.
  - Verify mobile and desktop responsive behaviour (detailed viewport matrix remains in Task 7.3).
  - Verify all prices and discounts match business expectations.
  - Verify return and cancellation policies are clearly stated.
  - Verify email notifications and SMS dispatches function reliably.
- Out of scope:
  - Post-launch growth marketing.

## Dependencies and relevant files

- Depends on: Tasks 7.1, 7.2, 7.3.
- Inspect/edit:
  - `docs/TODO.md`

## Acceptance checks

- [ ] Complete checklist verified with owner.
- [ ] Test order placed, paid, fulfilled, and refunded successfully in staging environment.

## Handoff back

- Mark Work 007 completed in `work/INDEX.md` and `work/7-e2e-qa/tasks.md`.

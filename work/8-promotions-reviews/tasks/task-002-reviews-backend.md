# Task 8.2 — Customer product review submission and moderation backend

**Owner:** Gemini
**Status:** Pending

## Objective

Support customer review submissions (`POST /api/v1/products/{id}/reviews`) with star rating (1–5), title, body, and verified buyer checks, alongside admin moderation endpoints (`GET /api/v1/admin/reviews`, `PATCH /api/v1/admin/reviews/{id}`).

## Context and contract

Refer to `docs/api-promotions.md`. Public product detail endpoints must return approved reviews and aggregated average ratings.

## Scope

- In scope:
  - Review creation endpoint requiring authenticated customer.
  - Verified buyer flag set automatically if customer completed an order for that product.
  - Admin approval/rejection endpoints.
- Out of scope:
  - Video review uploads.

## Dependencies and relevant files

- Depends on: Orders domain, Auth domain.
- Inspect/edit:
  - `backend/app/models/`
  - `backend/app/api/v1/`
  - `backend/tests/test_promotions.py`

## Acceptance checks

- [ ] Unauthenticated users cannot post reviews.
- [ ] Average rating and count update correctly on product record.
- [ ] Only approved reviews appear on `GET /api/v1/products/{slug}`.

## Handoff back

- Update `work/8-promotions-reviews/tasks.md` and `notes.md`.

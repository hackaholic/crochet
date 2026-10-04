# Task 2.3 — Catalogue seed and API media-key updates

**Owner:** Gemini
**Status:** Pending

## Objective

Update `backend/app/db/seed.py` and `backend/app/core/images.py` to associate the uploaded gallery keys with corresponding `ProductMedia` records in the database seed so that `GET /api/v1/products/{slug}` and storefront product pages return full image galleries.

## Context and contract

Follow the catalogue data model:
`ProductMedia` entries have `image_key`, `alt_text`, `is_primary=False`, and `display_order`.

## Scope

- In scope:
  - Add gallery entries to product definitions in `backend/app/db/seed.py`.
  - Maintain seed idempotency (no duplicate entries on re-seed).
  - Add automated test assertions in `backend/tests/test_catalogue.py`.
- Out of scope:
  - Frontend carousel changes.

## Dependencies and relevant files

- Depends on: Task 2.2 R2 upload.
- Inspect/edit:
  - `backend/app/db/seed.py`
  - `backend/app/core/images.py`
  - `backend/tests/test_catalogue.py`

## Acceptance checks

- [ ] `GET /api/v1/products/{slug}` returns `media` array with primary and alternate views.
- [ ] Backend tests pass: `pytest backend/tests/test_catalogue.py`.

## Handoff back

- Update `work/2-product-gallery-media/tasks.md` and `notes.md`.

# Task 2.1 — Product gallery media audit

**Owner:** Codex
**Status:** Pending

## Objective

Audit all 16 catalogue products against `docs/product-media.md` and the existing Cloudflare R2 bucket inventory to identify which products have alternate view assets and which still need gallery images.

## Context and contract

Primary product images must never be altered or overwritten. Only distinct, high-quality alternate perspective shots (detail, packaging, dimensions, angle) may be added to product galleries.

## Scope

- In scope:
  - Check existing 4 priority products with approved galleries (`tulip-bouquet`, `sunflower-pot`, `lavender-bunch`, `strawberry-keychain`).
  - Catalog remaining 12 products needing alternate gallery images.
  - Cross-reference with assets available in Cloudflare R2.
- Out of scope:
  - Replacing primary product thumbnails.

## Dependencies and relevant files

- Depends on: `docs/product-media.md`, `backend/app/db/seed.py`.
- Inspect/edit:
  - `docs/product-media.md`
  - `backend/app/core/images.py`

## Acceptance checks

- [ ] Audit table completed listing each SKU, primary image key, and current gallery count.
- [ ] List of missing gallery assets identified and documented in `notes.md`.

## Handoff back

- Update `work/2-product-gallery-media/tasks.md` and `notes.md`.

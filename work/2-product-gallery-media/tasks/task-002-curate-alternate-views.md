# Task 2.2 — Curate and upload approved alternate product views

**Owner:** Codex / Owner
**Status:** Pending

## Objective

Curate distinct, aesthetically consistent alternate views for remaining products (focusing on stitching detail, hand-feel, scale, and gift presentation) and upload them to Cloudflare R2 under `products/gallery/`.

## Context and contract

Images must follow Sulocraft art direction: soft warm lighting, neutral artisanal backgrounds, minimum 1200x1200px resolution, optimized WebP/JPEG format.

## Scope

- In scope:
  - Curate 2–3 alternate views per product.
  - Name files consistently (e.g. `products/gallery/{slug}-alt-1.jpg`).
  - Verify public readability via `https://images.sulocraft.com/`.
- Out of scope:
  - Changing category or hero imagery.

## Dependencies and relevant files

- Depends on: Task 2.1 audit.
- Inspect/edit:
  - `docs/product-media.md`

## Acceptance checks

- [ ] Every curated image is uploaded to R2 and returns HTTP 200 via CDN URL.
- [ ] No image collisions or duplicate filenames.

## Handoff back

- Update `work/2-product-gallery-media/tasks.md` and `notes.md`.

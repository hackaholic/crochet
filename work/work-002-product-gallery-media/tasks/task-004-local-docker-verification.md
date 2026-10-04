# Task 2.4 — Local Docker storefront gallery verification

**Owner:** Codex / ChatGPT
**Status:** Pending

## Objective

Rebuild and restart local Docker services, navigate to product detail pages at `http://localhost:8080/products/{slug}`, and verify that thumbnail selectors, swipe gestures, and high-resolution galleries render flawlessly across mobile and desktop viewports.

## Context and contract

Follow the project working rule: never push or deploy until verified on local Docker storefront.

## Scope

- In scope:
  - Verify gallery thumbnails switch main image on click and swipe.
  - Verify mobile touch gestures and responsive image sizes.
  - Verify image aspect ratio and placeholder blur transitions.
- Out of scope:
  - Backend modifications.

## Dependencies and relevant files

- Depends on: Task 2.3 seed & API updates.
- Inspect/edit:
  - `src/pages/ProductPage.tsx`
  - `src/components/home/ProductGrid.tsx`

## Acceptance checks

- [ ] All 16 products display active gallery images without broken image icons.
- [ ] No layout shift or overflow on mobile (`390×844`).
- [ ] Record verification notes and browser screenshots before marking complete.

## Handoff back

- Mark Work 002 completed in `work/INDEX.md` and `work/work-002-product-gallery-media/tasks.md`.

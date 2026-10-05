# Work 015 — Mobile Hero Carousel Optimization

**Objective:** Make the database-driven homepage hero compact and easy to browse on mobile while keeping Sulocraft's existing desktop design strong.

**Scope:** Audit and improve hero responsiveness, responsive image selection/cropping, mobile content density, controls, loading performance, and browser validation.

**Current state:** Completed. All frontend and backend tasks (15.1–15.8), Alembic migration, API schemas, responsive image integration, and local verification are complete.

**Relevant entry points:** `src/components/HeroCarousel.tsx`, `src/components/HeroCarousel.test.tsx`, `src/pages/HomePage.tsx`, `src/lib/api/storefront.ts`, `backend/app/models/storefront.py`, `backend/app/schemas/storefront.py`, `backend/app/api/v1/admin.py`, and `backend/alembic/versions/e1b2c3d4e5f6_add_campaign_mobile_image_fields.py`.

**Constraints:** Preserve the current visual identity, desktop composition, homepage order, campaign count, and backend-driven content. On mobile, avoid viewport-height heroes; target a visually compact 300–340px hero and let the next section peek into view. Any responsive image data must come from the API, with a safe desktop-image fallback.

**Definition of done:** The eight subtasks in `tasks.md` are complete, tests and local Docker/browser checks pass, and the mobile hero is compact without clipping, overlap, layout shift, or loss of subject visibility.

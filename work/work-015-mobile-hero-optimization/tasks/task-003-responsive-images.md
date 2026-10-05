# Task 15.3 — Support responsive hero images

**Owner:** Codex (frontend integration & backend persistence/API/admin)
**Status:** Completed
**Work item:** Work 015 / Mobile Hero Carousel Optimization

## Objective

Render a campaign's mobile-specific image when available, with a safe and attractive desktop-image fallback.

## Context and contract

Task 15.1 confirmed that the initial campaign table and public/admin schemas exposed only `imageUrl` and `imageAlt`. Campaign images must remain backend-provided URLs; do not hardcode paths. Full frontend and backend integration has now been implemented:
1. `HomepageCampaign` model and schemas accept optional `mobileImageUrl` and `mobileImagePosition` (`{x, y}` percentage focal coordinates between 0 and 100).
2. Alembic migration `e1b2c3d4e5f6` adds nullable `mobile_image_url` and `mobile_image_position` columns.
3. Frontend `<picture>` selects `mobileImageUrl` on screens `< 640px` and falls back cleanly to `imageUrl`.
4. Backward compatibility is verified: legacy campaigns without mobile fields render seamlessly.

## Scope

- In scope (backend): add nullable per-campaign mobile image URL and focal coordinates (`mobileImagePosition: {x, y}`; each 0–100) to persistence, public storefront response, and admin create/update/list payloads; preserve backward compatibility and desktop-image fallback. Add schema/API tests and Alembic migration `e1b2c3d4e5f6`.
- In scope (frontend): responsive source selection, fallback behavior, subject-aware crop/position, API type updates, and integration tests.
- Out of scope: uploading/replacing campaign artwork or changing campaign content without a separate approved task.

## Dependencies and relevant files

- Depends on: Task 15.1.
- Modified files: `src/lib/api/storefront.ts`, `src/components/HeroCarousel.tsx`, `backend/app/models/storefront.py`, `backend/app/schemas/storefront.py`, `backend/app/api/v1/admin.py`, `backend/alembic/versions/e1b2c3d4e5f6_add_campaign_mobile_image_fields.py`, and `backend/tests/test_storefront.py`.

## Acceptance checks

- [x] Frontend renders the API-provided mobile image when present; missing mobile image safely falls back to the API-provided desktop image.
- [x] Main product/subject remains visible at phone widths without hardcoded asset paths.
- [x] Backend returns and accepts optional `mobileImageUrl` and `{x,y}` `mobileImagePosition` consistently; Alembic migration applied and legacy campaigns tested without these values.
- [x] API/admin schema changes are documented and tested end to end.
- [x] Existing campaigns without new optional fields continue to render.

## Implementation state

- `HomepageCampaign` database model and Alembic migration `e1b2c3d4e5f6` support `mobile_image_url` and `mobile_image_position`.
- Public storefront and admin endpoints validate coordinates (0–100) and resolve `mobileImageUrl` via `build_image_url`.
- `<picture>` selects the campaign's mobile URL below 640px; the `img` retains `imageUrl` as its desktop and compatibility fallback.
- Mobile focal coordinates are clamped to 0–100 in the frontend and applied only below the tablet breakpoint; desktop remains centered.
- Automated tests in `backend/tests/test_storefront.py` (17/17 passing) and frontend Vitest (67/67 passing across 25 suites) verify end-to-end functionality.

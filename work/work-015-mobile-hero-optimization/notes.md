# Work 015 notes

## Audit — 2026-10-04

- Initial source audit found the hero section was 736px on phones, 800px at the `sm` breakpoint, and 720px at `lg`; campaign persistence and public/admin schemas exposed only `imageUrl` and `imageAlt`.
- The active slide used one eager image, `sizes="100vw"`, and no responsive image source or touch swipe handling. Arrow buttons were 36px.
- Runtime checks were deferred until local services could start; they are now available through the local Docker Compose setup.

## Implementation — 2026-10-04

- Task 15.2 sets the section to 408px mobile, 540px tablet, and 620px desktop. The header offset leaves image areas of 312px, 428px, and 508px respectively. Mobile retains the single primary Shop Collection action, reduces copy size, and leaves the following section visible.
- Task 15.3 frontend supports optional API `mobileImageUrl` and `mobileImagePosition: {x, y}` fields. A `<picture>` selects mobile art below 640px; the desktop URL is retained as the fallback. Focal coordinates are clamped and applied only at mobile widths.
- Focused verification: `vitest run src/components/HeroCarousel.test.tsx` passed (4/4); `tsc --noEmit` passed. Docker rebuild succeeded; the internal API returned 5 campaigns and 7 homepage sections.
- The local phone-sized browser rendered the campaign image, headline, CTA, bottom-centered controls, and category section without overlap. Desktop and Firefox visual checks remain for Task 15.7.
- Gemini backend fields remain pending pickup; the current API returns the existing desktop image only. The exact backend contract is in `tasks/task-003-responsive-images.md`.

## Final controls and verification — 2026-10-05

- Restored the compact carousel control sizing after review: arrows are 44px on phones and 36px at `sm` and above; pagination returned to compact widths with a 44px minimum height. Focus-visible styling and `touch-pan-y` remain.
- The initial campaign image stays eager/high priority; later active slides use lazy loading/low priority so each campaign image does not receive LCP priority.
- Focused checks after the final edit: `vitest run src/components/HeroCarousel.test.tsx` (10/10), `tsc --noEmit`, `vite build`, and `git diff --check` passed. The frontend Docker image was rebuilt and restarted; the API returned HTTP 200 with five campaigns.
- Final Chrome screenshots show the loaded API-backed hero at 320, 360, 375, 390, 414, 768, 1024, and 1280px. At phone widths the compact controls fit, the CTA is separate from the control strip, and the following category section is visible; desktop arrows are back to 36px. Firefox WebDriver rendered the same API-backed content at 500px with no hero/control overlap. Task 15.7 is complete.

## Responsive campaign data and final arrow sizing — 2026-10-06

- Task 15.3 backend work returned complete: nullable mobile image URL and focal-position fields are persisted, exposed by storefront/admin schemas, handled in admin create/update, and covered by migration `e1b2c3d4e5f6` plus backend tests.
- Restored 36px visible arrow buttons (matching the prior design) and kept the mobile tap target at 44px with an invisible hit area. Updated Task 15.5 acceptance and added Task 15.8 to the checklist.
- Local Docker frontend and API rebuilt. Frontend suite: 67/67 tests pass; typecheck and production build pass. API health returned `ok`; `/api/v1/storefront/home` returned five campaigns with both mobile-image fields. Direct Pydantic validation confirmed aliased campaign fields and focal coordinate boundaries.
- Local browser rendered the API-backed homepage and campaign controls after loading; the desktop view shows 36px arrows and the full-width hero. A repeated local `pytest tests/test_storefront.py -vv -x` attempt stalled at the first existing media endpoint test in this environment, so the backend suite result recorded in the returned Task 15.3 contract (17/17) could not be independently reproduced in this session.

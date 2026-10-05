# Task 15.1 — Audit current hero behavior and API fields

**Owner:** Codex
**Status:** Completed
**Work item:** Work 015 / Mobile Hero Carousel Optimization

## Objective

Record how the current hero behaves at desktop, tablet, and mobile widths before implementation.

## Context and contract

The desktop hero is accepted. Mobile currently takes too much vertical space. Keep existing campaign content backend-driven and do not change code in this audit.

## Scope

- In scope: inspect component/styles/tests and storefront campaign schema/admin fields; measure hero height and note breakpoints, image sizing/cropping, copy, controls, and loading behavior.
- Out of scope: implementation, campaign removal, visual redesign, or changing backend records.

## Dependencies and relevant files

- Depends on: none.
- Inspect: `src/components/HeroCarousel.tsx`, its styles/tests, `src/pages/HomePage.tsx`, `src/lib/api/storefront.ts`, `backend/app/schemas/storefront.py`, and relevant campaign model/admin files.

## Acceptance checks

- [x] Document desktop/tablet/mobile heights and breakpoints with viewport sizes.
- [x] Record current campaign image fields and whether admin/API already support mobile assets or positioning.
- [x] Note existing image loading priorities, control behavior, and any text/CTA clipping or overlap.
- [x] Update Work 015 notes with findings and propose the smallest implementation sequence; no code changes.

## Audit findings (2026-10-04)

- Source-derived hero heights at the default 16px root size are 736px below 640px (`h-[46rem]`), 800px from 640px (`sm:h-[50rem]`), and 720px from 1024px (`lg:h-[720px]`). The image and content frame exclude the 112px top header offset. These are class-derived measurements; live computed dimensions were not available because the local API is stopped and the in-app browser has no open tab.
- The component uses one backend-provided `imageUrl` per campaign, `sizes="100vw"`, and an eager image for whichever slide is active. There is no `srcSet`, mobile image, or mobile focal-position field.
- `HomepageCampaign` in the SQLAlchemy model and public/admin Pydantic schemas has only `image_url` and `image_alt`. Admin create/update payloads likewise accept only those image fields. No mobile asset or crop field is present in the current persistence/API contract.
- Mobile/tablet/desktop use the same content structure. The component reserves fixed title/content heights; the hero remains 736px tall on common phone widths, and its 36px previous/next controls are below a 44px touch target. Slide rotation pauses on mouse/focus, but there is no touch swipe handling.
- The mobile image/schema gap is real if campaign owners need to configure a separate mobile crop/source per campaign. Task 15.3 needs backend/admin support for optional `mobileImageUrl` and an optional mobile focal/object position, with the existing desktop image as fallback. This is the only confirmed Gemini dependency; the remaining work is frontend-owned. Do not assign Gemini until the owner requests the handoff.
- Runtime API/browser inspection remains for Task 15.7 after the local Docker services are available. `http://localhost:8000/api/v1/storefront/home` was unreachable during this audit, and `docker-compose -f docker/compose.yaml ps` could not access the Docker daemon socket in this session. The in-app browser had no open tab.

## Handoff back

- Update this contract and `tasks.md` with findings and blockers; record only concise observations in `notes.md`.
- If the API/admin needs fields, identify the exact gap before assigning Task 15.3 to Gemini.

## Pickup checklist

- [x] Read the Work 015 context and this contract before auditing.
- [x] Keep the audit read-only for application code and data.

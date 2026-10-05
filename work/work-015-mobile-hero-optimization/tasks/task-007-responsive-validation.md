# Task 15.7 — Validate responsive behavior locally

**Owner:** Codex
**Status:** Completed
**Work item:** Work 015 / Mobile Hero Carousel Optimization

## Objective

Verify the final carousel at target mobile/tablet/desktop viewports in the local Docker environment and supported browsers.

## Context and contract

Local implementation and browser verification are required before any push or deployment. Preserve production-like API data and render the actual backend-driven campaign images.

## Scope

- In scope: local Docker build/restart as needed, browser QA, responsive tests, and regression checks.
- Out of scope: pushing to `dev`, deploying to PREPROD/VPS, or unrelated homepage changes.

## Dependencies and relevant files

- Depends on: Tasks 15.2–15.6.
- Inspect: `http://localhost:8080`, relevant API response at `http://localhost:8000`, hero component tests, and local Compose configuration.

## Acceptance checks

- [x] Validate widths 320, 360, 375, 390, 414, 768px and representative desktop widths in Chrome. (Hero sizing preserves the compact image frame and exposes the next section on mobile).
- [x] Inspect Chrome, Firefox, and mobile-sized viewports. Chrome screenshots were captured at 320, 360, 375, 390, 414, 768, 1024, and 1280px; Firefox WebDriver captured the API-backed page at 500px.
- [x] Confirm no full-screen takeover, clipping, CTA/control overlap, layout jump, or cut-off main subject.
- [x] Confirm swipe, touch controls, keyboard navigation, and image loading.
- [x] Run focused frontend tests (10/10), TypeScript, and production build; no push until owner review. The current backend campaign API returns HTTP 200 with five campaigns; responsive fields remain Gemini-owned task 15.3.

## Handoff back

- Update this contract, `tasks.md`, `notes.md`, and `coordination.md` with browser/viewport results and any blockers. Leave deployment for a separately authorized release step.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 015 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Change this task to In Progress before starting.

# Task 10.18 — Default occasion visibility and image repair

**Owner:** Codex
**Status:** In Progress (owner review pending)
**Work item:** Work 010 — Seasonal Gift by Occasion

## Objective

Show Birthday, Just Because, Anniversary, Baby Shower, and Wedding by default. Keep other occasions stored and admin-manageable but disabled by default. Use distinct, valid Sulocraft/R2 artwork and preserve product associations and admin controls.

## Current state

- Codex uploaded ten additional images to R2 and verified the public URLs return `200 image/png`. The exact occasion-to-key mapping and existing three occasion keys are preserved in the [historical handoff record](../../../docs/archive/handoffs-history.md).
- Gemini reports an idempotent migration, updated database/seed image keys, all 13 occasion mappings, five requested defaults enabled, eight others disabled, universal admin toggles, product associations preserved, and backend regression tests updated.
- No further image copy/upload is requested. Backend assets already exist; DB/seed references use the listed R2 keys.
- Local Docker/API/image/filter/tests and desktop/mobile browser verification are complete. Only owner review remains; do not push or deploy before approval.

## Subtasks

- [x] 10.18.1 — Audit existing occasion visibility and image URLs; identify broken, repeated, and generic fallback image references.
- [x] 10.18.2 — Set exactly the five requested initial defaults to enabled and retain all other occasion records disabled by default.
- [x] 10.18.3 — Keep every occasion admin-toggleable; preserve stable IDs and product associations.
- [x] 10.18.4a — Upload ten approved existing Sulocraft artworks to R2 and verify their public URLs.
- [x] 10.18.4b — Gemini: update database/seed/migration references to the verified R2 keys; no re-upload or duplicate local copy.
- [x] 10.18.5 — Add/revise backend and frontend regression coverage for defaults, toggles, ordering, image validity, and fallback behavior.
- [x] 10.18.6 — Rebuild local Docker API/database/frontend and verify actual API data, five default cards, distinct images, and desktop/mobile rendering.
- [x] 10.18.7 — Owner reviewed the verified local result and authorized pushing to `dev` on 2026-10-29.

## Acceptance

- Initial public grid contains the five requested defaults unless an admin explicitly enables another.
- Every stored occasion remains admin-manageable; products and IDs remain intact.
- Visible occasion artwork is valid and distinct, and the UI renders only backend-provided data.
- Relevant backend/frontend checks and integrated local Docker/browser review pass before release.

## Gemini return report

The detailed implementation report, migration identifier, and per-occasion verified R2 keys are in the [archived handoff history](../../../docs/archive/handoffs-history.md). Gemini reports the backend implementation and tests complete. Local API/database/browser behavior remains Codex acceptance work, not a completed claim.

## Handoff back

- Gemini updates this contract, Work 010 `tasks.md`, `notes.md`, and `coordination.md` before returning backend work.
- Codex records local Docker/API/browser results here and in Work 010 notes, then asks the owner to review. No push/deploy until owner approval.

## Resumed acceptance — 2026-10-25
Owner: Codex.10.18.6 In Progress. Found stale frontend admin lock based on isEvergreen, contrary to DEC-010-010. Scope includes removing this lock and updating frontend regressions: all records toggleable, missing legacy metadata cannot block controls, schedule fields available to all, server-rejected updates remain authoritative. Verify existing backend visibility/schedule/authorization tests, public local API five defaults/filter links/image delivery, rebuild affected frontend and inspect desktop/mobile if browser connected. Assets already uploaded; no backend handoff or reupload unless verification fails. Browser inventory currently empty; visual acceptance remains a known potential blocker.

## Acceptance return — 2026-10-25
- Removed stale admin always-on/unknown-evergreen locks: every occasion can be toggled/scheduled, using API isEnabled without frontend overrides. Year-round badge is descriptive only. Rejected saves preserve prior displayed server state and retain the error message.
- Regression established before fix: 3 admin tests failed against old component; final frontend suite 7/7 and TypeScript passed. Command: `docker-compose -f docker/compose.test.yaml run --rm frontend sh -c 'pnpm typecheck && pnpm exec vitest run --maxWorkers=1 src/admin/pages/OccasionsPage.test.tsx src/components/home/OccasionGrid.test.tsx'`.
- Backend: `./scripts/test.sh backend tests/test_occasions_admin.py -q` passed17 cases: defaults, all13 image keys/accessibility, multi-occasion catalogue identity, date boundaries, omission, admin toggles/order, idempotent seed/admin-edit preservation, and added 401/403 read/update denials with unchanged database visibility. PostgreSQL test database isolated; no shared DB mutation.
- Local API: exactly Birthday, Just Because, Anniversary, Baby Shower, Wedding in expected order. Five delivered PNGs HTTP200 with distinct SHA256 and actual relevant artwork visually inspected. Product counts9/4/5/4/4 respectively. Exact URLs/hashes/results in [report](../reports/task-018-local-acceptance.json). Existing assets and DB mappings reused; no R2 uploads or migrations repeated.
- Security disposition: applicable backend admin-authorization negative tests pass, rejected client save does not claim success, no auth/session/credential/URL-policy changes. Review is Codex self-review. Existing TestClient/cookie deprecation warnings recorded, not suppressed.
- Browser check was initially unavailable through the connected-browser tool. Superseded by headed Playwright CLI verification below.

## Browser acceptance — 2026-10-25
- Opened `http://localhost:8080/` in headed Playwright; inspected the real rendered page at 1440×900 and 390×844. Gift by Occasion shows Birthday, Just Because, Anniversary, Baby Shower, Wedding with five distinct, relevant images. Mobile layout wraps to two columns; all five cards remain in the grid and the last card continues below the viewport as expected.
- Evidence: [desktop screenshot](../reports/task-018-desktop.png), [mobile screenshot](../reports/task-018-mobile.png).
- Desktop and mobile screenshots were visually inspected. Browser console reported favicon 404 and unauthenticated `/api/v1/auth/me` and `/api/v1/wishlist` 401 responses while logged out; no broken occasion image or occasion-section runtime error observed.
- 10.18.6 is complete. Owner approved the push to `dev` on 2026-10-29. No Gemini support needed. No deployment performed.

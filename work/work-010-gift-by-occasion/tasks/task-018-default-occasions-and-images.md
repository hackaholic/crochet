# Task 10.18 — Default occasion visibility and image repair

**Status:** Gemini implementation returned; Codex local integration verification in progress.
**Work item:** Work 010 — Seasonal Gift by Occasion

## Objective

Show Birthday, Just Because, Anniversary, Baby Shower, and Wedding by default. Keep other occasions stored and admin-manageable but disabled by default. Use distinct, valid Sulocraft/R2 artwork and preserve product associations and admin controls.

## Current state

- Codex uploaded ten additional images to R2 and verified the public URLs return `200 image/png`. The exact occasion-to-key mapping and existing three occasion keys are preserved in the [historical handoff record](../../../docs/archive/handoffs-history.md).
- Gemini reports an idempotent migration, updated database/seed image keys, all 13 occasion mappings, five requested defaults enabled, eight others disabled, universal admin toggles, product associations preserved, and backend regression tests updated.
- No further image copy/upload is requested. Backend assets already exist; DB/seed references use the listed R2 keys.
- Integrated Docker/browser verification has not yet been completed for this returned change. Do not push or deploy before that check and owner review.

## Subtasks

- [x] 10.18.1 — Audit existing occasion visibility and image URLs; identify broken, repeated, and generic fallback image references.
- [x] 10.18.2 — Set exactly the five requested initial defaults to enabled and retain all other occasion records disabled by default.
- [x] 10.18.3 — Keep every occasion admin-toggleable; preserve stable IDs and product associations.
- [x] 10.18.4a — Upload ten approved existing Sulocraft artworks to R2 and verify their public URLs.
- [x] 10.18.4b — Gemini: update database/seed/migration references to the verified R2 keys; no re-upload or duplicate local copy.
- [x] 10.18.5 — Add/revise backend and frontend regression coverage for defaults, toggles, ordering, image validity, and fallback behavior.
- [ ] 10.18.6 — Rebuild local Docker API/database/frontend and verify actual API data, five default cards, distinct images, and desktop/mobile rendering.
- [ ] 10.18.7 — Present the verified local result for owner review; release only after approval.

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

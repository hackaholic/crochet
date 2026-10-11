# Task 1.7.6 — Catalogue final local acceptance

**Task ID:** 1.7.6
**Owner:** Codex
**Status:** Blocked
**Work item:** Work 001

## Objective and scope
Complete real local product create/upload/tag roundtrip and browser acceptance; preserve supplied admin design.
No redesign, unrelated data changes or deployment.

## Dependencies/relevant files
Read Work001 README/tasks/decisions/coordination. Catalogue blueprint and original evidence: task-005-catalogue.md. Tag API historical return: task-006-tags-api.md. Existing admin API remains source of truth.

## Acceptance/tests and evidence
Tag discovery and duplicate reuse verified; real create/upload and Firefox acceptance remain pending.
Pending acceptance: verify persisted create/upload/tag roundtrip; loading/error/validation states; local desktop/mobile and Firefox where available. Run relevant ProductEditor/ProductsPage tests and typecheck. Dependencies1.7.5 and1.7.9 returned; no backend blocker.

## Security validation
Retain administrator authorization, credentialed API transport, validated inputs and React text escaping. No provider secrets or PII in this record. Existing scoped evidence preserved; final end-to-end security acceptance remains the explicit acceptance task where applicable. No runtime change in this normalization.

## Handoff back
Update this exact contract and work-local records on meaningful changes. No repeated setup or asset work. Historical details remain in original parent/archive; this is the authoritative subtask status.

## Current acceptance plan
- Reuse returned tag APIs and existing editor/defaults; no repeated setup.
- Add photo upload failure/retry and primary/gallery regression cases; run catalogue/editor tests and typecheck once.
- Rebuild affected frontend; exercise actual local create/upload/tag save and reopen on desktop/mobile. Remove temporary listing after checking.
- Check unauthenticated mutation denial without persisting data; record browser availability accurately.

## Return evidence — 2026-10-11
- Added two ProductPhotos regression cases: failed upload/retry/deduplication and primary promotion/removal. Repaired ProductsPage defaults mocks revealed by Work019 integration. Docker Node:16/16 focused tests and typecheck pass. Host native binding unavailable; Docker checks authoritative.
- Rebuilt/restarted frontend. Actual browser upload returned `products/0a78532f6c4f.png`; image loaded from local API. Existing handmade tag reused once; save/reopen retained Flowers category, tag, price250 and stock3.390px viewport/document width390, no overflow. Temporary QA listing archived after verification.
- Unauthenticated local POST products returned401. Existing transport403 regression passed. Self-review: test-only frontend diff, no runtime design/API change.
- Real create initially failed: products sequence behind explicit seeded IDs. Non-rewinding local sequence repair allowed unchanged submission to succeed. Durable fix assigned to Gemini1.7.11; final acceptance remains Blocked until rebuilt local seed/create rerun.
- Depends on: 1.7.11
- Blocked by: 1.7.11
- Browser limitation: Chromium/mobile viewport available; Firefox unavailable, remains broader1.6 verification requirement.
- No push/deployment.

1.6 correction: uploaded URL redirects to unrelated Unsplash image. Earlier loaded-image evidence is invalid as proof of actual uploaded content. Gemini1.7.11 returned; final acceptance now blocked by1.7.12.
- Depends on: 1.7.12
- Blocked by: 1.7.12

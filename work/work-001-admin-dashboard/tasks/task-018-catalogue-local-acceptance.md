# Task 1.7.6 — Catalogue final local acceptance

**Task ID:** 1.7.6
**Owner:** Codex
**Status:** Pending
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

# Task 1.14.4 — Top-selling products and variants

**Owner:** Gemini
**Status:** Pending
**Work item:** Work 001 / 1.14 Finance analytics

## Objective and context
Correct existing ranking semantics for selected date and eligible orders; rank by units or product revenue with stable tie-breaks, configurable bounded limit/pagination. Return product identifier, sale-time name, SKU/variant where supported, backend image_url, units, distinct orders, product revenue; separate cancelled/refunded treatment per1.14.1. Define unknown/deleted products honestly; products renamed across orders must not split just by name. No duplication of catalogue truth or constructed image storage paths in UI.

## Scope
In scope: selected-period Sulocraft commerce analytics using existing database/API and supplied admin design. Out of scope: architecture redesign, fabricated sales, visitor analytics, inferred profit, production deployment and unrelated work.

## Dependencies and relevant files
Depends on: Returned1.14.1.
Inspect/edit: Existing get_admin_analytics; analytics service; order item snapshots; product/media resolver; docs/api-admin.md

## Test cases (define before implementation)
Backend: unpaid/cancelled exclusion, partial returns, date filtering, stable ties, renamed/deleted products, multiple variants, pagination and image URL handling. Frontend: ranking metric toggle, thumbnails/fallback and page transport fixtures in1.14.6. Security: admin only, valid metric/limit, no hidden secrets/PII in payload.

Assign concrete testcase IDs and files before implementation. Every subtask requires frontend contract/render/transport coverage AND backend behavior/regression/security evidence. For API work, return typed fixtures and record dependent UI tests as pending1.14.6; no claim that backend mocks prove UI acceptance. For UI work, link/rerun returned server tests. Document any unrun integration case explicitly.

## Security validation
Pending. Admin session/authorization, input/date/sort/limit validation, parameterized bounded queries, currency integrity, privacy and no secret output. Pair each applicable control with negative tests and confirm denial causes no writes. Read-only analytics must not change commerce records.

## Acceptance checks
- [ ] Metric/payload definitions documented, dependencies ready.
- [ ] Relevant frontend/backend cases implemented with results or explicit dependent UI acceptance.
- [ ] Accounting/boundary/security tests pass; no invented data or unsupported financial claims.
- [ ] Review accurately labeled; performance concerns and blockers recorded.

## Handoff back
Return exact payload examples without customer PII, definitions/filter semantics, changed files, test commands/counts and Codex integration needs. Update this contract, tasks.md, notes.md and coordination.md. No push/deploy without user authorization; completed contracts preserved.

## Pickup checklist
- [ ] Read work/INDEX.md and Work001 README/tasks/decisions/coordination and this contract.
- [ ] Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md.
- [ ] Confirm ownership; mark only selected task In Progress.

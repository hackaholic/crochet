# Task 1.14.6 — Finance analytics panels

**Owner:** Codex
**Status:** Pending
**Work item:** Work 001 / 1.14 Finance analytics

## Objective and context
Extend supplied Finance design with category and destination breakdowns, top product rankings/thumbnails, trends and concise KPI cards. Preserve current summary; one shared selected period filters all widgets. Reusable tables/charts; units vs revenue ranking; clearly labeled metrics, share denominators and unknown data. Add keyboard access, loading/error/retry/empty states and mobile tables. Only API data; no fake chart numbers/images. Export CSV is deferred until separately scoped; do not imply exports or real-time data we do not supply.

## Scope
In scope: selected-period Sulocraft commerce analytics using existing database/API and supplied admin design. Out of scope: architecture redesign, fabricated sales, visitor analytics, inferred profit, production deployment and unrelated work.

## Dependencies and relevant files
Depends on: Returned1.14.1–1.14.5 contracts and local API deployment.
Inspect/edit: src/admin/pages/FinancePage.tsx; src/admin/components/; types/services/API clients; component tests

## Test cases (define before implementation)
Frontend: date changes all requests and cancels stale result, category/country/state/product render, sorting/pagination, amounts formatted from correct units, unknown/refund/no-baseline states, retry/partial failure and mobile overflow. Backend: rerun/link returned API authorization/accounting regressions against final payload. No UI auth assumed to replace backend controls.

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

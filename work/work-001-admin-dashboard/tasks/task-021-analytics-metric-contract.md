# Task 1.14.1 — Define finance analytics contract

**Owner:** Gemini
**Status:** Pending
**Work item:** Work 001 / 1.14 Finance analytics

## Objective and context
Specify one date/timezone, payment eligibility and currency policy shared by summary, trends and breakdowns. Document gross product sales vs order receipts vs net revenue, refunds and discounts without double subtraction. Current topSellingProducts aggregates all OrderItems without date/payment filtering: fix the contract before exposing it. Finance chart currently maps every non-7d range to30d; require exact selected range across all widgets. Define counts, units, average order value, previous-period comparison and complete/missing-data indicators. No profit/conversion claims without costs/visitor data.

## Scope
In scope: selected-period Sulocraft commerce analytics using existing database/API and supplied admin design. Out of scope: architecture redesign, fabricated sales, visitor analytics, inferred profit, production deployment and unrelated work.

## Dependencies and relevant files
Depends on: Existing Finance/dashboard semantics; no dependency on other new tasks.
Inspect/edit: Existing finance summary/sales APIs; docs/api-admin.md; backend admin schemas/services; src/admin/types.ts

## Test cases (define before implementation)
Backend: deterministic paid/unpaid/cancelled/refunded/partial-refund fixtures, date-boundary IST inclusion, same period totals reconcile, integer-paise precision and zero-order averages. Frontend: typed response/transport fixtures and range query mapping; non7d range never silently becomes30d. Security: admin only, bounded date range/limit, no customer PII in aggregates.

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

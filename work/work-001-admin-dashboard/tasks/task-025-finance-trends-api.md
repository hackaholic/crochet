# Task 1.14.5 — Finance trends and operational indicators

**Owner:** Gemini
**Status:** Pending
**Work item:** Work 001 / 1.14 Finance analytics

## Objective and context
Use the metric contract to provide orders, average order value, sales/revenue and refund trends plus previous equal-length period comparisons. Useful operational indicators: pending payment totals, cancellation/refund counts and fulfillment-state counts explicitly labeled separately from earned revenue. Decide which existing summary/series endpoints can be extended rather than duplicate them. Zero/missing prior baseline has null percentage, not infinity or fake growth. No margin/COGS, carrier performance or gateway fee estimate without recorded inputs.

## Scope
In scope: selected-period Sulocraft commerce analytics using existing database/API and supplied admin design. Out of scope: architecture redesign, fabricated sales, visitor analytics, inferred profit, production deployment and unrelated work.

## Dependencies and relevant files
Depends on: Returned1.14.1.
Inspect/edit: Existing finance summary and sales endpoints; focused analytics service; payment/return history; docs/api-admin.md

## Test cases (define before implementation)
Backend: empty periods, null baseline, IST day/month buckets, partial/completed refund handling, no duplicate payment counts, matching comparison window and reconciliation. Frontend: correct date range, percentages/null baseline, loading/errors in1.14.6. Security: admin authorization, bounded period/range, aggregate-only outputs.

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

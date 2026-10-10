# Task 1.14.7 — Local analytics reconciliation and acceptance

**Owner:** Codex
**Status:** Pending
**Work item:** Work 001 / 1.14 Finance analytics

## Objective and context
Build affected Docker services; create explicitly disposable local orders/categories/destinations/refunds to verify meaningful charts and rankings, then reconcile breakdowns with documented totals. Inspect localhost admin Finance desktop/mobile and record browser availability. Review with user before any dev push. Do not mutate real orders or produce real charges/emails/shipping. Existing fixture/history kept, no secrets in notes.

## Scope
In scope: selected-period Sulocraft commerce analytics using existing database/API and supplied admin design. Out of scope: architecture redesign, fabricated sales, visitor analytics, inferred profit, production deployment and unrelated work.

## Dependencies and relevant files
Depends on: 1.14.6 complete; backend test evidence returned.
Inspect/edit: docker/compose.yaml; frontend/backend analytics tests; Work001 notes/coordination

## Test cases (define before implementation)
Frontend: real API rendering, date/metric changes, thumbnails, empty/error states, desktop/mobile keyboard checks. Backend: deterministic PostgreSQL reconciliation with categories/countries/top products, owner/admin auth and bounded query checks; relevant query performance/explain evidence on representative fixtures. Currency/timezone criteria pass. Record exact test counts and cleanup, separate mock from real checks.

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

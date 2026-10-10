# Task 1.14.2 — Sales by category

**Owner:** Gemini
**Status:** Pending
**Work item:** Work 001 / 1.14 Finance analytics

## Objective and context
Return category ID/name, qualifying order count, units, gross product sales, share and optional separately-defined refunds/net where attribution is reliable. Group each line into exactly one accounting category so multi-category products are not counted twice; use explicit primary/sale-time category policy, unclassified bucket for missing/deleted data. Historical category drift must be disclosed or snapshot-supported, not silently reinterpreted. Include sort, pagination/limit and totals metadata.

## Scope
In scope: selected-period Sulocraft commerce analytics using existing database/API and supplied admin design. Out of scope: architecture redesign, fabricated sales, visitor analytics, inferred profit, production deployment and unrelated work.

## Dependencies and relevant files
Depends on: Returned1.14.1 definitions.
Inspect/edit: Focused backend analytics service/repository; admin routes/schemas; category/order models; docs/api-admin.md

## Test cases (define before implementation)
Backend: multi-category item counted once, duplicate lines/order count distinct, missing category, renamed/deleted product, refunds attribution unavailable vszero, sum breakdown reconciles. Frontend: category response/render fixtures and empty/error tests required in1.14.6. Security: nonadmin rejected, sort whitelist/bounded limits, aggregation excludes PII.

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

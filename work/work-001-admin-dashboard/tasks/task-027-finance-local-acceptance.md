# Task 1.14.7 — Local analytics reconciliation and acceptance

**Owner:** Codex
**Status:** Completed
**Work item:** Work 001 / 1.14 Finance analytics

## Objective and context
Build affected Docker services; create explicitly disposable local orders/categories/destinations/refunds to verify meaningful charts and rankings, then reconcile breakdowns with documented totals. Inspect localhost admin Finance desktop/mobile and record browser availability. Review with user before any dev push. Do not mutate real orders or produce real charges/emails/shipping. Existing fixture/history kept, no secrets in notes.

## Scope
In scope: selected-period Sulocraft commerce analytics using existing database/API and supplied admin design. Out of scope: architecture redesign, fabricated sales, visitor analytics, inferred profit, production deployment and unrelated work.

## Dependencies and relevant files
Depends on: 1.14.6
Dependency context: 1.14.6 complete; backend test evidence returned.
Inspect/edit: docker/compose.yaml; frontend/backend analytics tests; Work001 notes/coordination

## Test cases (define before implementation)
Frontend: real API rendering, date/metric changes, thumbnails, empty/error states, desktop/mobile keyboard checks. Backend: deterministic PostgreSQL reconciliation with categories/countries/top products, owner/admin auth and bounded query checks; relevant query performance/explain evidence on representative fixtures. Currency/timezone criteria pass. Record exact test counts and cleanup, separate mock from real checks.

Assign concrete testcase IDs and files before implementation. Every subtask requires frontend contract/render/transport coverage AND backend behavior/regression/security evidence. For API work, return typed fixtures and record dependent UI tests as pending1.14.6; no claim that backend mocks prove UI acceptance. For UI work, link/rerun returned server tests. Document any unrun integration case explicitly.

## Security validation
Pass for scoped acceptance (see final return). Admin session/authorization, input/date/sort/limit validation, parameterized bounded queries, currency integrity, privacy and no secret output. Pair each applicable control with negative tests and confirm denial causes no writes. Read-only analytics must not change commerce records.

## Acceptance checks
- [x] Metric/payload definitions documented, dependencies ready.
- [x] Relevant frontend/backend cases implemented with results or explicit dependent UI acceptance.
- [x] Accounting/boundary/security tests pass; no invented data or unsupported financial claims.
- [x] Review accurately labeled; performance concerns and blockers recorded.

## Handoff back
Return exact payload examples without customer PII, definitions/filter semantics, changed files, test commands/counts and Codex integration needs. Update this contract, tasks.md, notes.md and coordination.md. No push/deploy without user authorization; completed contracts preserved.

## Pickup checklist
- [ ] Read work/INDEX.md and Work001 README/tasks/decisions/coordination and this contract.
- [ ] Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md.
- [ ] Confirm ownership; mark only selected task In Progress.

## Acceptance cases — 2026-10-11
- TC-FIN-27-01: isolated PostgreSQL paid/unpaid/cancelled/COD recognition across all four analytics endpoints.
- TC-FIN-27-02: discounted order category/destination/trend gross totals reconcile with persisted order-line gross; real checkout stores subtotal before discount.
- Existing frontend rendering/transport/security cases from1.14.6 remain valid; do not repeat unchanged tests. Accounting failures block final acceptance and receive a Gemini contract.

## Verification return — 2026-10-11
PostgreSQL disposable runner: 7 cases executed, 1 passed, 6 failed. TC-FIN-27-01 fails on all four endpoints; TC-FIN-27-02 passes categories, fails destinations/trends. No application database was changed. Checkout subtotal is pre-discount, verified from order creation source. Backend remediation is [1.14.8](task-040-finance-accounting-reconciliation.md). Final refund/timezone/performance/browser acceptance remains pending after return; prior1.14.6 UI evidence remains preserved. Self-review: fixtures use correct subtotal/total values and a separate2050 date window; failures reflect server accounting, not transport errors. Security disposition: financial integrity fails acceptance; previous authorization checks are not invalidated.

Blocked by: None
Blocker reason: None; Gemini1.14.8 returned19/19 PostgreSQL tests passing.
Next action: User local review; no push/deploy without authorization.

## Final return — 2026-10-11
Completed after Gemini1.14.8 return. API rebuilt from current source and restarted locally (Compose dependency lookup failed after recreation; started the rebuilt docker-api-1 container successfully). Existing frontend already rebuilt/verified; no repeated unchanged frontend suite.

- `backend/scripts/run_isolated_tests.sh backend/tests/test_admin_dashboard.py -q -s`:21 cases passed, exit0; disposable PostgreSQL container torn down. Includes original19 and new TC-FIN-27-05 IST start/end boundaries/equal previous single-day range, TC-FIN-27-06 batched read-only queries across20 synthetic orders.
- Query smoke evidence: categories2 statements/0.013s, destinations2/0.012s, top-products2/0.012s. No INSERT/UPDATE/DELETE from these reads. Small fixture evidence, not a production-scale load benchmark or EXPLAIN study; large-volume ORM aggregation remains a scaling consideration, no unsupported capacity claim.
- Prior19 finance frontend rendering/transport/date checks from1.14.6 retained; current local browser uses rebuilt real PostgreSQL API. Gross6098, refunds2599, net3499;4 recognized orders. Category5198+900 and destination5648+450 both reconcile6098. One real product thumbnail loads; intentionally photo-less QA products show honest fallback.
- Local Chromium desktop/mobile390x844: ranking changed to Units sold, native India-region disclosure expanded by Enter; Previous Month shows September1–30 IST,0 sales/orders and honest no-baseline/no-sales messages. Populated and empty mobile document width390 equals viewport390. Viewport reset, reporting period restored. Screenshot /tmp/sulocraft-finance-accepted.png.
- Security: existing admin/customer/anonymous denial and invalid date/sort/limit cases included in passing backend suite; finance reads unchanged commerce rows. Test fixtures only in disposable database; no real order/payment/email/shipping side effects. Local login uses existing mock-email flow.
- Self-review: money follows pre-discount stored subtotal and subtracts refunds once; unpaid operational counts separate. No business content invented. Firefox unavailable; browser coverage honestly limited to Chromium plus mobile viewport, with broader cross-browser acceptance tracked separately under1.6. No push/deployment.

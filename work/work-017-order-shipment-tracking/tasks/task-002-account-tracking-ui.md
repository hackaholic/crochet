# Task 17.2 — Signed-in customer tracking view

**Owner:** Codex
**Status:** Completed
**Work item:** Work 017

## Objective/context and scope
Add tracking action to each account order and reusable API-backed details/timeline. Loading/empty/retry/unauthorized states, accessible navigation; no invented courier links or delivery dates.
Out of scope: application redesign, unrelated changes, live shipment purchases, deployment.

## Dependencies and relevant files
Requires returned17.1; src/pages/AccountPage.tsx, src/lib/api/orders.ts, reusable tracking components and tests.

## Test cases (before implementation)
| ID | Category | Input/action | Expected | Evidence |
| --- | --- | --- | --- | --- |
| 002-TC01 | Success | Select order from account history | Fetch exact order; render shared view | Passed scoped tests/local browser |
| 002-TC02 | Failure | Timeout/403/404 then retry | Clear old details; generic error/retry | Passed scoped tests/local browser |
| 002-TC03 | Regression | Switch order while old request pending | Old result never replaces current order | Passed scoped tests/local browser |
| 002-TC04 | Boundary | No shipment or no orders | Honest empty state | Passed scoped tests/local browser |
| 002-TC05 | Security | HTML-like API text | Escaped rendering; no invented URLs | Passed scoped tests/local browser |
| 002-TC06 | Acceptance | Keyboard and390px local browser | Usable focus/back controls; no document overflow | Passed scoped tests/local browser |

## Security validation
Order access and shipment/customer data are sensitive. Enforce exact ownership or verified scoped guest credentials, validation/limits, safe errors and parameterized queries. No secrets/private contacts in handoff. Disposition: Pending audit/testing.

## Acceptance checks
- [ ] Scoped objective completed with relevant tests/evidence.
- [ ] Security disposition and self/independent review recorded accurately.
- [ ] Local verification recorded where runtime changes are made.

## Handoff back / pickup
Read work/GEMINI_WORKFLOW_PROMPT.md if Gemini, then selected work docs and this contract. Mark only assigned task In Progress. Return exact files/contracts, executed tests, remaining risks and blockers in this task and work-local tasks/notes/coordination. Report contract changes before expanding scope. No credentials or duplicate global contract.

## Return — 2026-10-10
Added account order Track shipment action, shared abortable OrderTrackingPanel and credentialed no-store tracking API service. Guest tokens (future17.3) use header transport rather than query URLs.13 scoped tests passed (6 presentation,3 loader,2 account,2 API transport); TypeScript passed. Frontend Docker rebuilt/restarted. Real browser account order fixture QA-W017-ACCOUNT rendered courier, number, null ETA and timeline from running API; close action worked.390px mobile document did not overflow. Disposable local order created without stock/payment changes and removed after acceptance. Firefox unavailable, remains broader acceptance.

Security/self-review: no guest/account identifier bypass added; server controls ownership. No response-body leakage in denied errors, no tokens persisted/logged, no constructed carrier URLs. Late requests aborted/ignored. Self-review Pass for frontend scope; Gemini17.1 tests provide backend access-control evidence. No push/deploy. Next:17.3 guest page and17.5 end-to-end acceptance.

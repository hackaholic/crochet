# Task 17.3 — Secure guest shipment view

**Owner:** Codex
**Status:** Completed
**Work item:** Work 017

## Objective/context and scope
Integrate17.1 guest link/access flow and discoverable tracking entry. No login requirement for verified guest purchaser; no unsecured order lookup. Keep credential out of persistent analytics/logs; follow returned token transport contract.
Out of scope: application redesign, unrelated changes, live shipment purchases, deployment.

## Dependencies and relevant files
Requires returned17.1 and shared17.2 view; App routing, guest tracking page, checkout confirmation/email link contract.

## Test cases (before implementation)
| ID | Category | Input/action | Expected | Evidence |
| --- | --- | --- | --- | --- |
| 003-TC01 | Success | Valid verified guest link | Only scoped order renders without account login | Passed tests/local checks |
| 003-TC02 | Security | Missing/expired/tampered/wrong-order token | No order fields; recovery flow | Passed tests/local checks |
| 003-TC03 | Failure | Link-request rate limit/network error | Safe retry without enumerating orders | Passed tests/local checks |
| 003-TC04 | Security | Inspect navigation/log/storage | No token analytics/log/persistent-storage leakage | Passed tests/local checks |
| 003-TC05 | Acceptance | Refresh/back and mobile keyboard flow | Secure access retained per contract; accessible view | Passed tests/local checks |

## Security validation
Order access and shipment/customer data are sensitive. Enforce exact ownership or verified scoped guest credentials, validation/limits, safe errors and parameterized queries. No secrets/private contacts in handoff. Disposition: Pending audit/testing.

## Acceptance checks
- [ ] Scoped objective completed with relevant tests/evidence.
- [ ] Security disposition and self/independent review recorded accurately.
- [ ] Local verification recorded where runtime changes are made.

## Handoff back / pickup
Read work/GEMINI_WORKFLOW_PROMPT.md if Gemini, then selected work docs and this contract. Mark only assigned task In Progress. Return exact files/contracts, executed tests, remaining risks and blockers in this task and work-local tasks/notes/coordination. Report contract changes before expanding scope. No credentials or duplicate global contract.

## Return — 2026-10-10
GuestTrackingPage at /track and /track/{orderNumber}: shared shipment view with secure fragment/header access, no-login recovery form, safe generic messages/retry and busy guard. Footer entry and checkout confirmation token link added; route is noindex/nofollow. Legacy query links are replaced with fragment, refresh retains access; Skip to content preserves token fragment and focuses main. No browser local/session-storage writes or raw credential logging.

Tests: TypeScript and27 scoped tests pass (guest6, presentation6, loader3, transport3, account2, routes4, SEO3). Initial test-run failures were an incorrect Testing Library query name and helper output status role; corrected, final suite passes. Docker frontend rebuilt/restarted. Live local guest fixture rendered persisted carrier/number/timeline, null ETA, reload and mobile390px no overflow, invalid token hides fields, no-token recovery form, generic recovery response. Cookie-free local API200 with valid scoped header and404 without token. Test fixture/tokens removed without original order/stock/payment changes. Firefox unavailable.

Security/self-review: Pass for frontend scope; React escaped text, no provider URL inference, encoded identifiers, no-store API transport, no token in API query. Gemini17.7 required before release: backend email query links and development response exposure need remediation/validation. This does not mark full Work017 security accepted. Actual full checkout-to-email-to-delivery acceptance remains17.5, including real checkout link rendering; route helper link safety tested here. No push/deployment.

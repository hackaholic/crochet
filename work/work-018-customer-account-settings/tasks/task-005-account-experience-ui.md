# Task 18.5 — Account navigation and editors

**Owner:** Codex
**Status:** Completed
**Work item:** Work 018

## Objective and context
Implement Profile, Addresses and Orders navigation styled from references using Sulocraft tokens; reusable components. Edit phone/name with shared client policy matching backend, readable field errors, disabled duplicate submit, cancel/reset and saved state. Email read-only with explanation. Add address edit/delete confirmation/default controls. Order number/details action opens order items and shared tracking/progress; preserve Work017 guest tracking. Add retry/empty/loading/focus states, accessible labels and sensible mobile layout; wishlist/sign-out remain reachable.

## Scope
In scope: existing account/order feature enhancement and its frontend/backend contract tests. Out of scope: architecture redesign, carrier integration, production deployment, password/OTP authentication, deleting completed work.

## Dependencies and relevant files
Depends on: 18.2, 18.3, 18.4
Dependency context: Returned18.2/18.3/18.4; reuse Work017 components.
Inspect/edit: src/pages/AccountPage.tsx; src/components/account/; src/lib/api/account.ts and orders.ts; shared validation; account and tracking component tests

## Test cases (define before implementation)
Frontend success/roundtrip: valid edits submit exact API payload and UI reloads saved data. Boundary/failure: invalid input blocks submission, backend field errors retained, failed save keeps draft, cancel restores values, double submits prevented. Order selection/progress loading, missing data, terminal statuses and stale-request race covered. Security: no unverified email edits, API data escaped, logout clears private view, address ID scoped by API. Backend regressions rerun for transport contracts; do not claim mocked UI tests verify server authorization.

Add concrete test IDs and test files/results before implementation. Every task requires frontend coverage of the user/transport behavior plus backend acceptance/regression/security coverage; a backend-only task records frontend contract fixtures for Codex and cannot claim UI integration complete until18.5/18.6. A frontend-only task reruns relevant API tests or links returned backend evidence. No blanket “not applicable” for either layer.

## Security validation
Pending: session/CSRF policy, object and field authorization, safe errors/PII, validation, race conditions and no mutation on denied requests. Map negative test IDs to each applicable control. Never log raw auth links, phone/email values or secrets in handoff evidence.

## Acceptance checks
- [ ] Contract and validation policy documented; dependency readiness recorded.
- [ ] Relevant frontend and backend tests identified, executed or explicitly pending dependent UI acceptance.
- [ ] Required behavior, failure and security checks pass with evidence.
- [ ] Self/independent review labeled; no unresolved release blocker concealed.

## Handoff back
Update this exact contract, tasks.md, notes.md and coordination.md. Return changed files, schema/error examples without personal data, test commands/counts, blockers and exact Codex integration needs. No push or deployment. Preserve completed task history.

## Pickup checklist
- [ ] Read work/INDEX.md and Work018 README/tasks/decisions/coordination.
- [ ] Gemini reads work/GEMINI_WORKFLOW_PROMPT.md before pickup.
- [ ] Confirm ownership and mark only this task In Progress.

## Pickup 2026-10-11
Backend18.2–18.4 returned. Implement profile form, address manager and API milestones as focused components. Test valid/invalid/cancel/failure flows, mutation reload/default state, and terminal/pending milestone semantics before local Docker/browser acceptance.

## Codex progress 2026-10-11
Implemented reusable ProfileEditor, AddressManager, OrderItems and shared input validation. Account navigation renders each panel; phone/name save, address edit/default/delete confirmation, order item loading and API milestone/terminal-state rendering are integrated. Email remains read-only. Failed mutation drafts retained; address mutations reload server defaults; order item requests ignore stale results.

Verification: 29 tests passed across account editors/navigation, order items, shared tracking and API transport; TypeScript passed. Frontend and API Docker images rebuilt, services restarted, API /health returned 200. Actual localhost account browser verified invalid phone and empty-address field errors, cancel/reset, Profile/Addresses switching. At 390x844, document width380 <= viewport390: no horizontal overflow. Screenshot /tmp/sulocraft-work018-addresses.png. Existing account has zero orders, so live order/milestone acceptance remains pending. Gemini backend evidence is recorded above; Codex did not rerun those backend suites in this pass. No push/deployment.

Remaining18.5: map server validation field errors, explicit retry controls, order-number details action, and persisted profile/address success roundtrip.18.6: fixture order lifecycle/ownership/security acceptance and browser coverage including Firefox when available. No automatic courier update integration claimed.

## Remaining acceptance plan
18.5-TC08: allowlisted server validation fields render safe messages, unknown fields and raw inputs never reflected.
18.5-TC09: failed account/item loads retry successfully; stale requests ignored.
18.5-TC10: order-number button opens shared details.
18.5-TC11: local browser profile/address save survives reload; defaults reconcile.
Security checks: retain credentialed API authorization; no raw provider error reflection; no email mutation; invalid client values send no mutation.

## Codex acceptance 2026-10-11
18.5-TC08–TC11 implemented: safe allowlisted 422 field mapping (no raw messages/inputs reflected), profile/address retained drafts, explicit account/items/address retry controls, order-number details action, matching accessible navigation panel IDs. 35 frontend/transport tests and typecheck passed; 44 backend tests passed in disposable container with DATABASE_URL=sqlite:////tmp/test_work018.db (account, orders, security authorization/business logic, tracking security). Deprecation warnings only.
Frontend rebuilt/restarted; backend image from prior pass remains current. Self-review: credentialed API transport preserved, email immutable, validation errors sanitized, stale effects cancelled. Live local API verified phone persistence; invalid phone/PIN cause zero mutation; cross-user address/order tracking and anonymous access denied; historical shipping snapshot unchanged. Browser verified profile save/reload; address create/edit/reload; shipped and cancelled item/progress rendering; mobile390 no overflow (content380). Latest demo browser session revoked on logout and private account view removed.

Fixtures: reserved local customer.demo@example.com; QA-W018-SHIPPED and QA-W018-CANCELLED; one address named QA Work018; separate reserved QA customer for ownership checks (temporary session revoked). No payment/shipping/email to real recipients. Fixtures retained locally for user review; no automatic seed or deployment integration. Do not purge any unrelated records. Screenshot /tmp/sulocraft-work018-progress.png.

18.5 Completed.18.6 account checks performed; full acceptance Blocked by unavailable Firefox browser surface and Work01717.5 checkout→guest emailed tracking-link acceptance still Pending. Chromium-family IAB desktop/mobile checked; do not claim Firefox/real mobile device passed. No courier automation claimed. No push/deployment.

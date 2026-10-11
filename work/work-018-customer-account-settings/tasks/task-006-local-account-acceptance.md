# Task 18.6 — Integrated local acceptance

**Owner:** Codex
**Status:** Blocked
**Work item:** Work 018

## Objective and context
Rebuild affected Docker services, use local Demo Customer and another isolated customer to exercise profile/address/order flow against actual API. Add documented disposable lifecycle order fixtures rather than charging or shipping anything. Browser inspect desktop/mobile, Chrome/Firefox availability, invalid forms and reload persistence. Verify independent ownership and session logout. Retain completed contracts and record fixture cleanup with user authorization for disposable data.

## Scope
In scope: existing account/order feature enhancement and its frontend/backend contract tests. Out of scope: architecture redesign, carrier integration, production deployment, password/OTP authentication, deleting completed work.

## Dependencies and relevant files
Depends on: 18.5, 17.5
Dependency context: 18.5 and Work01717.5 acceptance; real backend contracts returned.
Inspect/edit: docker/compose.yaml; UI/API tests; work018 notes; work017 acceptance evidence

## Test cases (define before implementation)
Frontend E2E: profile phone persists, address operations and order detail milestones render on actual local app; mobile/keyboard no overflow. Backend integration: unauthorized/cross-user edits and tracking rejected with zero mutations, invalid values rejected even bypassing frontend, order snapshot unchanged. Lifecycle stages and cancellation checked. Production parity config only; no public dummy seeds or token logs. Record test counts, browser evidence and blockers. User reviews localhost before push.

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

## Codex acceptance 2026-10-11
18.5-TC08–TC11 implemented: safe allowlisted 422 field mapping (no raw messages/inputs reflected), profile/address retained drafts, explicit account/items/address retry controls, order-number details action, matching accessible navigation panel IDs. 35 frontend/transport tests and typecheck passed; 44 backend tests passed in disposable container with DATABASE_URL=sqlite:////tmp/test_work018.db (account, orders, security authorization/business logic, tracking security). Deprecation warnings only.
Frontend rebuilt/restarted; backend image from prior pass remains current. Self-review: credentialed API transport preserved, email immutable, validation errors sanitized, stale effects cancelled. Live local API verified phone persistence; invalid phone/PIN cause zero mutation; cross-user address/order tracking and anonymous access denied; historical shipping snapshot unchanged. Browser verified profile save/reload; address create/edit/reload; shipped and cancelled item/progress rendering; mobile390 no overflow (content380). Latest demo browser session revoked on logout and private account view removed.

Fixtures: reserved local customer.demo@example.com; QA-W018-SHIPPED and QA-W018-CANCELLED; one address named QA Work018; separate reserved QA customer for ownership checks (temporary session revoked). No payment/shipping/email to real recipients. Fixtures retained locally for user review; no automatic seed or deployment integration. Do not purge any unrelated records. Screenshot /tmp/sulocraft-work018-progress.png.

18.5 Completed.18.6 account checks performed; full acceptance Blocked by unavailable Firefox browser surface and Work01717.5 checkout→guest emailed tracking-link acceptance still Pending. Chromium-family IAB desktop/mobile checked; do not claim Firefox/real mobile device passed. No courier automation claimed. No push/deployment.

## Blocker recheck 2026-10-11
Codex rechecked available browser surfaces: only Chromium-family IAB and MCP Apps; Firefox is not connected.18.6 remains Blocked, not silently waived.
Additional local acceptance passed: a disposable QA-W018-GUEST order's request-link API returned202 with fragment token; anonymous browser opening the link rendered real order status/milestones and missing-courier states. Removing the token via navigation removed all shipment details and showed only the request-link form. This verifies request-link→guest UI, not a complete checkout/email-provider journey. No application code changed, so no rebuild/repeated unit suite required for this evidence-only pass.
Remaining: Firefox rendering; Work01717.5 full checkout→email-link acceptance. Prior35 frontend/44 backend tests, profile/address persistence and owner security evidence retained. No Gemini backend task needed. No push.

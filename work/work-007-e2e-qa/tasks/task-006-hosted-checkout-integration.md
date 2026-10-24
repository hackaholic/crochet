# Task 7.2.2 — Hosted checkout frontend integration
**Owner:** Codex
**Status:** Blocked
**Work item:** Work007

## Objective
Consume Gemini's real provider intent/callback contract, open trusted hosted checkout for Razorpay, and retain explicit mock-only simulation for mock intents. No hardcoded secrets or real charges.

## Dependencies and relevant files
- Depends on: 7.2.1
- Dependency context: 7.2.1 backend contract returned; owner is still deciding the payment gateway. Do not start integration until that decision.
- Blocked by: Owner gateway selection
- Blocker reason: Owner explicitly deferred payment integration on 2026-10-24.
- Next action: Wait for owner gateway selection; then confirm provider contract and acceptance tests.
- Inspect/edit: src/lib/api/payments.ts; reusable gateway component/helper; CheckoutPage/tests.

## Acceptance/security tests
Mock intent works; nonmock cannot call mock verification; returned amount/order/key used safely, valid callback posted, cancel/error never shows paid confirmation, script-load failure retry safe, no duplicate order on retry and no secrets in bundle. Test real provider transport at external boundary; actual test-mode browser action requires owner setup and no real money.

## Handoff
Update this contract and work-local tasks/notes/coordination, record local Docker/browser/security checks and honest provider/device limits. No push/deploy without user instruction.

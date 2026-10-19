# Task 7.2.2 — Hosted checkout frontend integration
**Owner:** Codex
**Status:** Blocked
**Work item:** Work007

## Objective
Consume Gemini's real provider intent/callback contract, open trusted hosted checkout for Razorpay, and retain explicit mock-only simulation for mock intents. No hardcoded secrets or real charges.

## Dependencies and relevant files
- Depends on: 7.2.1
- Dependency context: Current provider is a placeholder; await typed/public-key/error/cancel return. Early fail-closed nonmock guard is safe independently.
- Blocked by: 7.2.1
- Blocker reason: Real provider backend contract needed.
- Next action: Read task-005 return, define deterministic hosted callback/cancel/error tests before implementation.
- Inspect/edit: src/lib/api/payments.ts; reusable gateway component/helper; CheckoutPage/tests.

## Acceptance/security tests
Mock intent works; nonmock cannot call mock verification; returned amount/order/key used safely, valid callback posted, cancel/error never shows paid confirmation, script-load failure retry safe, no duplicate order on retry and no secrets in bundle. Test real provider transport at external boundary; actual test-mode browser action requires owner setup and no real money.

## Handoff
Update this contract and work-local tasks/notes/coordination, record local Docker/browser/security checks and honest provider/device limits. No push/deploy without user instruction.

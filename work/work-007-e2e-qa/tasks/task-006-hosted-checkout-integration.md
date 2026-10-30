# Task 7.2.2 — Hosted checkout frontend integration
**Owner:** Codex
**Status:** Completed
**Work item:** Work007

## Objective
Consume Gemini's Cashfree intent contract, open Cashfree hosted checkout using its payment session ID, and retain explicit mock-only simulation for mock intents. No hardcoded secrets or real charges.

## Dependencies and relevant files
- Depends on: 7.2.3
- Dependency context: Owner selected Cashfree hosted web checkout. Gemini's backend task is ready; frontend starts once `paymentSessionId` and verification response contract are returned.
- Blocked by: None
- Blocker reason: None
- Next action: Consume Gemini's returned API contract and implement Cashfree's SDK redirect.
- Inspect/edit: src/lib/api/payments.ts; reusable gateway component/helper; CheckoutPage/tests.

## Acceptance/security tests
- [x] Local Mock checkout remains explicit and completes using a real catalogue item.
- [x] Cashfree uses the server-provided payment session and the API-selected `sandbox` / `production` environment; no frontend credentials.
- [x] Return query values are treated as untrusted input; only a matching backend response with `provider=cashfree`, `status=SUCCESS`, the same payment ID, and provider order ID displays payment confirmation.
- [x] Pending/error results keep the page unconfirmed and allow a retry; SDK errors are redacted.
- [x] Focused tests, typecheck, production build, SAST, local Docker and browser checks recorded in [7.2.4.2](task-018-cashfree-local-acceptance.md).

Actual Cashfree sandbox browser transaction remains in 7.2.4.3 and requires the configured preprod runtime; no live payment was performed.

## Handoff
Frontend integration is returned to Work 007. Gemini owns preprod runtime wiring under 7.2.4.1; Cashfree Sandbox browser acceptance remains 7.2.4.3. No push/deploy performed.

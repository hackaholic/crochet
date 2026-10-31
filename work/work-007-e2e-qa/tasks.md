# Work 007 tasks

## In Progress

- [ ] 7.2.4.3 Codex: [Dev Cashfree Sandbox end-to-end](tasks/task-019-cashfree-dev-sandbox-e2e.md) — Preprod Sandbox success and total parity pass; Gemini returned backend retry contract `7.2.4.5`; Codex integrates frontend retry UI and completes cancellation, pending, retry and customer history browser checks after this verified COD-removal revision reaches dev.
- [ ] 7.13 Codex: [Remove Cash on Delivery from new purchases](tasks/task-023-remove-cash-on-delivery.md) — local implementation, tests, security checks, Docker rebuild, and browser verification complete; dev push/deployment confirmation remains.

## Pending


- [ ] 7.2.4 Cashfree end-to-end and production-readiness track; subtasks 7.2.4.1–7.2.4.4 below.
- [ ] 7.2.4.4 Codex + Gemini: [Production configuration parity](tasks/task-020-cashfree-production-config-parity.md) — Gemini backend parity tests (`7.2.4.4-TC01`..`TC03`, `41/41` passing) and go-live checklist completed; final sign-off follows `7.2.4.3` dev Sandbox E2E.
- [ ] 7.2 Codex + Gemini: Multi-provider regression (Mock, Cashfree, retained Razorpay) per [task-002-payment-reconciliation.md](tasks/task-002-payment-reconciliation.md) — Gemini backend multi-provider suite completed (`28/28` isolated PostgreSQL tests passing).
- [ ] 7.3 Codex: Mobile viewport rendering matrix verification per [task-003-mobile-rendering-matrix.md](tasks/task-003-mobile-rendering-matrix.md).
- [ ] 7.4 Owner + Codex + Gemini: Pre-launch quality sign-off per [task-004-prelaunch-signoff.md](tasks/task-004-prelaunch-signoff.md).

## Completed

- [x] 7.2.4.5 Gemini: [Secure retry after failed/pending Cashfree payment](tasks/task-022-cashfree-safe-retry.md) — Completed & returned to Codex; guest capability enforcement (`validate_guest_order_token` via `guestOrderToken`/`X-Guest-Order-Token`/`Authorization: Bearer`; query-param tokens rejected) and authenticated owner check (`404` non-enumerating with zero side effects), `POST /api/v1/payments/{payment_id}/retry`, accurate `FAILED` vs `PENDING` attempt classification on Cashfree `ACTIVE` orders, safe pending-attempt reconciliation before retry, and enriched `PaymentOut` (`orderStatus`, `orderPaymentStatus`, `verificationState`, `canRetry`, `errorMessage`). `41/41` isolated PostgreSQL payment/regression/security tests + SAST pass + local Docker API verified.
- [x] 7.2.4.1 Gemini: [Preprod runtime configuration and secret wiring](tasks/task-017-cashfree-preprod-runtime-wiring.md) — Completed; explicit `payment_provider` + `cashfree_environment` in `deploy/vps-config.example.yaml`, `.deploy/vps-config.yaml`, and `scripts/deploy_vps.py` (with fail-closed prod/preprod boundary guards), API-only secret file mounts (`cashfree_app_id`, `cashfree_secret_key`), `bootstrap_secrets.sh` required-secret enforcement, server-derived `PaymentOut.orderNumber`, and guest verification isolation (`providerOrderId` binding required before idempotent return or gateway check). `37/37` deploy/secret tests + `26/26` isolated DB payment tests + SAST pass.

- [x] 7.2.2 Codex: [Cashfree hosted checkout frontend](tasks/task-006-hosted-checkout-integration.md) — server session/environment handoff, explicit local Mock, backend-only return verification, pending/failure/retry states; local Docker/browser and security evidence in task-018.
- [x] 7.2.4.2 Codex: [Frontend and local checkout acceptance](tasks/task-018-cashfree-local-acceptance.md) — 20 focused tests, typecheck/build/SAST pass, local Mock order/browser verified; no Cashfree sandbox transaction performed.
- [x] 7.12 Codex: [Layered recommendations on order confirmation](tasks/task-021-order-confirmation-recommendations.md) — full-width confirmation, API-driven recommendation layers, purchased-product exclusion, local desktop/mobile verification, 24 focused tests and SAST pass.

- [x] 7.2.5 Codex: [Add Cashfree fields to the SOPS backend group](tasks/task-016-cashfree-sops-secret-fields.md) — fields prepared and owner-populated; decrypt allowlist and file-backed App ID support added; 7 helper tests pass; ciphertext round-trip verified.

- [x] 7.2.3 Gemini: [Cashfree payment provider backend](tasks/task-015-cashfree-provider-api.md) — Completed; Cashfree PG adapter (`v2023-08-01`), `paymentSessionId` intent contract, server-side status verification (`GET /pg/orders/{id}` + `/payments`), Base64 HMAC-SHA256 webhook signature (`x-webhook-timestamp` + raw bytes), confirmed-only refunds, 24/24 isolated PostgreSQL tests (`18/18` payment + `6/6` purchase regression), 0 blocking SAST findings, live Docker API verified.

- [x] 7.11 Codex — [Checkout contact prefill](tasks/task-014-checkout-contact-prefill.md):11tests/typecheck, local authenticated profile/checkout and mobile acceptance.

- [x] 7.10 Codex: [Ranked discovery integrated acceptance](tasks/task-012-ranked-discovery-local-acceptance.md) — actual ranked API, five sections/all steps and mobile paging verified.

- [x] 7.6.1 Gemini: [Discovery allocation/ranking follow-up](tasks/task-013-discovery-section-allocation.md) — Completed. Deterministic round-robin allocation eliminates strategy starvation; surfaces all eligible groups (Popular, New, Featured, Trending, Related); strict ranking provenance (eligible sales only for Popular, genuine Review records for Trending, zero broad fake backfill for New); tenant isolation and 0 DB mutations. 9/9 tests passing in isolated test container; live Docker verified.
- [x] 7.6 Gemini: [Ranked discovery API](tasks/task-008-discovery-ranking-api.md) — Completed. GET /api/v1/storefront/discovery with opaque cursor pagination, truthful ranking strategies (related, popular, newest, featured, trending), cross-section/cross-page deduplication, and basket exclusion. 6/6 tests passing in isolated test container; live Docker verified.
- [x] 7.7 Codex: [Scrollable discovery feed](tasks/task-009-discovery-feed-ui.md) — client complete; ranked API acceptance remains 7.10.
- [x] 7.8 Codex: [Full-width checkout and basket button](tasks/task-010-checkout-width-basket-button.md).
- [x] 7.9 Codex: [Basket discovery parity](tasks/task-011-basket-discovery-parity.md).

- [x] 7.5 Codex: [Checkout presentation and discovery](tasks/task-007-checkout-presentation-discovery.md) — compact responsive layout, shared Quick Add, local browser/tests/security evidence returned.

- [x] 7.2.1 Gemini: [Payment provider hardening](tasks/task-005-payment-provider-hardening.md) — Completed; real Razorpay boundary, fail-closed HMAC, order-binding, and 11 passed payment tests.
- [x] Initial purchase regression test suite implemented with 6 passing tests.
- [x] Vitest and Testing Library configured for frontend component tests.

## Blocked
- [ ] 7.1 Codex: [Guest/login merge regression](tasks/task-001-guest-merge-regression.md) — Docker backend/frontend/security checks pass; final localhost browser acceptance blocked by disconnected browser plugin.

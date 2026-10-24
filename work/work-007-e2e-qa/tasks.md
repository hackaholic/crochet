# Work 007 tasks

## In Progress

None.

## Pending


- [ ] 7.1 Codex: [Guest/login merge regression](tasks/task-001-guest-merge-regression.md) — remaining acceptance retained; ready to resume.

- [ ] 7.2.2 Codex: [Hosted checkout integration](tasks/task-006-hosted-checkout-integration.md) — unblocked by 7.2.1 typed return.
- [ ] 7.2 Gemini + Codex: Multi-provider payment flow testing (Mock & Razorpay) per [task-002-payment-reconciliation.md](tasks/task-002-payment-reconciliation.md).
- [ ] 7.3 Codex: Mobile viewport rendering matrix verification per [task-003-mobile-rendering-matrix.md](tasks/task-003-mobile-rendering-matrix.md).
- [ ] 7.4 Owner + Codex + Gemini: Pre-launch quality sign-off per [task-004-prelaunch-signoff.md](tasks/task-004-prelaunch-signoff.md).

## Completed

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
*(None)*

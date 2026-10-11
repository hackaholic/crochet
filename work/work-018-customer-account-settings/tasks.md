# Work 018 tasks

## Completed
- [x] 18.10 — Table order history and four local demo orders for demo.customer@example.com — Codex. Account tests/typecheck/build passed; real local login, persisted order selection and all seven delivered milestones verified; mobile has no page overflow. No push.
- [x] 18.9 — Admin account and sidebar sign-out — Codex. 12 tests/typecheck and Docker build passed; localhost admin profile/addresses/dashboard link and real sign-out to storefront verified. No push.
- [x] 18.7 Codex — [Premium shipment progress](tasks/task-008-shipment-progress-visuals.md).17 focused tests/typecheck and local desktop/mobile verified.
- [x] 18.8 Codex — [Premium account summary cards](tasks/task-009-account-summary-visuals.md).17 focused tests/typecheck and local desktop/mobile verified.
- [x] 18.5 Codex — [Account editors and progress](tasks/task-005-account-experience-ui.md).35 frontend/transport tests, typecheck,44 backend tests; local profile/address/order persistence verified.
- [x] 18.4 Gemini — [Order lifecycle progress contract](tasks/task-004-order-progress-api.md). (Controlled milestone schema PLACED->CONFIRMED->PROCESSING->READY_TO_SHIP->SHIPPED->OUT_FOR_DELIVERY->DELIVERED, terminal explanations for CANCELLED/REFUNDED, truthful un-backfilled timestamps DEC018-4, 18 backend & 4 frontend tests passed).
- [x] 18.3 Gemini — [Address validation and ownership](tasks/task-003-address-management-api.md). (Strict Indian PIN code regex `^[1-9][0-9]{5}$`, phone validation, whitespace trimming & Unicode text support, single default invariant with deletion fallback, IDOR authorization protection, immutable historical order snapshots; 32 backend & 4 frontend tests passed).
- [x] 18.2 Gemini — [Profile contact validation and safe email policy](tasks/task-002-profile-contact-api.md). (Delivery phone support, email immutability DEC018-3, Unicode/whitespace handling, uniqueness conflict prevention, 11 tests passed).
- [x] 18.5.1 Codex — [Account navigation shell](tasks/task-007-account-navigation-shell.md), independent of pending API changes. — 8 tests/typecheck and local desktop/mobile checks passed.
- [x] 18.1 Codex — Repository/browser audit and task contracts defined (2026-10-10). Code confirms existing tracking; local browser showed no order fixture. Planning-only checks, no behavior change.

## Completed (additional)
- [x] 18.11 — Real-catalogue demo items and linked thumbnail item table — Codex. Existing order API snapshots; local fixtures only; 17 focused tests passed; rebuilt local browser verifies real thumbnail/link/quantity/total.

## Pending
None.

## Blocked
- [ ] 18.6 Codex — [Integrated local acceptance](tasks/task-006-local-account-acceptance.md). Account/API desktop/mobile checks pass; Firefox surface unavailable and Work01717.5 guest emailed-link acceptance remains Pending. No Gemini backend blocker.

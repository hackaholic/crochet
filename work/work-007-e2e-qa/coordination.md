# Work 007 coordination

## Active pickup — 2026-10-31
**Owner:** Codex
**Status:** Active — 7.13 in progress
**Contract:** [7.13 Remove Cash on Delivery from new purchases](tasks/task-023-remove-cash-on-delivery.md)

The owner confirmed Sulocraft does not offer COD. Remove it from new checkout and reject COD at the order API boundary. Keep persisted historical COD rows and admin/reporting compatibility. Local Docker/browser verification is required before dev push; production is out of scope.

## Active pickup — 2026-10-30
**Owner:** Codex
**Status:** Returned — 7.2.5 Completed
**Contract:** [task-016-cashfree-sops-secret-fields.md](tasks/task-016-cashfree-sops-secret-fields.md)
Prepared the backend SOPS group and decrypt allowlist for Cashfree credentials. Owner enters credential values locally; do not transmit values in chat. 7.2.4 sandbox acceptance remains dependent on frontend 7.2.2 and owner-configured sandbox credentials.

This file is the work-local coordination entry point. The work folder is the source of truth: read this file with README.md, tasks.md, decisions.md, and only the assigned task contract.

## Current handoffs

Current implementation owner and status are recorded in the selected task entry in tasks.md. If no task is In Progress, the work is queued, completed, or blocked as that file states. A cross-agent handoff becomes active only when an exact contract is assigned and this section links to it.

## Return protocol

The assigned agent updates the exact contract, tasks.md, notes.md, and this file before returning the task. The global registry at docs/handoffs.md points here; it does not duplicate this work's status.

## Previous pickup — 2026-10-19
- Codex: 7.1 In Progress (guest merge & cart regression).
- Gemini: 7.2.1 Completed ([task-005-payment-provider-hardening.md](tasks/task-005-payment-provider-hardening.md)). Provider abstraction and Razorpay boundary hardened; 11/11 payment tests passed. Unblocks 7.2.2 for Codex.
- Codex: 7.2.2 Ready for pickup ([task-006-hosted-checkout-integration.md](tasks/task-006-hosted-checkout-integration.md)).

## Current return — 2026-10-20
**Owner:** Codex
**Status:** Returned — 7.5 Completed
[7.5 checkout presentation/discovery](tasks/task-007-checkout-presentation-discovery.md) includes exact tests/security/local screenshot evidence. No new Gemini dependency; existing backend recommendation enhancement remains Work023/23.3. 7.1 and 7.2.2 remain pending; no push or deployment.

## Current extension return — 2026-10-20
**Owner:** Codex
**Status:** Returned — 7.7, 7.8, 7.9 frontend completed locally
Gemini is assigned pickup-ready [7.6](tasks/task-008-discovery-ranking-api.md); read work/GEMINI_WORKFLOW_PROMPT.md first. Frontend files exclusively Codex; backend schema/service/tests Gemini. Exact section/cursor contract is task-008. No asset uploads/setup required. Codex [7.10](tasks/task-012-ranked-discovery-local-acceptance.md) verifies actual rankings after return. Current newest fallback is verified, not labelled as live featured/trending/popular. No push/deploy.

## Current Gemini return — 2026-10-20
**Owner:** Gemini
**Status:** Returned — 7.6 Completed
[7.6 discovery ranking API](tasks/task-008-discovery-ranking-api.md) completed with GET `/api/v1/storefront/discovery`. Schema `DiscoverySectionOut` / `DiscoveryResponse`, service `backend/app/services/discovery.py`, endpoint in `backend/app/api/v1/storefront.py`. Opaque URL-safe base64 cursor (`<=512` chars, `catalogue:` prefix handled), active cart item exclusion, cross-section/cross-page deduplication, max 5 sections, max 8 products/section, max 16 products/page. Real ranking strategies (`related`, `popular`, `new-arrivals`, `featured`, `trending`). 6/6 tests passing in `backend/tests/test_storefront_discovery.py`, 3/3 in `src/lib/api/productDiscovery.test.ts`, 6/6 in `backend/tests/test_purchase_regression.py`. Live Docker API container rebuilt and verified on port 8000. Codex is unblocked for [7.10](tasks/task-012-ranked-discovery-local-acceptance.md). No push or preprod deployment.


## Codex integration review — 2026-10-20
7.6 returned;7.10 Blocked on [7.6.1 allocation/ranking follow-up](tasks/task-013-discovery-section-allocation.md). Gemini pickup ready. Exact defects, verified inputs, negative tests and return requirements are in task-013. Preserve completed7.6 history. No push/deploy.

## Current Gemini return — 2026-10-20
**Owner:** Gemini
**Status:** Returned — 7.6.1 Completed
[7.6.1 discovery section allocation and ranking](tasks/task-013-discovery-section-allocation.md) completed. Resolved strategy starvation via deterministic round-robin allocation; all eligible groups (`popular`, `new-arrivals`, `featured`, `trending`, and `related` when cart present) surface across pages. Enforced strict ranking provenance: eligible sales only for Popular (PAID/COD, excluding cancelled/refunded/failed orders), genuine `Review` table records for Trending (rejecting unverified `Product.reviews_count`), zero broad fake backfill for New Arrivals, and empty unsupported groups omitted. Verified authenticated/guest cart tenant isolation, IDOR protection on claimed guest tokens, and 0 database mutations on GET. 9/9 tests passing in `backend/tests/test_storefront_discovery.py`, 3/3 in `src/lib/api/productDiscovery.test.ts`, 6/6 in `backend/tests/test_purchase_regression.py`, 0 blocking SAST findings. Live Docker API container verified on port 8000. Codex is unblocked to resume [7.10 ranked discovery local acceptance](tasks/task-012-ranked-discovery-local-acceptance.md). No push or deployment.



## Final discovery acceptance — 2026-10-20
Codex7.10 Returned/Completed after Gemini7.6.1: balanced sections, live deduplicated pages, actual checkout/mobile/all-step rendering accepted. Exact task-012 return. Owner authorizes combined dev commit/push; production promotion not requested.

7.11 Active — Codex: authenticated contact prefill via existing profile API; task-014 contract. No Gemini dependency or deployment.

7.11 Returned/Completed — Codex: signed-in contact prefill using existing profile endpoint, draft preservation and identity isolation.11tests/typecheck, Docker rebuild and local profile comparison/mobile acceptance passed. Task-014 return; no Gemini dependency/push.

## Cashfree integration handoff — 2026-10-30
**Owner:** Codex (unblocked for frontend 7.2.2); Gemini 7.2.3 Completed / Returned.
**Status:** 7.2.3 Returned / Completed by Gemini; owner Sandbox credentials configured; 7.2.2 completion reported but not present in current checkout; runtime wiring and frontend reconciliation remain.
**Contract:** [7.2.3 Cashfree provider backend](tasks/task-015-cashfree-provider-api.md) (Completed) -> unblocks [7.2.2 Hosted checkout frontend](tasks/task-006-hosted-checkout-integration.md).
- `POST /api/v1/payments/intent` returns `paymentSessionId`, `providerOrderId`, `environment` (`sandbox`|`production`), and `returnUrl` (`${FRONTEND_URL}/checkout?orderNumber=${orderNumber}&paymentId=${paymentId}&cfOrderId=${providerOrderId}`). Private secrets never cross the API boundary (`keyId: null`).
- `POST /api/v1/payments/verify` accepts `{ "paymentId": ..., "providerOrderId": ... }` (`providerPaymentId` is optional for Cashfree) and queries Cashfree server-side (`GET /pg/orders/{id}` and `/payments`), confirming only when `order_status === "PAID"` with matching amount and currency.
- 24/24 tests passing in isolated PostgreSQL container (`18/18` in `test_payments.py`, `6/6` in `test_purchase_regression.py`), SAST PASS (0 blocking High/Critical), live Docker API rebuilt and verified on port 8000. No push/deploy/live transaction performed.

## Active pickup — 2026-10-24
Codex owns 7.1 local cart/login/logout acceptance. Existing personalization plumbing, merge ownership filter and logout cookie retirement are already present; verify rather than reimplement. No Gemini dependency currently. Payment integration deferred by owner until gateway selection; do not start 7.2.2.

## 7.1 acceptance return — 2026-10-24
Codex: Blocked on browser connection only. Docker merge/purchase/security regressions and five ProductPage tests/typecheck passed; existing fixes reused, additional security assertions added. No Gemini dependency. Exact evidence and next action in task-001; no push/deploy.

## Cashfree sandbox E2E handoff — 2026-10-30
**Owner:** Gemini for 7.2.4.1; Codex owns 7.2.4.2; Codex + Gemini own 7.2.4.3–7.2.4.4.
**Status:** 7.2.4.1 ready for Gemini pickup; later subtasks Pending.
**Contract:** [backend preprod runtime wiring](tasks/task-017-cashfree-preprod-runtime-wiring.md).
**Inputs verified:** owner populated sandbox credentials in `secrets/encrypted/backend.enc.env`; values remain undisclosed. Demo account: `demo.customer@example.com`.
**Audit note:** 7.2.2 is reported complete by owner, but its contract remains Pending and this checkout contains no Cashfree SDK/session handling under `src`; reconcile before claiming frontend acceptance. Do not duplicate tests that have valid evidence.

## Active pickup — 2026-10-30
**Current Owner:** Codex
**Status:** Active
**Active Task:** [7.2.4.2 frontend and local checkout acceptance](tasks/task-018-cashfree-local-acceptance.md)
**Next Action:** Implement hosted SDK handoff and backend-only payment return verification; run focused tests and local Docker verification.
**Parallel handoff:** Gemini may pick up [7.2.4.1 preprod runtime configuration and secret wiring](tasks/task-017-cashfree-preprod-runtime-wiring.md). Before pickup, read `work/GEMINI_WORKFLOW_PROMPT.md` and this exact contract. Its return-verification section will be updated with the security review finding before handoff.

## Current return — 2026-10-30
**Current Owner:** Gemini for 7.2.4.1; Codex owns pending 7.12
**Status:** Gemini handoff Ready for pickup; Codex 7.2.2 and 7.2.4.2 Returned/Completed
**Active Task:** [7.2.4.1 preprod runtime and secret wiring](tasks/task-017-cashfree-preprod-runtime-wiring.md)
**Next Action:** Gemini reads `work/GEMINI_WORKFLOW_PROMPT.md` and picks up task-017. Codex starts 7.12 after the backend handoff is underway; 7.2.4.3 remains gated on runtime wiring and preprod acceptance.
**New scope:** Owner requested layered product recommendations on the order confirmation screen; exact contract is [7.12](tasks/task-021-order-confirmation-recommendations.md). It reuses existing discovery and does not change the Cashfree release gate.

## Active pickup — 2026-10-31
**Current Owner:** Codex for 7.2.4.3 dev deployment & browser checkout; Gemini returned completed backend checks for 7.2.4.1, 7.2.4.3, 7.2.4.4, and 7.2; Codex completed 7.12.
**Status:** 7.2.4.1, 7.2.4.2, Gemini's 7.2.4.3 backend checks, 7.2.4.4 backend parity, and 7.12 are complete. Codex's 7.2.4.3 browser scenarios remain active.
**Completed Tasks:** [7.2.4.1 preprod runtime and secret wiring](tasks/task-017-cashfree-preprod-runtime-wiring.md), [7.12 layered order-confirmation recommendations](tasks/task-021-order-confirmation-recommendations.md).
**Next Action:** Push the locally verified revision to `dev`, confirm its deployment, then run browser Cashfree Sandbox checkout (`7.2.4.3-TC01` & `TC02`) in [7.2.4.3 Dev Cashfree Sandbox E2E](tasks/task-019-cashfree-dev-sandbox-e2e.md).
**Evidence (7.2.4.1, 7.2.4.3, 7.2.4.4, 7.2 backend):** Explicit `payment_provider` + `cashfree_environment` in `deploy/vps-config.example.yaml`, `.deploy/vps-config.yaml`, and `scripts/deploy_vps.py` (blocking `mock`/`sandbox`/`secrets/encrypted` in `prod` and enforcing `sandbox` in `preprod`); API-only secret mounts (`cashfree_app_id`, `cashfree_secret_key`) in `backend/docker-compose.yml` and `docker/compose.preprod.yaml`; required-secret check in `backend/scripts/bootstrap_secrets.sh`; local `docker/compose.yaml` retained on `mock`; server-derived `PaymentOut.orderNumber` and guest verification isolation in `backend/app/api/v1/payments.py`. `41/41` deploy/secret parity unit tests (`7.2.4.1-TC01`..`TC05`, `7.2.4.4-TC01`..`TC03`) + `28/28` isolated PostgreSQL payment/regression tests (`7.2.4.1-TC06`..`TC07`, `7.2.4.3-TC03`..`TC04`, and `7.2` multi-provider) + redacted live Cashfree Sandbox API smoke test (`SANDBOX_SMOKE_OK` using SOPS `secrets/encrypted/backend.enc.env`) + SAST pass + local Docker API verified.
**Evidence (7.12):** Confirmation reuses the existing discovery feed on the full checkout width; post-order Quick Add only calls the basket callback; purchased products are excluded even after the basket clears. Focused frontend tests 24/24, typecheck, final production build/budgets, SAST 0 findings, local API/storefront healthy, Playwright COD confirmation checked at desktop and 390×844.

## Active Cashfree browser work — 2026-10-31
**Current Owner:** Codex for frontend retry UI integration & 7.2.4.3 preprod browser acceptance; Gemini 7.2.4.5 Completed / Returned.
**Backend Handoff:** [7.2.4.5 secure retry authorization](tasks/task-022-cashfree-safe-retry.md) returned Completed by Gemini; no active Gemini task remains.
**Handoff State:** Returned; Codex owns frontend integration and 7.2.4.3 preprod acceptance.
**Finding:** Cashfree Sandbox success passes with server-confirmed ₹898 INR. Before Gemini's return, a FAILED attempt had no secure retry path. Backend authorization is now integrated with the checkout UI locally; retry/cancel/pending/customer-history scenarios still need preprod acceptance.
**Evidence (7.2.4.5 backend return):**
- Enforced guest capability validation (`validate_guest_order_token` via `guestOrderToken` / `guestTrackingToken` in JSON body or `X-Guest-Order-Token` / `Authorization: Bearer` header; query-param tokens rejected with `404`) and authenticated owner checks (`404` non-enumerating, zero side effects) on `POST /api/v1/payments/intent` and new `POST /api/v1/payments/{payment_id}/retry`.
- `CashfreePaymentProvider.verify_payment` now inspects `GET /pg/orders/{id}/payments` when `order_status == "ACTIVE"` to distinguish terminal attempt failures (`FAILED`, `USER_DROPPED`, `CANCELLED`, `VOID` -> `status: "FAILED"`, `verificationState: "FAILED"`, `errorMessage`) from `PENDING` (`status: "PENDING"`, `verificationState: "PENDING"`).
- `PaymentOut` (and `POST /api/v1/payments/verify` HTTP `400` responses after ownership/binding validation) now includes `orderStatus`, `orderPaymentStatus`, `verificationState`, `canRetry`, and `errorMessage`.
- Safe retry policy checks prior `PENDING` Cashfree attempts against the gateway before issuing a new session (reconciling to `PAID` and blocking duplicate intents if the gateway already confirmed payment, or superseding prior `PENDING` rows once the new attempt is created).
- `41/41` isolated PostgreSQL tests (`7.2.4.5-TC01`..`TC06` + payment/purchase/security regressions), SAST `0` blocking findings, and local Docker API verified on port `8000`.
**Frontend integration evidence:** Guest capability is retained only in tab-scoped session storage and sent in JSON bodies, never in URLs. Local checkout distinguishes FAILED/PENDING, shows same-order retry only when server `canRetry` permits it, and preserves the existing order rather than creating a second order. Focused frontend tests `25/25`, typecheck, Docker production build (96 API-backed pages and budgets), API health and local browser simulation pass. Retry request body verified as `{"guestOrderToken":"qa-guest-token"}`; no real charge.
**Next Action:** Deploy the locally verified revision to isolated preprod, confirm the build, then complete failure retry, cancellation/USER_DROPPED, pending and customer-history browser checks in [7.2.4.3](tasks/task-019-cashfree-dev-sandbox-e2e.md). No production payment or promotion.

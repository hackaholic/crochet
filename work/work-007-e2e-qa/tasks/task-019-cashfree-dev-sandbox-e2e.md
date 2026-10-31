# Task 7.2.4.3 — Cashfree sandbox end-to-end test on dev

**Owner:** Codex  
**Status:** In Progress

## Objective

Complete a Cashfree Sandbox checkout on `dev.sulocraft.com` for the demo customer, then verify the order, payment, webhook and customer-facing history.

## Context

Read Work 007 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract. Use Cashfree Sandbox only. The owner configured sandbox credentials in the encrypted preprod SOPS group. Use `demo.customer@example.com` and a real active catalogue product. Local checks must pass before deployment. Do not use production credentials or submit a real charge.

## Scope

- In scope: deploy the locally verified revision to the isolated preprod stack through the existing deploy workflow; configure the Cashfree test webhook at `https://api-dev.sulocraft.com/api/v1/payments/webhook/cashfree`; exercise success, failure, cancellation, pending and retry; verify server-side reconciliation, idempotency, totals and customer history.
- Out of scope: production credentials, live charges, destructive cleanup of test orders, production deployment.

## Dependencies and relevant files

- Depends on: [7.2.4.1](task-017-cashfree-preprod-runtime-wiring.md), [7.2.4.2](task-018-cashfree-local-acceptance.md), [7.2.5](task-016-cashfree-sops-secret-fields.md)
- Dependency context: Backend runtime wiring and local acceptance must return complete. Owner sandbox credentials are configured; never include values in the contract.
- Blocked by: None
- Blocker reason: None
- Next action: Deploy the locally verified backend/frontend revision to isolated preprod, then exercise Cashfree FAILED retry, USER_DROPPED/cancel, PENDING, and customer order-history scenarios.
- Inspect/edit: `https://dev.sulocraft.com`, `https://api-dev.sulocraft.com`, Cashfree Sandbox webhook settings, payment/order state and demo customer history.

## Test cases

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 7.2.4.3-TC01 | Sandbox success reconciles order | Success | Demo guest buys Handcrafted Deity Poshak using Cashfree Sandbox success simulator | Server confirms one payment/order; amount, currency and UI status match | Dev browser plus payment verification response | PASS: corrected total ₹898; Cashfree simulator explicitly stated no actual debit; `/api/v1/payments/verify` returned `SUCCESS`, `cashfree`, ₹898/89800 paise, INR; checkout displayed Payment Confirmed for `CB-20261030-02BD`. Guest account history remains unverified. |
| 7.2.4.3-TC02 | Failure/cancel/pending stay unpaid and can retry safely | Failure | Cashfree Sandbox simulator returns FAILED, USER_DROPPED or PENDING | No false success; customer can safely retry the same eligible order | Dev browser/API state check | PARTIAL: preprod FAILED simulator made no debit and never showed false success. Gemini added the capability-protected same-order retry API; Codex UI now displays separate FAILED/PENDING states and exposes retry only when `canRetry=true`. Local unit/browser simulation passed, including guest capability in retry JSON body and no duplicate order creation. Preprod retry plus USER_DROPPED/cancel and PENDING scenarios remain after deployment. |
| 7.2.4.3-TC03 | Webhook signature/replay safety | Security | Deliver event twice, invalid-signature and out-of-order events | One transition only; invalid/replayed events rejected or ignored | `backend/tests/test_payments.py::test_7_2_4_3_tc03_webhook_signature_replay_and_out_of_order_safety` | PASS (invalid signature -> `400`; duplicate replay -> idempotent `200`; late `PAYMENT_FAILED_WEBHOOK` after `PAID` ignored, order stays `CONFIRMED`/`PAID`) |
| 7.2.4.3-TC04 | Order/customer/amount binding | Security | Verify with mismatched order, customer, amount or currency | No mismatched/foreign order becomes paid; safe error | `backend/tests/test_payments.py::test_7_2_4_3_tc04_order_customer_amount_currency_binding` | PASS (wrong user -> `404` anti-enumeration; foreign `providerOrderId` -> `400`; mismatched currency `USD` or underpaid amount -> `400`; order stays unpaid) |
| 7.2.4.3-TC05 | No secret disclosure or real charge | Security | Review API response, browser network and redacted logs | Secrets stay backend-only; payment uses Sandbox | Redacted live Cashfree Sandbox smoke check + `test_7_2_4_1_tc04_credentials_stay_backend_only` | PASS (`env=sandbox`, `key_id_is_none=True`, `has_session=True`, zero secret values in payload/logs) |
| 7.2.4.3-TC06 | Displayed total matches server-authoritative payment amount | Regression | Add a ₹799 item and reach review/payment | Cart, checkout review, order API and Cashfree all show ₹898 (₹99 shipping); threshold orders use free shipping consistently | `src/lib/commerce/shipping.test.ts`, `src/pages/CheckoutPage.test.tsx`, local browser, dev browser | PASS: local browser and Cashfree Sandbox success confirm ₹898; preprod displays ₹898 after `bffefc1` |

## Security validation

- Changed trust boundary: public Cashfree callbacks reach the dev API; sandbox orders enter the isolated preprod database.
- Controls: raw-body signature verification; order/user/amount/currency binding; duplicate/out-of-order guards; explicit sandbox mode; separate preprod DB/credentials; no secrets in frontend/logs; no real payment.
- Commands/results:
  - `./scripts/test.sh all` -> complete Docker backend/frontend/security gate exited successfully; frontend Vitest `409/409`, SAST `0` blocking findings, secret scan `0` leaked secrets.
  - `docker-compose --env-file .env -f docker/compose.yaml up -d --build api frontend` -> API healthy; local storefront returned HTTP `200` and rendered the Sulocraft home page in Playwright. Logged-out auth/wishlist calls returned expected `401`; favicon `404` is unrelated to checkout.
  - `(cd backend && bash scripts/run_isolated_tests.sh tests/test_payments.py tests/test_purchase_regression.py)` -> `28 passed in 24.1s` (`22/22` in `test_payments.py`, `6/6` in `test_purchase_regression.py`)
  - Redacted live Cashfree Sandbox API smoke check via SOPS-decrypted `secrets/encrypted/backend.enc.env` -> `SANDBOX_SMOKE_OK provider=cashfree env=sandbox has_session=True has_order_id=True key_id_is_none=True unpaid_verify_false=True state=PENDING`
  - `bash scripts/security/scan-sast.sh` -> `PASS: Zero blocking High/Critical SAST findings detected`
- Additional local verification after Gemini returned 7.2.4.5: `corepack pnpm exec vitest run src/lib/api/payments.test.ts src/pages/CheckoutPage.test.tsx` -> `25/25` passed; `corepack pnpm run typecheck` passed; isolated PostgreSQL payment/purchase/authz suite -> `41/41` passed; SAST -> `0` blocking High/Critical findings (`33` existing warnings); Docker production build with non-secret preprod public API/origin and local prerender API -> 96 public pages rendered and JS/CSS budgets passed; local Docker API health and storefront HTTP 200; Playwright simulated server `FAILED` response, displayed the order-specific retry action, and verified `guestOrderToken` was sent in the retry JSON body, not URL. No live charge.
- Disposition: In Progress (Gemini backend and local frontend integration verified; preprod retry/cancel/pending/customer-history browser checks remain)
- Findings/blockers: No local blocker. Existing browser logs include expected logged-out `401` calls and favicon `404`; unrelated. Do not claim preprod retry/cancel/pending/customer history complete until tested against the deployed revision.

## Acceptance checks

- [x] Local phase passes before deploy; the complete Docker test/security gate passed on the current working tree, with local API/storefront healthy after rebuild.
- [ ] Displayed totals match backend and Cashfree before any test authorization.
- [ ] Sandbox success, failure, cancel, pending and retry outcomes are recorded.
- [ ] Webhook signature, replay, order-binding and amount/currency checks pass.
- [ ] Demo customer sees one correct order and truthful payment timeline.
- [ ] No real charge or secret disclosure; preprod data remains isolated from production.

## Handoff back

Codex records sanitized evidence, updates this contract and Work 007 status, and reports any dashboard blockers. No production promotion occurs in this task.

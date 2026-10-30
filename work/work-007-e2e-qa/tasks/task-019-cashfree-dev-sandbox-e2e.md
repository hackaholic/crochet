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
- Next action: Push the locally verified revision to `dev`, confirm the deployment workflow and deployed sandbox mode, then run the Cashfree browser scenarios.
- Inspect/edit: `https://dev.sulocraft.com`, `https://api-dev.sulocraft.com`, Cashfree Sandbox webhook settings, payment/order state and demo customer history.

## Test cases

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 7.2.4.3-TC01 | Sandbox success reconciles order | Success | Demo customer buys real active product using Sandbox success flow | Server confirms one payment/order; history shows correct product and total | Dev browser plus read-only backend state check | Ready for dev deploy & browser run (live Cashfree Sandbox API `create_intent` + `verify_payment` verified via SOPS credentials: `SANDBOX_SMOKE_OK`) |
| 7.2.4.3-TC02 | Failure/cancel/pending stay unpaid | Failure | Exercise Sandbox failure, cancel and pending flows | No false success; safe retry available | Dev browser/API state check | Backend verified against live Cashfree Sandbox (`unpaid_verify_false=True`, `state=PENDING`) and in `test_payments.py`; dev browser run follows deploy |
| 7.2.4.3-TC03 | Webhook signature/replay safety | Security | Deliver event twice, invalid-signature and out-of-order events | One transition only; invalid/replayed events rejected or ignored | `backend/tests/test_payments.py::test_7_2_4_3_tc03_webhook_signature_replay_and_out_of_order_safety` | PASS (invalid signature -> `400`; duplicate replay -> idempotent `200`; late `PAYMENT_FAILED_WEBHOOK` after `PAID` ignored, order stays `CONFIRMED`/`PAID`) |
| 7.2.4.3-TC04 | Order/customer/amount binding | Security | Verify with mismatched order, customer, amount or currency | No mismatched/foreign order becomes paid; safe error | `backend/tests/test_payments.py::test_7_2_4_3_tc04_order_customer_amount_currency_binding` | PASS (wrong user -> `404` anti-enumeration; foreign `providerOrderId` -> `400`; mismatched currency `USD` or underpaid amount -> `400`; order stays unpaid) |
| 7.2.4.3-TC05 | No secret disclosure or real charge | Security | Review API response, browser network and redacted logs | Secrets stay backend-only; payment uses Sandbox | Redacted live Cashfree Sandbox smoke check + `test_7_2_4_1_tc04_credentials_stay_backend_only` | PASS (`env=sandbox`, `key_id_is_none=True`, `has_session=True`, zero secret values in payload/logs) |

## Security validation

- Changed trust boundary: public Cashfree callbacks reach the dev API; sandbox orders enter the isolated preprod database.
- Controls: raw-body signature verification; order/user/amount/currency binding; duplicate/out-of-order guards; explicit sandbox mode; separate preprod DB/credentials; no secrets in frontend/logs; no real payment.
- Commands/results:
  - `./scripts/test.sh all` -> complete Docker backend/frontend/security gate exited successfully; frontend Vitest `409/409`, SAST `0` blocking findings, secret scan `0` leaked secrets.
  - `docker-compose --env-file .env -f docker/compose.yaml up -d --build api frontend` -> API healthy; local storefront returned HTTP `200` and rendered the Sulocraft home page in Playwright. Logged-out auth/wishlist calls returned expected `401`; favicon `404` is unrelated to checkout.
  - `(cd backend && bash scripts/run_isolated_tests.sh tests/test_payments.py tests/test_purchase_regression.py)` -> `28 passed in 24.1s` (`22/22` in `test_payments.py`, `6/6` in `test_purchase_regression.py`)
  - Redacted live Cashfree Sandbox API smoke check via SOPS-decrypted `secrets/encrypted/backend.enc.env` -> `SANDBOX_SMOKE_OK provider=cashfree env=sandbox has_session=True has_order_id=True key_id_is_none=True unpaid_verify_false=True state=PENDING`
  - `bash scripts/security/scan-sast.sh` -> `PASS: Zero blocking High/Critical SAST findings detected`
- Disposition: In Progress (backend security and live Sandbox API smoke checks passed; dev browser checkout remains)
- Findings/blockers: Preprod browser checkout and final deployment verification remain. Read-only shell requests to dev endpoints returned HTTP `403`; confirm behavior in the browser after deployment.

## Acceptance checks

- [x] Local phase passes before deploy; the complete Docker test/security gate passed on the current working tree, with local API/storefront healthy after rebuild.
- [ ] Sandbox success, failure, cancel, pending and retry outcomes are recorded.
- [ ] Webhook signature, replay, order-binding and amount/currency checks pass.
- [ ] Demo customer sees one correct order and truthful payment timeline.
- [ ] No real charge or secret disclosure; preprod data remains isolated from production.

## Handoff back

Codex records sanitized evidence, updates this contract and Work 007 status, and reports any dashboard blockers. No production promotion occurs in this task.

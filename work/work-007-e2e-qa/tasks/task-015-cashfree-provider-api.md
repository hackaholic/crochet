# Task 7.2.3 — Cashfree payment provider backend

**Owner:** Gemini  
**Status:** Completed  
**Work item:** Work 007 — End-to-end purchase & mobile rendering QA

## Objective

Implement Cashfree Hosted Web Checkout in the existing payment-provider boundary so the backend creates and verifies Cashfree orders safely and Codex can consume a stable intent contract.

## Context and contract

Read `work/GEMINI_WORKFLOW_PROMPT.md`, Work 007 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract. Cashfree is the selected provider for checkout. Keep the mock provider for local tests and preserve the existing Razorpay adapter; provider selection stays environment-configurable. Use Cashfree’s current official docs for order creation, order fetch, hosted checkout, and webhook verification. Cashfree requires server-side order creation; its hosted SDK receives a `payment_session_id`; redirects alone do not prove payment success; only server-verified `PAID` status can confirm an order.

## Scope

- In scope: Cashfree adapter, environment configuration and `.env.example` placeholders, provider registry, intent response `paymentSessionId`, server-side status verification, webhook signature/event handling and idempotent reconciliation, refund behavior compatible with current admin flow, API docs/OpenAPI, deterministic boundary/security/regression tests.
- Out of scope: frontend SDK integration (Codex task 7.2.2), production credentials/transactions, inventory reservation changes, merchant account activation, live dashboard setup, deployment, push.

## Dependencies and relevant files

- Depends on: 7.2.1
- Dependency context: Provider abstraction and fail-closed Razorpay/mock behavior are complete. Mock Cashfree HTTP boundaries in tests; credentials are required only for later sandbox acceptance.
- Blocked by: None for implementation/tests
- Blocker reason: None
- Next action: Codex picks up Task 7.2.2 (`src/lib/api/payments.ts`, `CheckoutPage`, Cashfree JS SDK integration) using the returned `PaymentIntentOut` (`paymentSessionId`, `environment`, `returnUrl`, `providerOrderId`) and `POST /api/v1/payments/verify` contract.
- Inspect/edit: `backend/app/core/config.py`, `backend/.env.example`, `backend/app/services/payment/cashfree.py`, `backend/app/services/payment/base.py`, `backend/app/services/payment/mock.py`, `backend/app/services/payment/razorpay.py`, `backend/app/services/payment/factory.py`, `backend/app/services/payment/__init__.py`, `backend/app/api/v1/payments.py`, `backend/app/schemas/payment.py`, `backend/tests/test_payments.py`, `docs/api-payments.md`, `docs/openapi.yaml`.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 7.2.3-TC01 | Create Cashfree order | success | Authorized local order; mock Cashfree create-order response | Server-derived amount/currency/customer/order metadata sent; API returns Cashfree order ID and payment session ID; no secret returned | `backend/tests/test_payments.py::test_7_2_3_tc01_cashfree_order_creation` | PASS |
| 7.2.3-TC02 | Credentials/environment | boundary/security | Missing credentials or invalid environment | Fail closed; no provider fallback; no secret in output/logs | `backend/tests/test_payments.py::test_7_2_3_tc02_cashfree_credentials_and_environment_fail_closed` | PASS |
| 7.2.3-TC03 | Server-side status verification | security | Verified PAID/PENDING/FAILED; forged frontend success; amount/order mismatch | Only matching server-verified `PAID` for stored provider order and expected amount/currency marks the order paid | `backend/tests/test_payments.py::test_7_2_3_tc03_cashfree_server_side_verification` | PASS |
| 7.2.3-TC04 | Webhook authentication | security/failure | Correct signature; missing/tampered signature; malformed body/timestamp | Verify raw bytes per current Cashfree scheme; reject invalid events with zero DB side effects | `backend/tests/test_payments.py::test_7_2_3_tc04_cashfree_webhook_authentication` | PASS |
| 7.2.3-TC05 | Duplicate/out-of-order events | regression | Replay failed/captured event, duplicate success callback/webhook | One valid transition/history/notification; no duplicate fulfillment or stock decrement | `backend/tests/test_payments.py::test_7_2_3_tc05_cashfree_duplicate_and_out_of_order_events` & `test_purchase_regression.py` | PASS |
| 7.2.3-TC06 | Gateway errors and refunds | failure | Timeout, 4xx/5xx, malformed response, unsuccessful/duplicate refund | Safe explicit failure; never false success/refund completion; existing behavior preserved | `backend/tests/test_payments.py::test_7_2_3_tc06_cashfree_gateway_errors_and_refunds` | PASS |
| 7.2.3-TC07 | Ownership/provider isolation | authorization | Cross-customer payment/order or wrong-provider webhook | Deny without leaking data or mutating another order; mock/Razorpay regressions pass | `backend/tests/test_payments.py::test_7_2_3_tc07_cashfree_ownership_and_provider_isolation` | PASS |

Configuration names to implement/document: `PAYMENT_PROVIDER=cashfree`, `CASHFREE_ENVIRONMENT=sandbox|production`, `CASHFREE_APP_ID`, and `CASHFREE_SECRET_KEY` (load the secret through the existing secret-file/vault configuration path). Never select production implicitly or fall back between environments. Preserve the current configurable `FRONTEND_URL` for the redirect; define its exact local callback contract with Codex in the response/handoff.

The Cashfree redirect may return only its order reference; do not make the frontend invent a successful transaction ID or status to satisfy the current generic verification payload. Extend the backend contract safely so it can resolve the stored payment, query Cashfree, and derive the authoritative result server-side.

## Security validation

- Trust boundaries: money/order state, Cashfree credentials, browser callback, public webhook, customer/order PII.
- Controls/negative tests: backend-only credentials; validated provider/environment; server-authoritative amount; ownership checks; current raw-body webhook scheme (`Base64(HMAC-SHA256(secret, timestamp + raw_body))`) and constant-time comparison (`hmac.compare_digest`); server status fetch (`GET /pg/orders/{order_id}` + `GET /pg/orders/{order_id}/payments`); idempotence; out-of-order replay protection; cross-provider webhook isolation; safe errors. See TC02–TC07.
- API/database: parameterized SQLAlchemy queries, bounded 15s upstream timeout, strict response validation, no client amount authority, no mutation before verified success.
- Commands/results:
  - `cd backend && bash scripts/run_isolated_tests.sh tests/test_payments.py tests/test_purchase_regression.py` -> **24 passed** in 27.70s (`18/18` payment tests + `6/6` purchase regression tests) in isolated PostgreSQL container.
  - `bash scripts/security/scan-sast.sh` -> **PASS** (0 blocking High/Critical findings).
  - Live Docker API container rebuilt and verified on `http://localhost:8000/health` (`{"status":"ok","service":"sulocraft-api"}`) and `http://localhost:8000/openapi.json` (`paymentSessionId`, `environment`, `returnUrl` present).
- Disposition: **Pass** (Self-reviewed by Gemini; no external peer review claimed).
- Findings/blockers: None.

## Acceptance checks

- [x] Cashfree provider is configured; Mock stays usable locally and Razorpay regressions pass.
- [x] Intent includes `paymentSessionId`; private credentials never cross the API boundary.
- [x] Redirect is not payment proof; only server-verified `PAID` reconciles the order.
- [x] Refund cannot report completion without provider confirmation.
- [x] Focused backend/regression/security tests pass in Docker; docs/OpenAPI and `.env.example` match.
- [x] Test matrix and security disposition recorded; no unresolved blocking findings.
- [x] Peer review is accurately labeled.
- [x] Return API response example, config variable names only, changed files, tests, and owner setup needed for sandbox acceptance.

## Return handoff — Gemini (2026-10-30)

### 1. Contract Readiness for Codex (Task 7.2.2)
The Cashfree backend intent, server-side verification, and webhook contracts are **ready for Codex pickup on Task 7.2.2**:

- **`POST /api/v1/payments/intent` Response (`PaymentIntentOut`):**
  ```json
  {
    "paymentId": 10,
    "orderId": 42,
    "orderNumber": "CB-20261030-84AF",
    "provider": "cashfree",
    "providerOrderId": "CB-20261030-84AF-10",
    "paymentSessionId": "session_cf_sandbox_a8b9c0d1e2f3",
    "environment": "sandbox",
    "returnUrl": "http://localhost:8080/checkout?orderNumber=CB-20261030-84AF&paymentId=10&cfOrderId=CB-20261030-84AF-10",
    "amount": 2599,
    "amountPaise": 259900,
    "currency": "INR",
    "keyId": null,
    "notes": {
      "orderNumber": "CB-20261030-84AF",
      "environment": "sandbox",
      "returnUrl": "http://localhost:8080/checkout?orderNumber=CB-20261030-84AF&paymentId=10&cfOrderId=CB-20261030-84AF-10"
    }
  }
  ```
- **Redirect / Return URL Format:**
  `${FRONTEND_URL}/checkout?orderNumber=${orderNumber}&paymentId=${paymentId}&cfOrderId=${providerOrderId}`
- **Server-Side Verification (`POST /api/v1/payments/verify`):**
  - `providerPaymentId` is now optional (`str | None = None`).
  - For Cashfree, the frontend sends `{ "paymentId": 10, "providerOrderId": "CB-20261030-84AF-10" }` (or `{ "paymentId": 10 }`). The backend resolves the stored `Payment`, queries Cashfree `GET /pg/orders/{providerOrderId}` and `GET /pg/orders/{providerOrderId}/payments`, verifies `order_status === "PAID"`, matching `order_amount` and `order_currency`, and populates `providerPaymentId` (`cf_payment_id`) and `paymentMethodDetail` server-side.
  - If the Cashfree order is still `"ACTIVE"` (pending/unpaid), `POST /api/v1/payments/verify` returns `HTTP 400` and preserves `payment.status = "PENDING"` and `order.status = "PENDING_PAYMENT"`. If `"EXPIRED"`/`"TERMINATED"`/failed, `payment.status` is marked `"FAILED"` while `order.status` stays `"PENDING_PAYMENT"` for safe retry.

### 2. Configuration Variable Names
- `PAYMENT_PROVIDER` (`cashfree` | `mock` | `razorpay`)
- `CASHFREE_ENVIRONMENT` (`sandbox` | `production` — required explicitly when `PAYMENT_PROVIDER=cashfree`; fails closed if unset/invalid or if `sandbox` is used when `APP_ENV=production`)
- `CASHFREE_APP_ID`
- `CASHFREE_SECRET_KEY` (supports `CASHFREE_SECRET_KEY_FILE` and `/run/secrets/backend/cashfree_secret_key` via `config_value()`)
- `CASHFREE_API_VERSION` (defaults to `2023-08-01`)

### 3. Owner Sandbox Setup Needed for Task 7.2.4
To run live Cashfree Sandbox acceptance in Task 7.2.4 (after Codex completes Task 7.2.2):
1. Obtain Cashfree Sandbox API credentials (`CASHFREE_APP_ID` and `CASHFREE_SECRET_KEY`) from the Cashfree Merchant Dashboard (Developers -> API Keys -> Test/Sandbox).
2. Add `PAYMENT_PROVIDER=cashfree`, `CASHFREE_ENVIRONMENT=sandbox`, `CASHFREE_APP_ID`, and encrypted `CASHFREE_SECRET_KEY` to the local/preprod SOPS secret group (`secrets/encrypted/backend.enc.env`).
3. Configure webhook URL `https://api-dev.sulocraft.com/api/v1/payments/webhook/cashfree` in the Cashfree Sandbox dashboard (`2023-08-01`).

## Pickup checklist

- [x] Read the shared Gemini workflow prompt, selected Work 007 context, and this contract.
- [x] Confirm assignment and set only task 7.2.3 In Progress in work-local records.
- [x] Reuse the completed provider abstraction/hardening and purchase regression tests.

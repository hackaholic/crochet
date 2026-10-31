# Task 7.2.4.5 — Backend authorization for Cashfree payment retry

**Owner:** Gemini (Returned to Codex for frontend retry UI integration & preprod acceptance)
**Status:** Completed
**Work item:** Work 007 — End-to-end purchase & mobile rendering QA

## Objective

Let a customer retry Cashfree payment for the same unpaid order after a failed or unresolved attempt, without losing the basket context, creating a duplicate order, exposing another guest's order, or allowing a paid/cancelled order to be charged again.

## Context and contract

Preprod E2E on 2026-10-31 showed a valid Cashfree `FAILED` simulator result returns to `/checkout` with `payments/verify` HTTP 400. UI displays a generic verification retry message and an empty basket; it cannot start another payment attempt. The app must distinguish `FAILED` from `PENDING`, then offer an actual retry only when the authoritative server state allows it.

`POST /api/v1/payments/intent` currently accepts guest `orderNumber` without validating a guest order capability. Do not use that path for retry as-is. Reuse the existing guest-order capability/token mechanism or define another narrowly scoped, server-validated capability. Do not place secrets/tokens in query parameters. Keep authenticated ownership checks and fail closed.

Relevant contract: [7.2.4.3 Dev Cashfree Sandbox E2E](task-019-cashfree-dev-sandbox-e2e.md).

## Scope

- In scope: backend payment retry authorization and state rules; API schema/contract changes; safe server-derived payment status/attempt response; focused backend tests and security validation.
- Out of scope: frontend retry UI (Codex integrates after API handoff), changing pricing/provider/production credentials, real charges, deleting test orders, or weakening guest order/tracking authorization.

## Dependencies and relevant files

- Depends on: [7.2.4.1](task-017-cashfree-preprod-runtime-wiring.md), [7.2.4.3](task-019-cashfree-dev-sandbox-e2e.md)
- Dependency context: Cashfree Sandbox is active on preprod. The first successful sandbox order verified amount/status reconciliation. Browser failure test order `CB-20261030-A5A6` is unpaid; retain it. Exact observed failure and no-debit evidence are in task-019 and Work 007 notes.
- Blocked by: None
- Blocker reason: None
- Next action: None; backend implementation and evidence returned. Codex integrates the customer retry UI and completes preprod browser acceptance in task-019.
- Inspect/edit: `backend/app/api/v1/payments.py`, `backend/app/schemas/payment.py`, `backend/app/models/payment.py`, existing guest order token validation in `backend/app/api/v1/orders.py` and its helper/model, `src/lib/api/payments.ts`, `src/pages/CheckoutPage.tsx`, related backend/frontend tests, `docs/api-payments.md`.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 7.2.4.5-TC01 | Retry same unpaid order after confirmed failed attempt | Success | Owner guest or authenticated customer retries a Cashfree failed attempt | New server-created attempt references the same order and exact server amount; no duplicate order; existing order remains unpaid until server confirms success | `backend/tests/test_payments.py::test_7_2_4_5_tc01_retry_same_unpaid_order_after_failed_attempt` | **PASS** — Authenticated (`POST /api/v1/payments/{id}/retry`) and guest (`POST /api/v1/payments/intent` with `guestOrderToken`) retries create new `Payment` rows referencing the same `orderId`/`orderNumber` and exact `amountPaise`; 1 `Order` row each; order stays `PENDING_PAYMENT`/`PENDING` until verified |
| 7.2.4.5-TC02 | Pending attempt is not reported as final failure/success | Boundary | Cashfree Sandbox returns pending, then customer checks/retries | UI and API preserve pending truth; retry follows an explicit safe policy; no false paid state | `backend/tests/test_payments.py::test_7_2_4_5_tc02_pending_attempt_truth_and_safe_retry_policy` | **PASS** — `POST /api/v1/payments/verify` returns HTTP `400` with `status: "PENDING"`, `verificationState: "PENDING"`, `canRetry: true`; retry while gateway is still unpaid creates new attempt and marks prior `PENDING` row `FAILED` (`Superseded by a new payment retry attempt.`); if gateway confirmed `PAID` before retry, backend reconciles order as `PAID` and blocks duplicate intent (`400`, `0` new `POST /orders` calls) |
| 7.2.4.5-TC03 | Guest retry requires the correct order capability | Security | Omit token, tamper token, or submit a token from another order when creating retry intent | Denied with non-enumerating error; no payment/order mutation and no new provider call; valid owner capability permits retry | `backend/tests/test_payments.py::test_7_2_4_5_tc03_guest_retry_requires_correct_order_capability` | **PASS** — Omitted token, tampered token, foreign order token, and URL query-param token (`?guestOrderToken=...`) all fail closed with non-enumerating `404` (`0` provider calls, `0` DB mutations); valid `guestOrderToken` / `X-Guest-Order-Token` succeeds (`201`) |
| 7.2.4.5-TC04 | Authenticated retry is owner-only | Security | Another authenticated user retries the order | Denied with non-enumerating error; no mutation/provider call | `backend/tests/test_payments.py::test_7_2_4_5_tc04_authenticated_retry_is_owner_only` | **PASS** — Foreign authenticated user and anonymous caller receive `404` on both `/api/v1/payments/intent` and `/api/v1/payments/{id}/retry` with `0` provider calls and `0` new `Payment` rows |
| 7.2.4.5-TC05 | Paid/cancelled orders cannot be retried | Failure | Retry after server-confirmed success or order cancellation | Rejected; no new payment row/session and no provider call | `backend/tests/test_payments.py::test_7_2_4_5_tc05_paid_and_cancelled_orders_cannot_be_retried` | **PASS** — Retries on `PAID` and `CANCELLED` orders return `400 Bad Request` (`canRetry: false` on verified payment) with `0` provider calls and `0` new `Payment` rows |
| 7.2.4.5-TC06 | Backend contract supports accurate failed/pending UI states | Regression | Query/retry after Cashfree FAILED and PENDING states | API distinguishes authoritative failed vs pending; only eligible unpaid order can receive a new attempt; no order duplication | `backend/tests/test_payments.py::test_7_2_4_5_tc06_backend_contract_distinguishes_failed_vs_pending_and_retry_eligibility` | **PASS** — `CashfreePaymentProvider.verify_payment` inspects `/pg/orders/{id}/payments` when `order_status == "ACTIVE"` to distinguish `PENDING` (`status: "PENDING"`, `verificationState: "PENDING"`) from terminal attempt failure (`FAILED`/`USER_DROPPED`/`CANCELLED`/`VOID` -> `status: "FAILED"`, `verificationState: "FAILED"`, `errorMessage` preserved); `canRetry` is `true` only for eligible unpaid `PENDING_PAYMENT` orders |

## Security validation (required for every subtask)

- Changed assets/trust boundaries and plausible abuse: guest/authenticated customer can request payment sessions against order identifiers; risk of IDOR, duplicate sessions, stale amount, or charging an order after it is paid/cancelled.
- Applicable controls and linked negative test IDs: server derives order/user/amount/status; validate guest capability without URL leakage; authenticated owner check; reject paid/cancelled order; avoid state mutation/provider calls on invalid auth (`TC03`–`TC05`); secrets remain backend-only.
- API/database work: validate payment/order ownership, request shape and provider state; parameterized ORM access; return safe errors; ensure failed authorization has zero side effects; preserve idempotent success handling.
- Commands/target/results and evidence (redacted):
  - `(cd backend && bash scripts/run_isolated_tests.sh tests/test_payments.py tests/test_purchase_regression.py tests/test_security_authorization.py)` -> **`41 passed` in `23.31s`** (`34/34` in `test_payments.py` including `7.2.4.5-TC01`..`TC06`, `6/6` in `test_purchase_regression.py`, `2/2` in `test_security_authorization.py`).
  - `bash scripts/security/scan-sast.sh` -> **PASS (`0` blocking High/Critical findings, `33` pre-existing CI workflow warnings)**.
  - Local Docker API rebuild & verification (`docker-compose --env-file .env -f docker/compose.yaml up -d --build api`): `GET http://localhost:8000/health` -> `{"status":"ok","service":"sulocraft-api"}`, `/openapi.json` exposes `POST /api/v1/payments/{payment_id}/retry` and enriched `PaymentOut` (`orderStatus`, `orderPaymentStatus`, `verificationState`, `canRetry`, `errorMessage`).
- Disposition: **PASS**
- Findings, severity, remediation owner, and blockers: None. Unauthenticated guest order-number access on `POST /api/v1/payments/intent` is closed; guest orders require a valid order-scoped capability token (`guestOrderToken` / `guestTrackingToken` in JSON body or `X-Guest-Order-Token` / `Authorization: Bearer` header; query-string tokens rejected with `404`).

## Acceptance checks

- [x] Failure and pending responses remain truthful and never confirm payment without server verification.
- [x] Backend exposes a safe way to retry the same eligible order without duplicate orders or amount drift; frontend integration is a Codex follow-up.
- [x] Guest and authenticated authorization tests prove wrong-owner attempts cause zero side effects.
- [x] Paid/cancelled orders cannot create another payment attempt.
- [x] Focused backend tests, SAST, and local Docker/API checks pass; evidence is recorded here.
- [x] Peer review recorded, accurately identified as independent or self-review (`Self-review completed by Gemini; independent review to be performed by Codex during frontend retry integration`).

## Handoff back

### Return Report (Gemini -> Codex)
- **Changed files:**
  - `backend/app/schemas/payment.py`
  - `backend/app/services/payment/cashfree.py`
  - `backend/app/api/v1/payments.py`
  - `backend/tests/test_payments.py`
  - `docs/api-payments.md`
- **API contract & behavior changes for Codex frontend integration:**
  1. **Accurate `FAILED` vs `PENDING` classification (`CashfreePaymentProvider.verify_payment` & `POST /api/v1/payments/verify`):**
     - When Cashfree `GET /pg/orders/{order_id}` returns `order_status == "ACTIVE"`, the backend now also queries `GET /pg/orders/{order_id}/payments`. If attempts exist and all attempts are in terminal failure states (`FAILED`, `USER_DROPPED`, `CANCELLED`, `VOID`), `_verification_state` is `"FAILED"` (and `payment_message` is captured into `errorMessage`); if any attempt is `PENDING`/`FLAGGED`/`NOT_ATTEMPTED` or no attempts exist yet, `_verification_state` is `"PENDING"`.
     - When `POST /api/v1/payments/verify` returns `HTTP 400` after ownership/order-binding validation passes, the JSON body now includes the full `PaymentOut` payload alongside `detail`:
       `{ id, orderId, orderNumber, orderStatus, orderPaymentStatus, provider, providerOrderId, amount, amountPaise, currency, status: "FAILED" | "PENDING", verificationState: "FAILED" | "PENDING", canRetry: boolean, errorMessage, detail }`.
     - `GET /api/v1/payments/{payment_id}` returns the same `PaymentOut` fields (`canRetry` is `true` only when `order.status == "PENDING_PAYMENT"`, `order.payment_status` is not `PAID`/`REFUNDED`, `order.payment_method != "COD"`, and no payment row has `status == "SUCCESS"`).
  2. **Same-order retry endpoints & capability enforcement:**
     - **Option A:** `POST /api/v1/payments/{payment_id}/retry` (body: `PaymentRetryRequest { provider?, guestOrderToken?, guestTrackingToken? }`)
     - **Option B:** `POST /api/v1/payments/intent` (body: `PaymentIntentCreate { orderId?, orderNumber?, provider?, guestOrderToken?, guestTrackingToken? }`)
     - **Authenticated orders (`order.user_id != null`):** Requires the owner's authenticated session (`404` for any other user or anonymous caller, zero side effects).
     - **Guest orders (`order.user_id == null`):** Requires the order's `guestTrackingToken` (returned by `POST /api/v1/orders` in `OrderOut.guestTrackingToken`) supplied via JSON body (`guestOrderToken` or `guestTrackingToken`) or request header (`X-Guest-Order-Token` or `Authorization: Bearer <token>`). Tokens in URL query parameters (`?token=...`, `?guestOrderToken=...`) are rejected with `404`.
     - **Safe pending-attempt policy:** If an order has a prior `PENDING` Cashfree payment when retry is requested, the backend first checks Cashfree; if that prior attempt actually succeeded (`PAID`), the backend reconciles the order to `PAID`/`CONFIRMED` and returns `400 This order has already been paid.` without creating a second session. Otherwise, it creates a new `Payment` row + Cashfree session (`{orderNumber}-{newPaymentId}`) for the exact server-derived order total and marks the superseded `PENDING` row `FAILED` (`"Superseded by a new payment retry attempt."`).
- **Database/schema effects:** No Alembic migration required (reuses existing `payments.error_message` and `guest_order_access_tokens` tables). Existing preprod orders `CB-20261030-02BD` and `CB-20261030-A5A6` are untouched.
- **Unresolved risks / next steps:** Codex integrates the frontend retry UI (`src/lib/api/payments.ts`, `src/pages/CheckoutPage.tsx`) to pass `guestOrderToken` when creating/retrying guest payment intents, distinguish `FAILED` from `PENDING` on checkout return, and wire the same-order retry action, followed by local + preprod browser acceptance (`7.2.4.3`).

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 007 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, this contract, and `work/GEMINI_WORKFLOW_PROMPT.md`.
- [x] Confirm assignment and mark only 7.2.4.5 In Progress.
- [x] Reuse the existing order token and Sandbox setup; do not repeat deployment or credential setup.

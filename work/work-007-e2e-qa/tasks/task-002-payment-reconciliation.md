# Task 7.2 — Multi-provider payment flow & webhook reconciliation testing

**Owner:** Gemini + Codex
**Status:** Pending

## Objective

Test both Mock and Razorpay payment gateways end-to-end: payment intent creation, UPI QR code display, modal completion, webhook signature verification, and order state transition to `CONFIRMED`.

## Context and contract

Refer to `docs/api-payment.md`. Razorpay signatures are HMAC-SHA256 authenticated. Mock gateway enables instant development testing.

## Scope

- In scope:
  - Verify payment intent creation returns correct integer paise amounts.
  - Test simulated Razorpay webhook payloads with signature validation.
  - Verify order inventory decrement occurs only upon confirmed payment.
- Out of scope:
  - Real money transactions.

## Dependencies and relevant files

- Depends on: 7.1
- Dependency context: Task 7.1.
- Inspect/edit:
  - `backend/app/services/payment/`
  - `backend/tests/test_payments.py`

## Acceptance checks

- [x] `pytest backend/tests/test_payments.py` passes all payment provider tests (`22/22` in `test_payments.py` + `6/6` in `test_purchase_regression.py` across Mock, Cashfree, and retained Razorpay in isolated PostgreSQL container).
- [x] Successful payment updates order payment status to `PAID` and triggers notification queue.

## Handoff back

- Gemini backend portion completed (`28/28` isolated DB payment/regression tests passing; SAST `0` blocking findings). Final task closure awaits `7.2.4.3` dev Sandbox browser E2E acceptance.

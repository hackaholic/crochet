# Task 7.2.1 — Real payment provider correctness and fail-closed reconciliation

**Owner:** Gemini
**Status:** Completed
**Work item:** Work007
**Work owner:** Codex

## Objective
Replace placeholder Razorpay operations and fail-open verification with a real, configured provider boundary and deterministic offline security/reconciliation tests. Never move real money during this task.

## Context and contract
Read work/GEMINI_WORKFLOW_PROMPT.md and Work007 README/tasks/decisions/coordination plus this contract. Existing mock provider and purchase/cart/payment regression tests pass. Codex owns auth/cart personalization and browser QA; do not edit those files. No new assets, credentials, data reset or deployment needed.

## Verified findings
- backend/app/services/payment/razorpay.py create_intent generates random `order_` instead of gateway request; refund_payment returns simulated COMPLETED IDs.
- verify_payment falls through to bool(payment_id) when signature absent, even when key_secret is configured. verify_webhook returnsTrue when secret missing. Both must fail closed for Razorpay; mock simulation belongs only to MockPaymentProvider.
- Factory currently defaults an unknown provider name to MockPaymentProvider after its production mock-name guard; reject unknown providers instead of falling back, including production.
- Callback order ID must bind to stored provider_order_id; valid HMAC for a different order must not pay this order.
- orders.py reserves/decrements stock at order creation, whereas old7.2 wording says decrement after payment. Preserve existing reservation contract unless an explicit design/test covers release on failed/cancelled/expired orders. Do not blindly move stock decrement and double-count it.
- Frontend currently only implements mock completion. Codex will prevent mock verification of nonmock intents; real hosted checkout consumption follows your typed return (7.2.2).

## Scope
- In scope: real Razorpay order/refund HTTP/SDK adapter using validated credentials/config; API/provider schema contract; fail-closed HMAC/order-binding/webhook checks; duplicate callback/webhook idempotency including status history, notifications and stock; provider-error behavior; refund cannot report completed without gateway confirmation.
- Out of scope: auth/cart source ownership or personalized-note files, frontend implementation, new secrets/migrations unless separately justified, real charges/refunds, push/deploy, changing environment architecture.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Independent backend files; base mock regression already passed. Existing provider interface/config/payment/order models reused. Consult official provider docs. No credentials needed for offline boundary tests; owner supplies test-mode account only for later live acceptance.
- Blocked by: None
- Blocker reason: None for implementation/offline tests; actual gateway test-mode session requires owner setup later.
- Next action: Completed; unblocks Codex for 7.2.2.
- Inspect/edit: backend/app/services/payment/; backend/app/api/v1/payments.py; backend/app/schemas/payment.py; payment/refund tests; docs/api-payments.md. Notify Codex before editing orders.py or changing reservation behavior.

## Test cases
| ID | Category | Action | Expected | Evidence |
| --- | --- | --- | --- | --- |
| 7.2.1-TC01 | Security | Missing secret/signature, malformed signature, wrong signed order ID, tampered body | Denied; no PAID/refund/stock/history/notification side effects | Passed in test_7_2_1_tc01_security_razorpay_fail_closed |
| 7.2.1-TC02 | Acceptance | Real adapter request mocked at external HTTP boundary, paise/currency/receipt and returned gateway IDs | Correct request/response contract; no generated fake gateway success | Passed in test_7_2_1_tc02_acceptance_mocked_http_boundary |
| 7.2.1-TC03 | Regression | Valid callback then duplicate callback/webhook, webhook before callback | One transition/history/notification; no double stock decrement/refund | Passed in test_7_2_1_tc03_regression_idempotency |
| 7.2.1-TC04 | Failure | Gateway timeout/4xx/5xx/invalid response/refund failure | Safe explicit failure, retry semantics; never false COMPLETED | Passed in test_7_2_1_tc04_resilience_gateway_failure |
| 7.2.1-TC05 | Authorization | Other user/guest or mismatched order accesses payment/refund | No access or data leak, no mutation | Passed in test_7_2_1_tc05_cross_user_authorization |
| 7.2.1-TC06 | Compatibility | Existing mock full purchase and reservation/cancel flow | Local mock works using same interface; provider selected from config | Passed in test_7_2_1_tc06_mock_provider_compatibility |

## Security validation
Money/stock/customer-order trust boundaries. No secrets in browser/response/log except provider public key ID. Parameterized DB ownership queries, constant-time HMAC, raw-body signature verification, exact provider order binding and fail-closed missing config. Do not disable security/rate limits or treat mock results as real funds. Record tests/SAST and accurately labeled self-review.

## Acceptance checks
- [x] Required tests pass in isolated Docker DB; no real gateway mutations (11/11 tests pass in tests/test_payments.py, 6/6 in test_purchase_regression.py).
- [x] Missing credentials fail closed; no simulated Razorpay success remains.
- [x] Exact frontend contract returned: provider/public key/order ID/paise/currency, callback fields, errors/retries and canceled-modal behavior.
- [x] Inventory reservation/release and duplicate reconciliation evidence recorded.
- [x] Docs/work-local tasks/notes/coordination updated; no push/deploy.

## Handoff back
Return exact files/API examples/test/security results and any owner test-mode setup needed. Codex picks 7.2.2 hosted checkout integration only after your typed return. Do not repeat completed cart/browser/assets work.

## Pickup checklist
- [x] Shared Gemini rules and selected work only read.
- [x] Confirm payments ownership; mark only 7.2.1 In Progress.
- [x] Reuse provider/config models; no real-money operation.

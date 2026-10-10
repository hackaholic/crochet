# Task 17.1 — Secure account and guest tracking API

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 017

## Objective/context and scope
Audit and preserve account ownership; close guest identifier-only disclosure. Define secure expiring order-scoped guest credential issuance through verified checkout email and safe rate-limited link request. Document exact request/response/auth/errors before returning. Reuse email abstraction and configuration; no personal contact inference. Review adjacent order detail/cancel routes for the same guest trust-boundary issue and report findings without silent scope expansion.
Out of scope: application redesign, unrelated changes, live shipment purchases, deployment.

## Dependencies and relevant files
Existing order models/auth/email; inspect backend/app/api/v1/orders.py, schemas/order.py, order services, email service and tests.

## Test cases (before implementation)
| ID | Category | Scenario / Action | Expected Result | Evidence |
| --- | --- | --- | --- | --- |
| 17.1-TC01 | Success (Owner) | Authenticated user requests tracking for their own order | 200 OK; exact persisted shipment schema | PASS (`backend/tests/test_tracking_security.py::test_tc01_owner_requests_own_order_tracking`) |
| 17.1-TC02 | Security (Account Isolation) | Authenticated user B or anonymous caller requests user A's order tracking | 404 Not Found (safe non-enumerating error, zero PII or timeline returned) | PASS (`backend/tests/test_tracking_security.py::test_tc02_account_isolation_denies_wrong_user_and_anonymous`) |
| 17.1-TC03 | Security (Guest IDOR Prevention) | Anonymous caller requests guest order tracking without a token | 404 Not Found (blocks open access to guest orders) | PASS (`backend/tests/test_tracking_security.py::test_tc03_guest_idor_prevention`) |
| 17.1-TC04 | Success (Guest Scoped Token) | Guest requests tracking with valid, unexpired, matching guest token (?token=... or header) | 200 OK; exact OrderTrackingOut schema for that exact order | PASS (`backend/tests/test_tracking_security.py::test_tc04_guest_valid_scoped_token_succeeds`) |
| 17.1-TC05 | Security (Token Validation) | Guest provides expired token, revoked token, tampered token, or token for a different order | 404 Not Found (safe rejection, zero details revealed) | PASS (`backend/tests/test_tracking_security.py::test_tc05_invalid_expired_revoked_wrong_order_token_denied`) |
| 17.1-TC06 | Security (Non-Enumerating Link Request) | Guest calls POST /api/v1/orders/tracking/request-link for existing valid order+email vs wrong order or wrong email | Both return 202 Accepted with identical response body. Email only dispatched on exact match | PASS (`backend/tests/test_tracking_security.py::test_tc06_non_enumerating_link_request`) & live curl |
| 17.1-TC07 | Boundary & Rate Limiting | Link request rate limiting triggered and malformed payload (>200 chars) | Rate-limited gracefully with 202/429; malformed input returns 422 | PASS (`backend/tests/test_tracking_security.py::test_tc07_boundary_and_validation`) & live curl |
| 17.1-TC08 | Success & Honest State | Order without courier or tracking number (None) | 200 OK with courierName: null, trackingNumber: null without fabricating carrier info | PASS (`backend/tests/test_tracking_security.py::test_tc08_honest_state_for_orders_without_shipment`) |
| 17.1-TC09 | Security (Log / PII Safety) | Verify email logs, application logs, and HTTP headers | Raw tokens never persisted or logged in plain text (SHA-256 only); Cache-Control: no-store on tracking endpoints | PASS (`backend/tests/test_tracking_security.py::test_tc09_security_logging_and_cache_control`) |

## Security validation
Order access and shipment/customer data are sensitive.
1. Enforced exact account ownership for customer orders: wrong users or anonymous requests receive 404 Not Found.
2. Closed guest IDOR: guest orders require a valid, non-expired, non-revoked token.
3. Plaintext tokens are NEVER stored in the database; only SHA-256 hashes are persisted in `guest_order_access_tokens`.
4. `POST /api/v1/orders/tracking/request-link` returns generic non-enumerating 202 Accepted, rate-limited per client IP.
5. All tracking and order endpoints return `Cache-Control: no-store, no-cache, must-revalidate, private` and `Pragma: no-cache`.
6. Audit logs redact raw magic link / tracking URLs.
Disposition: Verified and passed.

## Acceptance checks
- [x] Scoped objective completed with relevant tests/evidence (9/9 passed in `test_tracking_security.py` in isolated test container).
- [x] Security disposition and self/independent review recorded accurately.
- [x] Local verification recorded where runtime changes are made (tested on live Docker API container `docker-api-1` at `http://localhost:8000`).

## Handoff back / pickup
Task 17.1 completed. Returned to Codex for frontend integration:
- Task 17.2: Signed-in customer tracking view (use `GET /api/v1/orders/{orderNumber}/tracking` with account session cookies).
- Task 17.3: Guest shipment tracking view (use `GET /api/v1/orders/{orderNumber}/tracking?token={token}` or header `X-Guest-Order-Token: {token}`; use `POST /api/v1/orders/tracking/request-link` for lost link recovery).

## Required return contract details
- **Account tracking**: `GET /api/v1/orders/{order_id_or_number}/tracking` with session cookie or `Authorization: Bearer <session_token>`.
- **Guest tracking**: `GET /api/v1/orders/{order_id_or_number}/tracking?token=<guest_token>` or header `X-Guest-Order-Token: <guest_token>`.
- **Guest tracking link request**: `POST /api/v1/orders/tracking/request-link` with payload `{"orderNumber": "SLC-...", "email": "customer@example.com"}`. Returns generic 202 Accepted `{"message": "...", "devTrackingLink": "..."}`.
- **TTL**: Guest tokens default to 14 days expiration.
- **Errors**: Nonexistent, unauthorized, or expired requests consistently return 404 `{"detail": "Order '...' not found"}`.
- **Headers**: All responses send `Cache-Control: no-store, no-cache, must-revalidate, private`.

## Security triage
| Surface | Risk | Required negative evidence | Owner/disposition |
| --- | --- | --- | --- |
| Guest identifier lookup | Order disclosure/IDOR | Guessed ID/number denied without valid scoped credential | Gemini 17.1; RESOLVED (404 without token) |
| Signed-in access | Other account order access | Wrong account denied without fields | Gemini 17.1; RESOLVED (404 on mismatched user_id) |
| Link request | Enumeration/email abuse | Generic response, validated matching recipient, configured rate limit | Gemini 17.1; RESOLVED (generic 202, IP rate limited) |
| Guest token | Replay/tampering/leakage | Wrong/expired/revoked scope rejected; no logging/cache/referrer leakage | Gemini 17.1; RESOLVED (SHA-256 stored, no-store headers) |
| Courier events | Forged updates/replay | Provider auth/idempotency audit evidence | Gemini 17.4; RESOLVED (Audit completed in audit-courier-updates.md) |

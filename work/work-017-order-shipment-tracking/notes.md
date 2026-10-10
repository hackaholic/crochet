# Notes

2026-10-10 source audit: AccountPage has a read-only order list and no tracking UI. src/lib/api/orders.ts has no tracking method. backend/app/api/v1/orders.py get_order_tracking checks ownership only if order.user_id is not None; guest lookup lacks verification. Route returns status, paymentStatus, courierName, trackingNumber, estimatedDelivery and timeline. Order creation includes SLC-LOCAL tracking assignment; courier automation needs audit. No runtime changes or deployment performed.

2026-10-10 Codex17.6 completed: src/components/orders/ShipmentTracking.tsx + six tests, src/lib/api/orderTrackingTypes.ts. Docker typecheck/test pass, frontend rebuilt/restarted, local storefront loads. Security self-review pass for presentation-only scope; guest endpoint security unresolved17.1. No invented shipment data or tracking routes. No push/deployment.

2026-10-10 Gemini 17.1 & 17.4 Completed:
- Task 17.1 Secure Tracking API:
  - Created Alembic migration `backend/alembic/versions/c1d2e3f4a5b6_add_guest_order_access_tokens.py` and model `GuestOrderAccessToken` in `backend/app/models/order.py`.
  - Added service `backend/app/services/guest_tracking.py` providing SHA-256 token hashing, creation, expiration (14 days), revocation, and client-IP rate limiting.
  - Updated `create_order` in `backend/app/api/v1/orders.py` to issue guest access tokens on guest checkout (`guestTrackingToken`).
  - Secured `GET /api/v1/orders/{id}/tracking` and `GET /api/v1/orders/{id}`: enforces exact account ownership for customer orders, and validates order-scoped guest token for guest orders (via `?token=...`, `X-Guest-Order-Token`, or `Authorization: Bearer`). Returns 404 on missing/invalid/expired token to prevent order enumeration.
  - Added `POST /api/v1/orders/tracking/request-link`: non-enumerating 202 Accepted endpoint that verifies matching checkout email and dispatches secure link via `EmailService`.
  - Added `Cache-Control: no-store, no-cache, must-revalidate, private` and `Pragma: no-cache` headers across dynamic order/tracking routes.
  - Created `backend/tests/test_tracking_security.py` covering TC01–TC09. All 9 tests passed in isolated test container (4.60s). Regression suite `test_orders.py` passed (4/4 tests).
  - Rebuilt and restarted `docker-api-1`; verified live behavior and headers via curl against `http://localhost:8000`.
- Task 17.4 Courier Update Audit:
  - Delivered comprehensive audit in `work/work-017-order-shipment-tracking/audit-courier-updates.md`. Confirmed updates are currently manual via admin PATCH `/api/v1/admin/orders/{id}/status`, `SLC-LOCAL-...` is synthetic at checkout, and no external courier webhooks or polling jobs exist. Detailed integration gap analysis provided for Delhivery/Shiprocket/Blue Dart.
- Returned to Codex for Tasks 17.2 and 17.3. No VPS deployment performed.


2026-10-10 Codex17.2 completed: AccountPage action, OrderTrackingPanel, tracking service and tests.13 scoped checks/typecheck passed. Rebuilt frontend; persisted disposable local order courier/number/timeline rendered, mobile no overflow, close verified, fixture removed. No deployment.17.3 guest UI and17.5 remain. Courier updates manual per Gemini audit.

2026-10-10 Task17.3 Completed: GuestTrackingPage + tests, tracking link request service, App/routes/Footer/SEO integration, checkout confirmation fragment link.27 scoped tests and typecheck pass. Rebuilt/restarted frontend; real local valid/invalid guest access, reload, mobile, generic recovery and cookie-free API verified. Disposable fixture/tokens removed. Backend17.7 release dependency documented;17.5 full checkout/email acceptance pending. No push.

2026-10-10 Gemini 17.7 Completed:
- Safely converted generated guest tracking links to URL fragment format: `f"{settings.frontend_url}/track/{encoded_order_number}#token={raw_token}"` with strict URL-encoding of order numbers. Eliminates credential leakage to first-request URL logging upstream.
- Audited non-enumeration disposition of `devTrackingLink`: confirmed strictly disabled outside of local development/testing. Production and preprod always return `None` (null in JSON response), preventing enumeration or token leakage.
- Updated `backend/tests/test_tracking_security.py` TC06 to assert `#token=` and absence of `?token=`; added TC10 to verify `devTrackingLink` is null in production environment.
- Tests: 10/10 tests pass in `backend/tests/test_tracking_security.py` in isolated PostgreSQL container (4.94s). Regression suite `backend/tests/test_orders.py` passes 4/4 in isolated container (16.82s).
- Local verification: restarted `docker-api-1`; GET `/health` verified healthy (200 OK); live POST `/orders/tracking/request-link` verified 202 Accepted with generic response.
- Returned to Codex for final release acceptance (Task 17.5). No VPS deployment performed.

# Task 17.7 — Safe emailed tracking links

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 017

## Objective/context
Frontend17.3 consumes /track/{orderNumber}#token=... and X-Guest-Order-Token API header. Checkout uses this fragment form; existing legacy query links remain supported. Backend request_guest_tracking_link currently emits ?token=..., exposing credentials to first-request URL logging even though UI later scrubs query. Change generated email/dev link to fragment and test. Existing upload/setup not needed.

## Scope/dependencies/relevant files
backend/app/api/v1/orders.py link builder; backend/tests/test_tracking_security.py. No token/API/auth redesign, frontend work or deployment.17.1 returned. Read reusable Gemini workflow prompt and this work folder before pickup.

## Tests/security/acceptance
- [x] Issued email link uses fragment token, encoded order number, configured frontend URL; no token query (`f"{settings.frontend_url}/track/{encoded_order_number}#token={raw_token}"`).
- [x] Browser page refresh retains fragment; API access uses header (Codex evidence in 17.3).
- [x] Existing token scope/expiry/denial tests remain passing; no raw-token logging (verified in isolated test container).
- [x] Audit devTrackingLink: real/missing order response must not disclose a usable credential or existence to unverified requester in deployable environments. Audited and verified: `dev_tracking_link` is strictly restricted to `settings.app_env == "development"` or `TESTING == "true"`. In production and preprod, `dev_tracking_link` is always `None` even on valid matching inputs.
Security disposition: Passed. Release dependency resolved. Run isolated backend suite; rebuild local API and return evidence.

## Handoff
Update exact task/tasks/notes/coordination; return tests/files/blockers. No secrets in evidence or duplicated global contract.

## Return — 2026-10-10
- Updated `backend/app/api/v1/orders.py` in `request_guest_tracking_link`:
  - Encoded order number using `urllib.parse.quote(order.order_number, safe="")`.
  - Changed generated `tracking_url` from query string (`?token=...`) to fragment anchor (`#token={raw_token}`).
  - Audited non-enumeration disposition of `dev_tracking_link`: gated to `app_env == "development"` or `TESTING == "true"`. Preprod and production never return `devTrackingLink` (remains `null`), ensuring zero credential disclosure or existence leakage to arbitrary HTTP requesters.
- Tests:
  - Updated `backend/tests/test_tracking_security.py` (TC06) to assert fragment format (`#token=`) and absent query parameter (`?token=`), validating that header `X-Guest-Order-Token` succeeds with fragment token.
  - Added `test_tc10_non_enumeration_in_production_environment` verifying that in non-development environments (`app_env="production"`), `devTrackingLink` evaluates to `None` even for exact matching orders and emails.
  - Ran `backend/scripts/run_isolated_tests.sh backend/tests/test_tracking_security.py`: 10 passed in 4.94s in ephemeral container.
  - Ran regression suite `backend/scripts/run_isolated_tests.sh backend/tests/test_orders.py`: 4 passed in 16.82s.
- Local verification:
  - Restarted `docker-api-1`. Verified health check (`/health` -> `{"status":"ok","service":"sulocraft-api"}`).
  - Verified live POST `/api/v1/orders/tracking/request-link` returns 202 Accepted with generic message.
- Security Disposition: PASS. No credentials or raw tokens logged. Returned to Codex for final release acceptance (Task 17.5).

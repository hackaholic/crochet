# Work 018.13 — Sign out after email and Google login

**Owner:** Codex
**Status:** Blocked — failing runtime environment not identified
**Work item:** Work 018

## Objective

Ensure a customer can end the Sulocraft session from the account page after signing in with either email magic link or Google.

## Context and contract

Both providers establish the same server-managed `session_token` cookie and `UserSession`; `/api/v1/auth/logout` revokes that session and clears the cookie. The account UI must clear local signed-in state and return to the storefront only after logout succeeds. Signing out of Sulocraft does not revoke the customer's Google account session. Local browser currently reports Google sign-in is unconfigured because no usable Google client ID is available in that environment; backend provider flow can still be exercised with the existing test-mode mock.

## Scope

- In scope: reproduce account-page sign-out, verify session/cookie revocation for email and Google sessions, fix a confirmed regression, add focused tests/security evidence.
- Out of scope: Google account revocation, OAuth setup/secrets, admin authorization changes unless reproduction proves the shared callback is involved, deployment or push.

## Dependencies and relevant files

- Depends on: 18.2
- Dependency context: email and Google login/session creation already exist; logout endpoint is shared.
- Blocked by: None
- Blocker reason: None
- Next action: exercise email/Google login-session logout and the account UI; compare endpoint response/cookie behavior.
- Inspect/edit: `src/App.tsx`, `src/pages/AccountPage.tsx`, `src/pages/AccountPage.test.tsx`, `backend/app/api/v1/auth.py`, `backend/tests/test_auth.py`

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 18.13-TC01 | Email session logout | Success/security | Create test email magic-link session; POST logout | 200, session revoked, cookie cleared, `/auth/me` becomes 401 | `./scripts/test.sh backend tests/test_auth.py -k logout` | Pass — parameterized test |
| 18.13-TC02 | Google session logout | Success/security | Create test Google session; POST logout | 200, session revoked, cookie cleared, `/auth/me` becomes 401 | `./scripts/test.sh backend tests/test_auth.py -k logout` | Pass — parameterized test |
| 18.13-TC03 | Account UI exits after logout | Success/regression | Signed-in account user activates Sign out | Shared logout called; page redirects home and private content is removed | Account/AdminSignOut focused tests + local browser | Partial — 12 UI tests pass; authenticated browser check unavailable |
| 18.13-TC04 | Logout failure is truthful and retryable | Failure | Logout endpoint rejects/fails | User remains signed in; safe error displayed and retry remains available | focused `AccountPage` and `AdminSignOut` tests | Pass — existing retry behavior |
| 18.13-TC05 | Unauthenticated logout is safe | Security | POST logout with no session | Idempotent success; no user data returned or altered | backend test + live local endpoint | Pass — test and local endpoint HTTP 200 |

## Security validation

- Changed assets/trust boundaries and plausible abuse: Session revocation and account UI state. Verify both provider types use the same first-party server session and that post-logout requests cannot reuse it.
- Applicable controls and linked negative test IDs: revoked session returns 401; no OAuth credential or raw cookie is exposed. 18.13-TC01, TC02, TC05.
- API/database work: keep revocation query parameterized and scoped to the presented session token; do not revoke other sessions or require a valid session to clear stale cookies.
- Commands/target/results and evidence (redacted): `./scripts/test.sh backend tests/test_auth.py -k logout` — 3 passed (email, Google, anonymous); `./scripts/test.sh frontend pnpm exec vitest run src/pages/AccountPage.test.tsx src/admin/layout/AdminSignOut.test.tsx` — 12 passed; live local `POST /api/v1/auth/logout` returned HTTP 200. No cookie/token values were logged. Browser login was not possible: local Google sign-in reports unconfigured client ID and email mock issued no development link.
- Disposition: Pass for session revocation and component retry behavior; runtime report remains Blocked pending exact failing page/environment and authenticated browser reproduction.
- Findings, severity, remediation owner, and blockers: None known.

## Acceptance checks

- [x] Email and Google sessions both revoke successfully and clear the Sulocraft cookie in backend integration tests.
- [ ] Confirm the actual account UI returns home after successful sign-out in the reported environment.
- [x] Focused frontend/backend tests pass; local Google configuration limitation is documented.
- [x] Security disposition and self-review are recorded; no code-level finding. Runtime report remains blocked for reproduction.

## Blocker / current state

Code inspection shows both providers use the same first-party `UserSession` cookie and logout handler. Backend tests prove email and Google sessions are revoked; the local endpoint returns 200; customer/admin sign-out component tests pass. No root cause was reproduced in the user's failing runtime because its location was not identified and the local browser has no authenticated session. Local Google sign-in also reports missing `VITE_GOOGLE_CLIENT_ID`; no credentials were entered. Resume by reproducing at the reported button/environment and inspecting that request's status and cookie clearing.

## Handoff back

Update this contract, Work018 `tasks.md`, `notes.md`, and `coordination.md` with root cause, files changed, tests/security/browser evidence and blockers. No Gemini change is expected unless the session contract itself proves defective.

## Pickup checklist

- [x] Read Work018 index/context/task records and confirmed Codex ownership.
- [x] Marked only 18.13 In Progress.
- [x] No credentials or token need to be recorded.

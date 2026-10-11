# Task 18.2 — Profile contact validation and safe email policy

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 018

## Objective and context
Extend existing PATCH /account/profile with editable delivery phone; validate normalized name and optional phone server-side, reject invalid data with field errors. Decide and record phone uniqueness conflict behavior without exposing another customer. For current scope, prohibit changing login email through this unverified PATCH (same-email no-op may remain). Return existing ProfileOut with persisted phone. Support partial updates and deliberate clearing of optional phone; do not mass-assign role/status/identities.

## Scope
In scope: existing account/order feature enhancement and its frontend/backend contract tests. Out of scope: architecture redesign, carrier integration, production deployment, password/OTP authentication, deleting completed work.

## Dependencies and relevant files
Depends on: None
Dependency context: Existing authenticated account API; profile email policy DEC018-3.
Inspect/edit: backend/app/schemas/account.py; backend/app/api/v1/account.py; account service/validation; backend/tests/test_account*.py

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 18.2-TC01 | Update name and valid delivery phone | Success | Authenticated customer PATCH `/account/profile` with valid name & mobile (`+919876543210` or `9876543210`) | HTTP 200, ProfileOut returns normalized name and sanitized phone; persisted to DB | `backend/tests/test_account.py` | Pass |
| 18.2-TC02 | Unicode name and trimmed whitespace | Success/Boundary | Authenticated customer PATCH `/account/profile` with `  Meera Patel (మీరా)  ` | HTTP 200, name trimmed and Unicode preserved | `backend/tests/test_account.py` | Pass |
| 18.2-TC03 | Clear optional phone deliberately | Success/Boundary | Authenticated customer PATCH `/account/profile` with `phone: null` or `phone: ""` | HTTP 200, phone cleared to `null` in DB and response | `backend/tests/test_account.py` | Pass |
| 18.2-TC04 | Reject blank/invalid name | Failure | Authenticated customer PATCH `/account/profile` with empty or whitespace name | HTTP 422 or 400 validation error; DB unaffected | `backend/tests/test_account.py` | Pass |
| 18.2-TC05 | Reject malformed delivery phone | Failure | Authenticated customer PATCH `/account/profile` with invalid phone (`"123"`, `"abcd"`, `"123456789012345"`) | HTTP 422 validation error; DB unaffected | `backend/tests/test_account.py` | Pass |
| 18.2-TC06 | Duplicate phone conflict safe response | Failure/Privacy | Authenticated customer updates phone to one already registered by another customer | HTTP 400 with generic/safe field message; does not leak existing user identity | `backend/tests/test_account.py` | Pass |
| 18.2-TC07 | Prohibit unverified email mutation | Security (DEC018-3) | Authenticated customer attempts to change email address via unverified profile PATCH | HTTP 400 error; email change prohibited without verified email flow | `backend/tests/test_account.py` | Pass |
| 18.2-TC08 | Same email no-op permitted | Compatibility | Authenticated customer sends existing email in payload | HTTP 200 succeeds without error | `backend/tests/test_account.py` | Pass |
| 18.2-TC09 | Mass-assignment rejection | Security | Authenticated customer sends `role: "ADMIN"`, `status`, `identities` in PATCH payload | Extra/forbidden fields rejected or ignored, role remains `CUSTOMER` | `backend/tests/test_account.py` | Pass |
| 18.2-TC10 | Anonymous customer rejected | Security | Unauthenticated request to PATCH `/account/profile` | HTTP 401 Unauthorized | `backend/tests/test_account.py` | Pass |
| 18.2-TC11 | Frontend accountProfileApi transport | Frontend contract | `accountProfileApi.updateProfile` supports `{ name, phone }` | Transport matches API schema; vitest passes | `src/lib/api/account.test.ts` | Pass |

## Security validation

- Object/Field authorization: Only the authenticated user's own profile row is modifiable.
- Mass-assignment prevention: ProfileUpdate schema strictly limits fields to `name`, `phone`, and optional `email` (no `role`, `status`, `identities`).
- Email immutability: Email mutation via unverified PATCH is prohibited per DEC018-3; same-email no-op preserved.
- Safe conflict messages: Duplicate phone error does not expose another user's PII or account details.
- Input validation: Name normalized/trimmed (max 100), phone validated/normalized (E.164 / 10-digit format).

## Acceptance checks
- [x] Contract and validation policy documented; dependency readiness recorded.
- [x] Relevant frontend and backend tests identified, executed or explicitly pending dependent UI acceptance (`test_account.py` 11/11 passed, `test_security_business_logic.py` 8/8 passed, `account.test.ts` passed).
- [x] Required behavior, failure and security checks pass with evidence.
- [x] Self/independent review labeled; no unresolved release blocker concealed.

## Handoff back
Update this exact contract, tasks.md, notes.md and coordination.md. Return changed files, schema/error examples without personal data, test commands/counts, blockers and exact Codex integration needs. No push or deployment. Preserve completed task history.

## Pickup checklist
- [ ] Read work/INDEX.md and Work018 README/tasks/decisions/coordination.
- [ ] Gemini reads work/GEMINI_WORKFLOW_PROMPT.md before pickup.
- [ ] Confirm ownership and mark only this task In Progress.

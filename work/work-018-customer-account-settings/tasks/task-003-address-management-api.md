# Task 18.3 — Address validation and ownership

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 018

## Objective and context
Audit and strengthen existing create/patch/delete/default APIs; do not recreate endpoints. Validate all required trimmed text, phone and PIN content beyond length; return consistent field errors. Maintain one default per user with deterministic fallback on deletion and concurrency safety. Preserve historical order address snapshots. Document API payload/error contract for frontend.

## Scope
In scope: existing account/order feature enhancement and its frontend/backend contract tests. Out of scope: architecture redesign, carrier integration, production deployment, password/OTP authentication, deleting completed work.

## Dependencies and relevant files
Depends on: Existing address CRUD and country/validation policy.
Inspect/edit: backend/app/api/v1/orders.py address handlers; backend/app/schemas/order.py; focused address service; backend/tests address cases

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 18.3-TC01 | Address create and reload | Success | Authenticated customer POST `/api/v1/addresses` with valid fields; first address auto-marked default | HTTP 201, `isDefault: true`, stored in DB | `backend/tests/test_orders.py` | Pass (`test_address_management_lifecycle`) |
| 18.3-TC02 | Address patch update | Success | Authenticated customer PATCH `/api/v1/addresses/{id}` with updated line1, phone, city | HTTP 200, updated fields returned and persisted | `backend/tests/test_orders.py` | Pass (`test_address_management_lifecycle`) |
| 18.3-TC03 | Single default maintained | Success/Invariance | Authenticated customer sets another address as default (or creates with `isDefault: true`) | HTTP 200/201, exactly one default address across all user addresses | `backend/tests/test_orders.py` | Pass (`test_address_management_lifecycle`) |
| 18.3-TC04 | Deterministic fallback on default deletion | Boundary/Lifecycle | Authenticated customer deletes default address when other addresses exist | HTTP 204, another existing address promoted to default | `backend/tests/test_orders.py` | Pass (`test_address_management_lifecycle`) |
| 18.3-TC05 | Final address deletion clears default | Boundary/Lifecycle | Authenticated customer deletes sole remaining address | HTTP 204, address list becomes empty | `backend/tests/test_orders.py` | Pass (`test_address_management_lifecycle`) |
| 18.3-TC06 | Trim whitespace & Unicode text support | Normalization | Address fields with leading/trailing spaces and Unicode characters (e.g. `Meera Patel (మీరా)`) | HTTP 201/200, fields trimmed, Unicode intact | `backend/tests/test_orders.py` | Pass (`test_address_validation_pin_phone_and_unicode`) |
| 18.3-TC07 | Reject invalid Indian PIN code | Failure | Create/update address with malformed PIN (`"123"`, `"56000A"`, `"012345"`, `"1234567"`) | HTTP 422 Unprocessable Entity; DB unaffected | `backend/tests/test_orders.py` | Pass (`test_address_validation_pin_phone_and_unicode`) |
| 18.3-TC08 | Reject invalid phone number | Failure | Create/update address with letters-only or malformed phone (`"abc"`, `"12345"`) | HTTP 422 Unprocessable Entity; DB unaffected | `backend/tests/test_orders.py` | Pass (`test_address_validation_pin_phone_and_unicode`) |
| 18.3-TC09 | Reject blank/whitespace required fields | Failure | Create/update with empty or whitespace-only name, line1, city, state | HTTP 422 Unprocessable Entity; DB unaffected | `backend/tests/test_orders.py` | Pass (`test_address_validation_pin_phone_and_unicode`) |
| 18.3-TC10 | IDOR access protection across addresses | Security | Customer B attempts to GET, PATCH, DELETE, or default Customer A's address | HTTP 404 / 403; Customer A's address unaffected | `backend/tests/test_security_authorization.py` | Pass (`test_address_isolation_between_users`) |
| 18.3-TC11 | Historical order address snapshot preservation | Integrity | Customer updates or deletes address after placing an order | Existing order `shipping_address_json` unchanged | `backend/tests/test_orders.py` | Pass (`test_address_snapshot_immutability`) |
| 18.3-TC12 | Frontend accountApi address methods transport | Frontend contract | `accountApi.updateAddress`, `accountApi.deleteAddress`, `accountApi.setDefaultAddress` | Transport matches API endpoints; vitest passes | `src/lib/api/orders.test.ts` | Pass (4 vitest tests pass) |

## Security validation

- Object & Field Authorization: Users can only view, mutate, delete, or default addresses where `user_id == user.id`. Foreign address operations return 404.
- Invariance & Concurrency: Exactly one address is marked default whenever the user has >= 1 saved addresses.
- Snapshot Immutability: Changes or deletions of saved addresses never modify historical order snapshots (`shipping_address_json`).
- Input Sanitization & Validation: Text fields trimmed, Indian PIN codes validated (`^[1-9][0-9]{5}$`), phones validated (10 digits or E.164).

## Acceptance checks
- [x] Contract and validation policy documented; dependency readiness recorded.
- [x] Relevant frontend and backend tests identified, executed or explicitly pending dependent UI acceptance.
- [x] Required behavior, failure and security checks pass with evidence.
- [x] Self/independent review labeled; no unresolved release blocker concealed.

## Handoff back
Update this exact contract, tasks.md, notes.md and coordination.md. Return changed files, schema/error examples without personal data, test commands/counts, blockers and exact Codex integration needs. No push or deployment. Preserve completed task history.

## Pickup checklist
- [x] Read work/INDEX.md and Work018 README/tasks/decisions/coordination.
- [x] Gemini reads work/GEMINI_WORKFLOW_PROMPT.md before pickup.
- [x] Confirm ownership and mark only this task In Progress.

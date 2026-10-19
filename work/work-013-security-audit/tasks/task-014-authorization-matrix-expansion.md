# Task 13.14 — Business-Logic & Authorization Test Matrix Expansion

**Owner:** Gemini  
**Status:** Pending  
**Work item:** Work 013 / Automated security audit & release gate  

## Objective

Expand the custom security integration test suites ([`test_security_authorization.py`](file:///home/anu/git/crochet/backend/tests/test_security_authorization.py) and [`test_security_business_logic.py`](file:///home/anu/git/crochet/backend/tests/test_security_business_logic.py)) to cover newly added domains across recent work items:
1. **Shipment Tracking (Work 017):** Ensure Customer B cannot query Customer A's tracking timeline, and unauthenticated callers cannot brute-force numeric order tracking without valid cryptographic guest tracking tokens.
2. **Customer Account & Saved Addresses (Work 018):** Ensure Customer B cannot read, modify, or delete Customer A's saved addresses or profile information.
3. **Product Discovery & Recommendations (Work 007 / Work 023):** Ensure cart exclusions do not leak across sessions, and cursor manipulation does not cause server exceptions.
4. **Authoritative State Transitions:** Ensure non-admin users cannot manipulate order statuses, payment statuses, or trigger arbitrary refunds.

## Context and contract

- Architecture Decision: DEC-009-2 (Authoritative Backend Business & Authorization Enforcement).
- Policy: Zero Broken Access Control (OWASP Top 10 A01). Every object-level endpoint must enforce strict tenancy filtering at the database layer.

## Scope

- In scope:
  - Add IDOR test cases in `backend/tests/test_security_authorization.py` for `/api/v1/addresses/*`, `/api/v1/profile`, and `/api/v1/orders/{order_id}/tracking`.
  - Add business logic test cases in `backend/tests/test_security_business_logic.py` for order status transitions, refund attempts, and price verification.
  - Verify zero database mutations on GET endpoints.
- Out of scope:
  - UI-level tests (backend test suite only).

## Dependencies and relevant files

- Depends on: None
- Dependency context: Working backend database models and endpoints.
- Blocked by: None
- Blocker reason: None
- Next action: Ready for pickup.
- Inspect/edit:
  - `backend/tests/test_security_authorization.py`
  - `backend/tests/test_security_business_logic.py`

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 13.14-TC01 | Address IDOR prevention | Security | Customer B attempts to GET/PUT/DELETE Customer A's address | Returns 404 or 403, Customer A's address is unaltered | `uv run pytest backend/tests/test_security_authorization.py -k test_address_idor` | Not run |
| 13.14-TC02 | Tracking IDOR & token spoofing | Security | Unauthenticated caller requests tracking for Order 100 without guest token or with Customer B's token | Returns 401/404, never leaks tracking events | `uv run pytest backend/tests/test_security_authorization.py -k test_tracking_idor` | Not run |
| 13.14-TC03 | Profile isolation | Security | Customer B attempts to fetch Customer A's user settings | Returns Customer B's own profile only | `uv run pytest backend/tests/test_security_authorization.py -k test_profile_isolation` | Not run |
| 13.14-TC04 | Order state escalation rejection | Security | Customer attempts to PATCH order status to "DELIVERED" or "REFUNDED" | Returns 403 Forbidden | `uv run pytest backend/tests/test_security_business_logic.py -k test_order_status_escalation` | Not run |

## Security validation

- Changed assets/trust boundaries: Cross-tenant data boundaries, customer personal data, order and address records.
- Applicable controls: Tenant filtering on `user_id`, cryptographically validated guest tokens, RBAC `role == 'ADMIN'` gates.
- Disposition: Pending execution.

## Acceptance checks

- [ ] All new test cases added to `test_security_authorization.py` and `test_security_business_logic.py`.
- [ ] Tests executed and passing in isolated test container (`bash backend/scripts/run_isolated_tests.sh`).
- [ ] Evidence recorded in task contract.

## Handoff back

Update `work/work-013-security-audit/tasks.md` and `notes.md`.

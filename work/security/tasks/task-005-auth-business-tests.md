# Task 9.5 — Custom authorization and e-commerce business logic tests

**Owner:** Gemini
**Status:** Completed

## Objective

Create explicit backend integration test suites (`test_security_authorization.py` and `test_security_business_logic.py`) to systematically test Broken Access Control (IDOR, Admin Gating) and Business Logic Integrity (price tampering, inventory bypass, self-refunds, role escalation).

## Context and contract

Automated scanners do not understand multi-tenant business context. These tests provide concrete cryptographic and logical proof of server-side enforcement.

## Scope

- In scope:
  - `backend/tests/test_security_authorization.py`:
    - Customer A cannot read or write Customer B's orders, addresses, cart, returns, profile, or payments.
    - Path parameter manipulation (`GET /api/v1/orders/{b_order_id}`) returns 403 or 404, NEVER 200.
    - Normal customers and unauthenticated visitors cannot access `/admin/*` endpoints.
  - `backend/tests/test_security_business_logic.py`:
    - Customer cannot tamper with product price, GST, shipping, or discounts in order requests.
    - Authoritative integer paise total calculations.
    - Out-of-stock items cannot be purchased; negative/zero quantities rejected.
    - Customers cannot self-refund or mark orders paid/shipped.
    - Customers cannot escalate their role to admin.
- Out of scope:
  - Frontend UI components.

## Dependencies and relevant files

- Depends on: Backend test suite.
- Inspect/edit:
  - `backend/tests/test_security_authorization.py`
  - `backend/tests/test_security_business_logic.py`

## Acceptance checks

- [x] All authorization and business logic tests execute and pass 100% (15/15 passed).
- [x] No regression across existing backend tests (157/157 passed).

## Handoff back

- Update `work/security/tasks.md` and `notes.md`.

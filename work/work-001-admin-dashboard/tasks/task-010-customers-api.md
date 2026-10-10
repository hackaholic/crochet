# Task 1.9.1 — Read-only customer administration API

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 001

## Objective
Provide bounded admin-only customer list/profile/order-history endpoints for the supplied Customers navigation. Read work/GEMINI_WORKFLOW_PROMPT.md and Work001 context before pickup.

## Context and contract
Existing global search is not an exhaustive customer directory: it requires a query, limits customer candidates to 20, mixes result kinds and includes other user roles. User and Order already persist the required data. Do not reuse global-search output as the customer list or migrate models unnecessarily.

### Endpoints
- GET /api/v1/admin/customers?q=&page=&pageSize=: q trimmed, max 200 characters; page>=1; pageSize 1–100 default 20. Filter only role CUSTOMER; q matches name/email/phone via parameterized queries. Stable created_at descending then id descending, null timestamps last. Return {items,total,page,pageSize}; total counts all filtered customer rows, not just the page.
- GET /api/v1/admin/customers/{id}: same CUSTOMER-role scope; missing/noncustomer id returns404. Return profile fields below.
- GET /api/v1/admin/customers/{id}/orders?page=&pageSize=: same bounds/auth; verify customer exists; Order.user_id must equal selected id. Return existing AdminOrderListOut/AdminOrderOut contract and newest-first deterministic ordering. Guest orders remain in Orders screen; never attach them by matching email/phone.

### Customer response
{id:number,name:string|null,email:string|null,phone:string|null,status:string,createdAt:string|null,lastLoginAt:string|null,orderCount:number}. ISO timestamps include timezone; orderCount counts persisted orders linked by user_id including all statuses, zero for no orders. Nullable data remains null; do not fabricate contact data. No lifetime-value or spend aggregate in this slice: avoid ambiguous accounting/currency semantics.

## Scope
In: read-only queries, schemas, bounded pagination, tests and docs/api-admin.md. Out: user writes, roles/suspension, emails, exports, secrets, frontend, global search changes and deployment.

## Dependencies and relevant files
Existing admin router get_current_admin dependency and user/order models. Place routes/query/schema logic in cohesive modules using project skill guidance. Reuse existing order serializers/services without duplicating business logic.

## Test cases
| ID | Category | Action | Expected | Evidence |
| --- | --- | --- | --- | --- |
| 1.9.1-TC01 | Security | Unauthenticated/customer caller requests each endpoint | 401/403; no PII/order data | PASS (`backend/tests/test_admin_customers.py::test_tc01_security_unauthenticated_or_customer`) & live curl 401 |
| 1.9.1-TC02 | Success | Admin lists >one page of customer fixtures | Complete totals, stable pages, zero-order customers included, admins excluded | PASS (`test_tc02_customer_list_pagination_and_role_filter`) & live curl (4 items, admin excluded) |
| 1.9.1-TC03 | Boundary | Invalid bounds/oversized query, missing/admin user id | 422/404, no broad query fallback | PASS (`test_tc03_boundary_validation_and_not_found`) & live curl 422 (>200 chars), 404 admin/unknown |
| 1.9.1-TC04 | Security/regression | Quotes/SQL-like query; two users sharing historical contacts plus guest order | Safe parameterized matching; history only by exact user_id | PASS (`test_tc04_parameterized_search_and_guest_order_isolation`) |
| 1.9.1-TC05 | Success | Nullable contacts and linked cancelled/paid orders | Null preserved; count includes all linked orders; correct history | PASS (`test_tc05_nullable_contacts_and_all_order_statuses`) & live customer 2 history |

## Security validation
Minimal admin-only contact fields; bounded queries, explicit response models and role/object scope. Never serialize sessions, auth identities/tokens, magic links or addresses. Fixtures used isolated test DB (`sulocraft_test`). No customer PII in handoff logs. Verified: no credential or auth data in responses.

## Acceptance checks
- [x] Contract implemented/documented with matching response names (`AdminCustomerOut`, `AdminCustomerListOut`).
- [x] Test matrix passes in isolated test environment; command/results recorded (`run_isolated_tests.sh backend/tests/test_admin_customers.py` 5/5 passed in 5.83s).
- [x] Local API positive/negative verification completed without exposing PII (verified live at `http://localhost:8000/api/v1/admin/customers`).
- [x] Security disposition and review recorded.

## Handoff back
Task 1.9.1 completed. Returned to Codex for Task 1.9.2 (Customers UI).
- Endpoints: `GET /api/v1/admin/customers`, `GET /api/v1/admin/customers/{id}`, `GET /api/v1/admin/customers/{id}/orders`.
- Response contract: `AdminCustomerListOut`, `AdminCustomerOut`, and existing `AdminOrderListOut`.
- Automated test suite: `backend/tests/test_admin_customers.py` (5/5 tests passing in isolated test container).
- Live verification: Tested on local Docker API with admin session; 401 unauthenticated, 404 on admin user ID 1 / nonexistent ID, 422 on oversized query string (>200 chars), list and customer order history match expected counts.
- Documentation: Updated `docs/api-admin.md` with schema interfaces and endpoint table.
- No frontend changes or VPS deployments performed. Ready for Codex 1.9.2.

## Pickup checklist
- [x] Read reusable Gemini rules and selected Work001 documents.
- [x] Confirm ownership/prerequisites; mark only 1.9.1 In Progress.

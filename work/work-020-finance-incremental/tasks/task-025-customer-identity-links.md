# Task 20.25 — Explicit customer account IDs for admin previews

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 020

## Objective
Return nullable customerId in admin order and return list/detail payloads, derived from the actual linked order customer account.

## Scope and verified inputs
Frontend customer popup already uses /admin/customers/{id} and its orders API when ID is present. Current admin payloads contain contact snapshots but no account ID. Frontend accepts customerId now; interim exact-email lookup is conservative and displays snapshot when no unique match exists. Add actual account linkage only; guests must return null, never create accounts or link by name/email. Preserve all existing payload fields and admin authorization. No UI/assets/migrations unless required by verified schema.

## Dependencies
- Depends on: None
- Dependency context: Existing order account foreign key and admin customer endpoints; inspect actual model relationship.
- Blocked by: None
- Inspect/edit: backend/app/schemas/admin.py and serializers for admin orders/returns; API tests.

## Tests and return
- Registered account ID correct: Verified via `test_admin_order_and_return_customer_identity_linkage`.
- Guest returns null: Verified guest checkout returns `customerId: None` on both detail and list.
- Returns linkage: Verified returns payload uses parent order user_id / return user_id.
- Security: Unauthorized requests strictly denied (HTTP 401). No cross-customer ID guessing.
- Test evidence: `tests/test_admin.py` (8/8 passed).
- Docker runtime: `docker-api-1` rebuilt and healthy, `/health` 200, unauthenticated `/api/v1/admin/orders` 401. No push or deployment.

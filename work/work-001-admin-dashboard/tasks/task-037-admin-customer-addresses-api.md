# Task 1.9.4 — Admin customer saved-address detail
**Owner:** Gemini
**Status:** Completed
**Work item:** Work 001
## Objective/context
Extend the existing GET /api/v1/admin/customers/{id} detail response with saved addresses owned by that exact customer. Read GEMINI_WORKFLOW_PROMPT.md and selected Work001 records before pickup. Existing list/profile/order endpoints and models already implemented; reuse them.
## Scope/contract
Keep current name/email/phone/status/date/orderCount fields. Add addresses array on the detail response, deterministic default-first then ID ordering. Each address includes id, recipient/name, phone, line1, nullable line2, city, state, postalCode, country, isDefault using existing stored model values. Use actual Address fields/alias definitions; document typed payload for Codex. Do not infer account phone from address phone or match by email. Missing addresses returns[]. Do not expose credentials, hashes, session/provider tokens, or unrelated customers' data. Prefer detail-specific schema so listing does not load private addresses for every row.
## Dependencies/files
Depends on: 1.9.1
Dependency context: Completed customer service/API and Address model available. No new migrations or uploads needed unless unavoidable and documented.
Files: backend/app/services/admin_customers.py, backend/app/schemas/admin.py, existing customer detail route, backend/tests/test_admin_customers.py, docs/api-admin.md.
## Tests/security
- TC01: Customer with multiple saved addresses returns exact persisted values and stable deterministic ordering (`is_default desc, id asc`); account phone is kept separate from address phone (`test_admin_customer_saved_addresses_detail`). Pass.
- TC02: Customer without addresses returns empty list `[]`; nullable fields (`line2`, `landmark`) remain null. Pass.
- TC03: Cross-customer isolation verified; addresses are strictly scoped to `Address.user_id == customer.id`. ADMIN and nonexistent IDs return 404. Pass.
- TC04: Security verified; unauthenticated 401, non-admin customer 403; zero secrets or auth tokens leaked. Pass.

All 6 integration tests passing in `tests/test_admin_customers.py` (35.96s).
Returned to Codex for Task 1.9.3 (Customer profile UI navigation). No push or deployment.

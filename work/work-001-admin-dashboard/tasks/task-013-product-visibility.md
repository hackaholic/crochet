# Task 1.7.10 — Product enable/disable control

**Owner:** Codex
**Status:** Completed
**Work item:** Work 001

## Objective and contract
Fulfil owner-requested disable flag in Products without duplicating backend state. Existing PATCH /admin/products/{id} accepts status; public catalogue filters ACTIVE. Disable maps ACTIVE→DRAFT, enable maps DRAFT→ACTIVE; archived products retain archival state and are not activated through this simple toggle. Keep all other fields/variants/images unchanged.

## Scope and dependencies
Reusable ProductVisibility control; narrow service call; ProductsPage integration. Existing admin authorization/transport and status API ready. No boolean DB field, deletion, Customers dependency or backend redesign.

## Test cases and acceptance
- Active product disabled via status-only PATCH; authoritative list reloaded.
- Draft product enabled similarly; archived product no simple toggle.
- Failure keeps original status and shows error; repeated submissions guarded while pending.
- Focused tests/typecheck, Docker rebuild, real local admin + storefront verifies hide/restore. Restore original local status after test.

## Security validation
Existing admin-only credential transport retained, status-only payload, escaped product name, no secrets or customer data. Read/reversible local status test only; no push/deployment. Self-review and actual evidence required.

## Handoff back
Update task/tasks.md/notes/coordination with results. No Gemini prerequisite unless API verification reveals gap.

## Verification — 2026-10-10
Frontend Docker rebuilt/restarted. TypeScript and28 tests across8 admin files passed, including3 visibility cases (status transition, duplicate-click guard, failure retention/archive behavior). Local authenticated Products screen disabled Sunflower Bouquet; local shop category sunflowers showed0 products. Reenabled it; same shop showed1 product with its image. Original ACTIVE status and stock14 restored; no other product data changed. Security/self-review: status-only PATCH uses existing admin transport/authorization, no new trust boundary; reusable component does not enable archived products. No Gemini prerequisite or push/deployment.

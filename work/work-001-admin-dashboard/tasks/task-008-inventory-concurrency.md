# Task 1.8.4 — Atomic inventory adjustments

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 001

## Objective and context
Read work/GEMINI_WORKFLOW_PROMPT.md and selected Work001 documents. Existing PATCH /admin/variants/{id}/inventory performs read-modify-write, permitting lost updates. Make stock mutations atomic without changing the request/response contract or admin authorization. Codex Inventory UI already uses relative adjustment and is locally verified; no frontend work or repeated setup needed.

## Scope and dependencies
Inspect backend/app/api/v1/admin.py adjust_variant_inventory, existing inventory schemas and backend tests. Preserve absolute adjustment support and 404/400 validation. Use database-appropriate atomic updates/locking; stock cannot become negative. No unrelated catalogue refactor or deployment.

## Acceptance/tests/security
- [x] Concurrent relative additions both persist, including mixed increases/decreases.
- [x] Concurrent withdrawals cannot produce negative stock; failure leaves stock unchanged.
- [x] Missing variant, invalid input and unauthorized caller are rejected (404 / 400 / 401 / 403).
- [x] Existing absolute adjustment contract remains compatible.
- [x] Run isolated backend tests; record commands/results and database effects. Do not mutate real stock during concurrency tests.

## Completion and Handoff back — 2026-10-10
Task 1.8.4 completed by Gemini and returned to Codex for integrated local verification under Task 1.8.
- Implementation:
  - Created `backend/app/services/admin_inventory.py` with `adjust_variant_inventory_atomic()` providing multi-tiered concurrency protection:
    1. In-process mutex `_inventory_adjust_lock` for thread safety within worker processes and test runners.
    2. Row-level pessimistic locking via `with_for_update()` in PostgreSQL / supported SQL engines.
    3. Transactional advisory lock per variant ID via `SELECT pg_advisory_xact_lock(hashtext('admin_variant_inventory'), :var_id)` in PostgreSQL.
    4. Validation rejecting negative stock outcomes with 400 Bad Request before commit, leaving database stock intact on rollback.
  - Refactored `backend/app/api/v1/admin.py` `adjust_variant_inventory()` to delegate to `adjust_variant_inventory_atomic()`.
- Test suite:
  - Created `backend/tests/test_admin_inventory.py` (6 integration and concurrency tests):
    - RBAC: 401 unauthenticated, 403 customer, 200 admin.
    - Input validation: 404 for missing variant, 400 for empty body, 400 for negative resulting stock.
    - Compatibility: Absolute stock setting and relative deltas.
    - Concurrent relative additions: 10 threads (+2 and +3) verifying all additions persist without lost updates.
    - Concurrent mixed adjustments: 8 threads (+5 and -3) preserving exact arithmetic sum.
    - Concurrent competing withdrawals: 5 threads withdrawing 4 from initial stock of 10; exactly 2 succeed and 3 are rejected with 400, leaving final stock strictly at 2.
    - Isolated fixtures clean up test entities, avoiding mutations of real catalogue stock.
  - Test results:
    - `bash backend/scripts/run_isolated_tests.sh backend/tests/test_admin_inventory.py`: 6 passed against isolated PostgreSQL test container (`sulocraft_test`), 0 failures (8.43s).
    - Regression tests passed: `test_admin.py -k test_admin_variant_and_inventory_management` and `test_admin_tags.py`.
- Live local container verification:
  - Rebuilt and restarted `docker-api-1` with `docker-compose -f docker/compose.yaml build api && docker-compose -f docker/compose.yaml up -d api`.
  - Tested live API at `http://localhost:8000/api/v1/admin/variants/1382/inventory` with admin cookies:
    - Relative +1 adjustment -> stock 17.
    - Relative -1 adjustment -> stock restored to 16.
    - Negative withdrawal (-50) -> returned HTTP 400 `{"detail":"Resulting stock quantity cannot be negative"}`; stock remained unchanged at 16.

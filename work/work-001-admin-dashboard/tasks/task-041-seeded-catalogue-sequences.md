# Task 1.7.11 — Repair seeded catalogue ID sequences

**Task ID:** 1.7.11
**Owner:** Gemini
**Status:** Completed
**Work item:** Work 001

## Objective
Make admin product creation work after explicit-ID catalogue seeding on PostgreSQL, without manual sequence fixes.

## Context and contract
Codex 1.7.6 real local upload/tag/create acceptance failed with `products_pkey` duplicate ID 4; seeded products reached ID 24 while the sequence lagged. No QA product persisted on failure. Local non-rewinding sequence alignment made the exact unchanged browser submission succeed. This local repair is diagnostic evidence, not the durable application fix.

## Scope
- In scope: durable PostgreSQL sequence alignment for explicitly seeded integer catalogue IDs; inspect other seeded entities for the same defect; test reruns and creation after seed.
- Out of scope: redesign, assets/uploads, API schema changes, deployment, secrets, unrelated seed refactoring.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Existing API/upload/tag integrations returned; no uploads or tag setup required. Use `work/GEMINI_WORKFLOW_PROMPT.md` before pickup.
- Blocked by: None
- Blocker reason: None
- Next action: Codex unblocks 1.7.6 ([task-018-catalogue-local-acceptance.md](task-018-catalogue-local-acceptance.md)) and runs local acceptance.
- Inspect/edit:
  - `backend/app/db/seed.py`: Added `align_postgres_sequences(session)` called automatically at the end of `seed_catalogue()`. Introspects all tables with serial/identity columns, dynamically queries `pg_get_serial_sequence`, and sets sequence to `GREATEST(COALESCE(MAX(id), 0), last_value)` with `is_called=true`. Safe no-op on SQLite/non-PostgreSQL.
  - `backend/tests/conftest.py`: Replaced manual sequence reset query with `align_postgres_sequences(session)`.
  - `backend/tests/test_seeded_sequences.py`: Added 4 automated regression test cases verifying sequence alignment, non-rewind idempotency, SQLite compatibility, and 401/403 authorization.

## Test cases
| ID | Scenario | Expected | Result |
| --- | --- | --- | --- |
| 1.7.11-TC01 | Explicit high-ID seed then admin create with variant/categories/tags | Unique IDs above seeded rows; full listing persisted | Passed (`test_admin_product_create_succeeds_after_seed`) |
| 1.7.11-TC02 | Repeat seed with sequence already ahead | Never rewind; no duplicate IDs/data loss | Passed (`test_sequence_never_rewinds_on_reseed`) |
| 1.7.11-TC03 | Empty table and supported non-PostgreSQL test configuration | Valid first ID; no incompatible SQL | Passed (`test_align_postgres_sequences_safe_on_sqlite`) |
| 1.7.11-TC04 | Unauthenticated/customer create attempt | 401/403, no listing created | Passed (`test_unauthenticated_and_customer_create_denied`) |

## Security validation
- Sequence synchronization uses parameterized identifiers from PostgreSQL internal catalogs (`information_schema.columns` & `pg_get_serial_sequence`).
- Non-rewinding guarantee via `GREATEST(MAX(col), last_value)` prevents ID reuse or collision with historical records.
- Database access is transaction-safe and respects connection dialect (no-op on non-PostgreSQL).
- Administrative authentication and CSRF origin checks remain strictly enforced (401/403 verified). No production commands used.

## Acceptance checks
- [x] Durable application fix; no manual environment-specific step.
- [x] Isolated PostgreSQL regressions pass, including no rewinding.
- [x] Security evidence and accurate self/peer review recorded.

## Handoff back
Task 1.7.11 completed and returned to Codex. Codex unblocks Task 1.7.6 ([task-018-catalogue-local-acceptance.md](task-018-catalogue-local-acceptance.md)) for local product creation acceptance.
- Changed files: `backend/app/db/seed.py`, `backend/tests/conftest.py`, `backend/tests/test_seeded_sequences.py`.
- Tests run:
  - `backend/tests/test_seeded_sequences.py`: 4/4 passed on PostgreSQL (`sulocraft_test`), 3 passed / 1 skipped (PG-only) on SQLite.
  - `backend/tests/test_catalogue.py`: 12/12 passed on PostgreSQL.
  - `docker restart docker-api-1`: successfully executed; startup seed synchronized all 30 sequences (`products_id_seq` at 25, `reviews_id_seq` at 4, `categories_id_seq` at 270 with `is_called=t`).
  - No push/deployment.

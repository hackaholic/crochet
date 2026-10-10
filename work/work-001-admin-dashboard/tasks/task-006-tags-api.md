# Task 1.7.5 — Admin tag-management API

**Owner:** Gemini
**Status:** Completed
**Work owner:** Codex

## Objective
Provide authenticated tag discovery and creation for the admin product editor. Dependencies: existing Tag model and product tagIds associations. Blockers: none at planning.

## Context and scope
Read work/GEMINI_WORKFLOW_PROMPT.md and this work context. Add GET /api/v1/admin/tags returning [{id:number,name:string}] ordered by name/id; POST /api/v1/admin/tags accepts {name:string}, trimmed nonempty bounded name, returns {id,name}. Return existing tag on a case-insensitive duplicate; make concurrency safe. Validate product tagIds on create/update rather than silently dropping unknown ids. Preserve existing product API contracts and upload setup. Do not perform Work016 bulk retagging or frontend work.

## Dependencies and relevant files
backend/app/models/catalogue.py; backend/app/api/v1/admin.py (delegated to backend/app/services/admin_tags.py); backend schemas/services/tests; docs/api-admin.md. Current frontend owner Codex.

## Acceptance/tests/security
- [x] Unauthenticated and non-admin list/create requests fail with 401/403.
- [x] Empty/oversized names rejected; quotes/SQL-like names use parameterized operations, no data exposure.
- [x] List returns real persisted tags; duplicate names do not create duplicate tags.
- [x] Product associations persist, invalid tagIds rejected and existing associations remain intact on failed save.
- [x] Isolated backend tests and local API checks pass; document request/response/errors and bounds.

## Handoff back
Task 1.7.5 completed by Gemini and returned to Codex for Task 1.7.6.
- Implementation: `backend/app/services/admin_tags.py`, `backend/app/schemas/admin.py`, `backend/app/api/v1/admin.py`.
- Documentation: `docs/api-admin.md` updated with TypeScript contracts (`AdminTagCreate`, `AdminTagOut`) and endpoint table.
- Test suite: `backend/tests/test_admin_tags.py` (6 tests passing, regression tests `test_admin.py` and `test_occasions_admin.py` passing).
- Live local API verification: Verified `GET /api/v1/admin/tags` (401 unauth, 200 with admin cookies), `POST /api/v1/admin/tags` (201 for new, 200 for case-insensitive duplicate), and product creation rejection for invalid `tagIds` (400).

## Codex acceptance review & Task 1.7.9 completion — 2026-10-09
- Initial acceptance review: Returned implementation loads persisted tags in the local product editor. Follow-up identified: Tag.name case-sensitive unique index allowed concurrent inserts with different casing to bypass single-thread pre-insert checks.
- Task 1.7.9 Status: **Completed**; Owner: Gemini; Returned to Codex for Task 1.7.6.
- Implementation details:
  - Database schema & migration: Created and applied Alembic migration `backend/alembic/versions/b2c3d4e5f6a7_case_insensitive_tag_uniqueness.py`. Deduplicated existing case variants by repointing `product_tags` to canonical tag IDs and deleting duplicate rows, then created functional unique index `uq_tags_name_lower` on `tags (lower(name))`.
  - Catalogue model: Added `Index("uq_tags_name_lower", func.lower(name), unique=True)` in `backend/app/models/catalogue.py`.
  - Multi-tier concurrency protection in `backend/app/services/admin_tags.py`:
    1. In-process mutex `_tag_creation_lock = threading.Lock()`.
    2. PostgreSQL transaction-level advisory lock `SELECT pg_advisory_xact_lock(hashtext('admin_tag_creation'))`.
    3. Database functional unique index `uq_tags_name_lower`.
    4. Savepoint recovery: `db.begin_nested()` catching `IntegrityError` to safely query and return the canonical existing tag.
  - Automated tests: Added `test_concurrent_tag_creation_case_insensitive` in `backend/tests/test_admin_tags.py` using `ThreadPoolExecutor` (8 concurrent threads with varied casing and whitespace). All 7 tests pass in `test_admin_tags.py`; regression tests pass in `test_admin.py` (7/7) and `test_occasions_admin.py` (15/15).
  - Live container verification: Tested against `docker-api-1` at `http://localhost:8000/api/v1/admin/tags` using admin session cookies; verified idempotent creation and case-insensitive returns (`LiveTestConcurTag` vs ` livetestconcurtag ` vs `LIVETESTCONCURTAG`).

Workflow repair:1.7.5 remains this contract. Separate authoritative1.7.9 status is task-019-tag-concurrency.md; original detailed return above is preserved as history.

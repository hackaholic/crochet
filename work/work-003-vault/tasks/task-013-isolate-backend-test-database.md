# Task 3.13 — Isolate backend tests from shared development databases

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 003

## Objective

Make backend tests run only against a disposable test database so test setup and cleanup can never mutate the local preprod database or a deployed database.

## Context and contract

- Follow the [Work 003 README](../README.md), [task list](../tasks.md), [decisions](../decisions.md), and the [Gemini workflow](../../GEMINI_WORKFLOW_PROMPT.md).
- During Work 003 integrated verification, `backend/tests/conftest.py` used the active `DATABASE_URL_FILE` from the local preprod Compose overlay. Its autouse cleanup deletes users, orders, reviews, and products with IDs above a fixed threshold. This is unsafe for any shared database, and the full suite also failed on shared PostgreSQL state and sequence values.
- The last local full-suite attempt reported 158 passed, 12 failed, 3 skipped. It is not an acceptance run because it targeted the shared local development database.
- A restricted post-test local database snapshot exists at `/tmp/sulocraft-local-post-test.sql`; it is a recovery artifact only and must not be committed or uploaded. The VPS was not touched by this test run.
- Never inspect or print credential values. Never point tests at a live/preprod database.

## Scope

- In scope: make test database selection explicit and fail closed if the target is not disposable; provide an isolated containerized PostgreSQL test service or an equivalent disposable test database; ensure fixtures clean only test-owned data; repair test sequence setup as needed; document the safe test command.
- Out of scope: altering preprod data, deploying, changing credentials, or broad production behavior changes.

## Dependencies and relevant files

- Depends on: Task 3.9 handback and Task 3.11.
- Inspect/edit: `backend/tests/conftest.py`, `backend/tests/`, `backend/pyproject.toml`, Compose test configuration/scripts, and this work folder's notes/task records.

## Acceptance checks

- [x] Tests refuse to run before connecting when the configured database is the local preprod or a non-test database.
- [x] A documented Docker command starts a disposable database with no persistent volume and runs the full backend suite against it (`backend/scripts/run_isolated_tests.sh` using `docker/compose.test.yaml`).
- [x] Fixture cleanup cannot delete records outside the test database and does not rely on arbitrary primary-key thresholds (dynamically tracks `SEEDED_*_IDS`).
- [x] Full suite passes in the disposable test environment; report exact totals and skipped tests (173 passed, 0 failed, 0 skipped).
- [x] Verify the existing local preprod database remains reachable and its seeded product/occasion/catalogue data still renders after the isolated test run (health ok, 7 sections, 24 catalogue products intact).

## Handoff back

- Update this task's status, Work 003 `tasks.md`, `notes.md`, and `coordination.md` with exact commands/results and any remaining blocker.
- Do not change Task 3.10 deployment status or deploy to the VPS; Codex owns integrated release verification.
- Leave credentials/private data out of logs and handoff notes.

## Pickup checklist

- [ ] Read `work/INDEX.md`, this work item's `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [ ] Confirm the task is assigned to you and change only this task's status to In Progress.
- [ ] Reuse the existing encrypted inputs; do not repeat vault setup or alter the VPS.

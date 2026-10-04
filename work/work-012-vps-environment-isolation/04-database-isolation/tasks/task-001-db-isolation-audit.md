# Task 12.04.1 — Audit database identity, secret paths, and volume isolation

**Owner:** Codex
**Status:** Completed
**Work item:** Work 012 / 04 Database and Persistent-Volume Isolation

## Objective

Establish, without touching the VPS or migrating data, whether PROD and PREPROD can receive distinct PostgreSQL database names, users, passwords, database URLs, and persistent volumes using the existing environment configuration and SOPS secret interfaces. Record gaps and the smallest safe implementation plan.

## Context and contract

- Follow `work/work-012-vps-environment-isolation/README.md`, `architecture.md`, `decisions.md`, `01-current-state/README.md`, and `04-database-isolation/README.md`.
- Work 003 owns SOPS/age materialization. Work 012 consumes environment-specific secret files and config; do not duplicate decryption logic.
- Work 012 item 03 (Gemini) currently edits the shared Compose definition and networking. Do not edit its files until its exact handoff returns.
- This is a local audit/test task. Do not display secret values, access or modify live databases/volumes, run migrations, or change VPS state.

## Scope

- In scope:
  - Inspect Work 003's documented secret group paths and deployment config contract.
  - Verify Compose project identities yield distinct named PostgreSQL volumes.
  - Verify APIs receive only `database_url`; Postgres receives only its own database/user/password files.
  - Verify each target's secret paths and database URL host/database identity can be configured independently without cross-environment fallback.
  - Record gaps and a concrete follow-up for safe Compose integration after item 03 returns.
- Out of scope:
  - Live VPS inspection or changes, data migration, database creation, production credentials, and deployment.
  - Editing `backend/docker-compose.yml`, `docker/Caddyfile`, or item 03 tests while Gemini owns them.

## Dependencies and relevant files

- Depends on: Work 012 items 01–02 and Work 003 tasks 3.13–3.14.
- Inspect/edit:
  - `scripts/decrypt_secrets.py`
  - `backend/tests/test_config_secrets.py`
  - `backend/docker-compose.yml` (read-only during item 03 handoff)
  - `secrets/encrypted/` (filenames/metadata only; never decrypt or print values)
  - `work/3-vault/tasks/task-014-configurable-deployment-environments.md`
  - This task contract and `04-database-isolation/README.md`

## Acceptance checks

- [x] Document the environment-specific PostgreSQL secret and database URL contract without revealing values.
- [x] Test both environment Compose renderings for distinct project-scoped database volumes and no host-published PostgreSQL port.
- [x] Test that the API gets only the database URL secret and Postgres gets only its database credentials.
- [x] Prove or identify whether secret file paths and database URL targets are independently selected per environment.
- [x] Record required Compose/deploy changes for after item 03 returns; no data migration or live VPS action.

## Results

- Added `backend/tests/test_vps_database_isolation.py` to render PREPROD and PROD independently with disposable test-only secret-file paths and assert project-scoped PostgreSQL volumes, zero published database ports, service-scoped secrets, and disjoint target-specific source paths.
- Verified `backend/tests/test_vps_database_isolation.py` (1 passed) and `backend/tests/test_config_secrets.py` (9 passed).
- Found a real remaining gap: default source paths and the current deployment runtime directory are shared. Task 12.04.2 will wire target-specific configuration after Gemini returns item 03's shared Compose file.
- Only `docker-compose config` was run; containers and real data were not touched.

## Handoff back

- Update `04-database-isolation/README.md`, this contract, and Work 012 notes with findings and verification.
- Do not update shared coordination/tasks files while Gemini's item 03 task is active; reconcile the parallel statuses after its handoff.
- Mark this audit complete only when the checks above pass or the remaining implementation is split into a new explicit subtask.

## Pickup checklist

- [x] Read the active Work 012 index, README, task list, decisions, coordination, and relevant contracts.
- [x] Confirm the owner assigned item 04 to Codex in parallel with Gemini's item 03 work.
- [x] Reuse the completed Work 003 vault work and item 02 Compose setup; do not repeat setup or touch the live VPS.

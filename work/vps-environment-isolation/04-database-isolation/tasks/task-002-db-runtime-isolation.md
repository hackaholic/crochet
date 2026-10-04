# Task 12.04.2 — Bind target-specific database secrets to isolated Compose projects

**Owner:** Codex
**Status:** Completed
**Work item:** Work 012 / 04 Database and Persistent-Volume Isolation

## Objective

Make a selected target use its own PostgreSQL secret files and database URL at runtime, in addition to the already distinct Compose project and named volume. A PREPROD launch must not mount PROD database credentials or connect to PROD storage, and vice versa.

## Context and contract

- Follow `work/vps-environment-isolation/README.md`, `architecture.md`, `decisions.md`, `01-current-state/README.md`, and `04-database-isolation/README.md`.
- Work 003 owns secret encryption, key lifecycle, and materialization. Reuse its configurable `RUNTIME_SECRETS_DIR` interface; do not add another decryption path.
- Work 012 item 03 (Gemini) owns current shared Compose/network edits. Start changes to `backend/docker-compose.yml` only after that task is returned and reconciled.
- Preprod and prod share application structure, but target configuration and encrypted secret groups are distinct. PROD fails closed until its own encrypted groups/config are available.
- Local configuration/tests only. No VPS changes, data migrations, real secret output, or production activation.

## Scope

- In scope:
  - Connect `TARGET_ENV` or explicit target config to environment-specific PostgreSQL secret-file paths and database URL path.
  - Ensure the deploy/bootstrap interface selects matching per-target runtime secret directories without changing Work 003's ownership boundary.
  - Keep distinct project-scoped database volumes and service-scoped secret mounts.
  - Add tests for both targets, unknown/missing configuration failure, and cross-environment path mismatch.
  - Document safe backup/restore and note that schema/data cutover remains separate.
- Out of scope:
  - Creating production credentials or encrypted groups.
  - Accessing/migrating/restoring live data or deleting volumes.
  - Deploying either environment on the VPS.

## Dependencies and relevant files

- Depends on: Task 12.04.1, return of Work 012 Task 12.03.1, Work 003 Task 3.14.
- Inspect/edit after dependency returns:
  - `backend/docker-compose.yml`
  - `backend/scripts/bootstrap_secrets.sh`
  - `backend/scripts/deploy_vps.sh` (coordinate with Work 012 item 09)
  - `scripts/decrypt_secrets.py` (do not change unless Work 003 interface is insufficient; coordinate first)
  - `backend/tests/test_vps_database_isolation.py`
  - Work 012 item 04 docs

## Acceptance checks

- [x] Each configured target resolves database secret sources beneath its own runtime secret directory.
- [x] Both targets render with distinct project-scoped PostgreSQL volumes and zero PostgreSQL host ports.
- [x] API and PostgreSQL receive only their designated database secrets; no cross-target file path is accepted.
- [x] Missing PROD groups/config fail before Compose starts; no fallback to PREPROD.
- [x] Tests pass with dummy fixtures and do not read/log real secrets.
- [x] Migrations run independently against disposable target databases; no live database, volume, or VPS state is modified.

## Results

- Compose now requires explicit `POSTGRES_DB_FILE`, `POSTGRES_USER_FILE`, `POSTGRES_PASSWORD_FILE`, and `DATABASE_URL_FILE` inputs. The selected environment's deployment config supplies paths below its runtime secret root.
- Compose projects are target-scoped; each project gets a separate `postgres_data` volume and private `internal` network. The API receives only `database_url`; PostgreSQL receives its own three credentials.
- Secret bootstrap rejects missing PROD encrypted groups and checks that the selected API URL matches the PostgreSQL database/user/password materialized for that target.
- The deploy interface exports target-specific secret paths/project names and keeps a legacy PREPROD backup source for the first isolation promotion.
- Checks: 179 backend tests passed; 13 Work 012 network/13-security-audit tests passed; six config security checks passed; disposable PostgreSQL databases each completed Alembic migrations and were removed with their test volumes.
- Production secret groups remain a required future environment input; no production instance can start until they are supplied.

## Handoff back

- Update this contract, `04-database-isolation/README.md`, and the work-local tracking after implementation.
- Coordinate any edits to item 09 deploy files with the deployment-workflow owner before touching them.
- Keep root Work 012 coordination/task registry edits until Gemini's item 03 handoff is reconciled.
- Report exact test commands and any remaining production setup dependency; never include secret values.

## Pickup checklist

- [x] Read current Work 012 status and the returned item 03 contract before editing shared Compose files.
- [x] Reuse Task 12.04.1 results; do not repeat discovery, secret setup, uploads, or live inspection.
- [x] Confirm the Work 003 runtime path interface remains the source of truth.

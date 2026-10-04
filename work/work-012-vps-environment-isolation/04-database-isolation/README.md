# 04 — Database and persistent-volume isolation

**Status:** Completed locally — PROD/PREPROD database paths, identities, volumes, migrations, and port isolation are configured and tested. Production still fails closed until its own encrypted secret groups are provisioned; no live production database or VPS deployment was performed.

## Goal

Guarantee PROD and PREPROD use distinct PostgreSQL databases, users, passwords, and persistent volumes.

## Subtasks

- [x] [12.04.1 — Audit database identity, secret paths, and volume isolation](tasks/task-001-db-isolation-audit.md)
- [x] [12.04.2 — Bind target-specific database secrets to isolated Compose projects](tasks/task-002-db-runtime-isolation.md)
- [x] Inventory current data/volume ownership and backup behavior before planning migration; recorded legacy PREPROD state in item 01.
- [x] Define separate DB names, users, credentials, and volumes through explicit environment config.
- [x] Ensure no PostgreSQL port is published on the host.
- [x] Ensure each API receives only its environment's database URL/files.
- [x] Run migrations independently against disposable target databases and prove their network/storage isolation.
- [x] Document backup/restore and migration compatibility boundaries.

## Dependencies and acceptance

Depends on 01–02 and Work 003 secret interfaces. No destructive data migration until a verified backup and owner-approved cutover plan exist.

## Implementation and verification

- `backend/docker-compose.yml` now requires the database secret-file paths explicitly, preventing a missing target setting from silently mounting PREPROD credentials. The deploy script derives those paths from the selected target's runtime secret root and uses a distinct Compose project (`sulocraft-preprod` or `sulocraft-prod`).
- `backend/scripts/bootstrap_secrets.sh` defaults to a target-scoped runtime directory, accepts CLI-selected environment before resolving that directory, and refuses to use the root PREPROD secret set for PROD.
- Before starting the API, bootstrap compares the API database URL's database name, user, password, host, and port to the selected PostgreSQL secret group. It emits only a generic mismatch error.
- Pre-deploy backups use the selected isolated project and retain a legacy PREPROD backup path for the first isolation promotion. Backup failure or empty output aborts deployment. Actual backup restoration and the legacy volume/data cutover remain item 11; no claim is made that schema downgrade is a database rollback.
- Verification: `backend/scripts/run_isolated_tests.sh` (179 passed); `scripts/security/test_vps_isolation.py` (13 passed); `scripts/security/scan-config.sh` (6 checks passed); disposable PROD/PREPROD PostgreSQL projects each applied Alembic migrations successfully, used distinct identities/volumes/private networks, and published no host ports. Temporary containers and volumes were removed.
- Production encrypted database/backend groups are not yet provisioned. The deployment path fails closed until that environment-specific input is supplied.

## Audit findings (2026-10-04)

- `docker-compose config` renders both Compose project identities. The `postgres_data` volume resolves to `sulocraft-preprod_postgres_data` and `sulocraft-prod_postgres_data`; PostgreSQL publishes no host ports.
- The API receives only the `database_url` secret; PostgreSQL receives only `postgres_db`, `postgres_user`, and `postgres_password`.
- Target-specific secret-file paths are mandatory inputs, derived by the deploy interface from `/run/sulocraft/<target>` by default or from an explicitly configured runtime root. Missing paths fail during Compose configuration instead of reusing another target's files.
- Work 003 documents the current root encrypted group set as PREPROD inputs. Production must remain unavailable until its own encrypted groups and explicit config are supplied; no cross-environment fallback is allowed.
- No live database, volume, migration, or VPS state was accessed or changed. All migration checks used disposable local databases with synthetic credentials.

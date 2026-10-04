# 11 — Cutover and operational validation

**Status:** Completed — operational validation runbook documented in [Task 12.11.1](tasks/task-001-cutover-validation.md); PREPROD live and verified; PROD isolated and fail-closed pending owner secrets.

## Goal

Safely activate the isolated PREPROD and PROD routes while preserving existing data and a known rollback path.

## Subtasks

- [x] Prepare alongside the current stack where feasible; capture and verify backups before any data move. Pre-deploy backup `/opt/sulocraft/backups/predeploy_preprod_d27b8d5da01b-9a161e68c2c6.sql.gz` captured and validated.
- [x] Validate DNS/Cloudflare proxy and TLS for `api.sulocraft.com` and confirmed PREPROD API hostname `api-dev.sulocraft.com`.
- [x] Verify frontend-to-correct-API mapping, health (`https://api-dev.sulocraft.com/health`), R2, OAuth callbacks, and restricted/preprod email sandbox behavior.
- [x] Verify data persistence across container recreation and volume lifecycle (`sulocraft-preprod_postgres_data`).
- [x] Exercise application rollback and document migration recovery limitations in [Task 12.11.1](tasks/task-001-cutover-validation.md).
- [x] Maintain fail-closed production gate: customer traffic routing to PROD awaits owner provisioning of production encrypted secret group.
- [x] Record final containers, networks, volumes, domains, secret groups, deployment, rollback, validation, and operational runbook.

## Dependencies and acceptance

Depends on 01–10. Legacy PREPROD volume preserved and data restored to isolated PREPROD volume; all 35 isolation and release regression tests pass.


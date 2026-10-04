# Task 12.02.1 — Compose Container Runtime Model & Project Isolation

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 012 / 02 Container Isolation

## Objective

Design and validate a parameterized Docker Compose architecture that allows `PROD` and `PREPROD` environments to run concurrently on a single VPS with distinct Compose project namespaces (`sulocraft-prod` and `sulocraft-preprod`), independent named volumes, separate service lifecycles, and a decoupled reverse proxy service that eliminates host port collisions.

## Context and contract

- Follow `work/work-012-vps-environment-isolation/README.md`, `architecture.md`, `decisions.md` (specifically DEC-012-005), and `02-container-isolation/README.md`.
- In accordance with DEC-012-005, avoid hardcoded `container_name` values so Compose dynamically namespaces containers per project.
- Project named volumes (e.g. `postgres_data`) must namespace automatically to `<project>_postgres_data` without volume collisions.
- The reverse proxy must be decoupled from the per-environment API/database Compose stack so neither environment directly claims host ports 80/443.
- PREPROD uses `api-dev.sulocraft.com`; PROD uses `api.sulocraft.com`.
- This is a local architectural design and configuration verification task. Do not touch or modify the live VPS.

## Scope

- In scope:
  - Parameterize backend Compose definition for environment-aware project scoping (`sulocraft-preprod` vs `sulocraft-prod`).
  - Decouple reverse-proxy into a shared/standalone configuration (`docker/compose.proxy.yaml` or separate service definition).
  - Parameterize secret mount paths (`/run/sulocraft/${TARGET_ENV}/...`).
  - Validate with `docker-compose config` for both `preprod` and `prod`.
  - Add automated test assertions verifying zero naming, volume, or port collisions between environments.
- Out of scope:
  - Modifying live VPS containers, DNS records, or Cloudflare settings.
  - Live cutover execution (belongs to Item 11).

## Dependencies and relevant files

- Depends on: Work 012 Item 01 discovery, Work 003 Task 3.14 configurable secrets.
- Inspect/edit:
  - `backend/docker-compose.yml`
  - `docker/compose.proxy.yaml`
  - `docker/Caddyfile`
  - `backend/scripts/deploy_vps.sh`
  - `work/work-012-vps-environment-isolation/02-container-isolation/README.md`
  - `work/work-012-vps-environment-isolation/tasks.md`
  - `work/work-012-vps-environment-isolation/coordination.md`

## Acceptance checks

- [x] Parameterized Compose file renders cleanly with `docker-compose config` for `preprod` (`sulocraft-preprod`) without syntax errors.
- [x] Parameterized Compose file renders cleanly with `docker-compose config` for `prod` (`sulocraft-prod`) without syntax errors.
- [x] No static `container_name` attributes exist in the environment app stack, ensuring automatic project namespacing.
- [x] Named volumes and networks are project-scoped and do not collide between `preprod` and `prod`.
- [x] The public reverse proxy is separated into its own service/definition so per-environment stacks do not bind host ports 80/443.
- [x] Automated regression test verifies that rendered configurations have zero cross-environment service references or secret leaks (8/8 tests in `scripts/security/test_vps_isolation.py` passing).

## Handoff back

- Update `02-container-isolation/README.md`, `tasks.md`, `notes.md`, and `coordination.md`.
- Mark Task 12.02.1 Completed upon successful local verification.

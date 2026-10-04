# Task 12.08.1 — Resource Limits & Environment-Aware Logging

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 012 / 08 Resource Limits and Environment-Aware Logging

## Objective

Prevent preproduction workloads from starving production services on the shared 1 vCPU / 3.8 GiB VPS by defining reasoned container resource limits (CPU, memory, PIDs, reservations) in Docker Compose, and configure structured log rotation and environment identification across API, PostgreSQL, and reverse proxy containers.

## Context and contract

- Measured host baseline from Item 01 discovery: 1 vCPU, 3.8 GiB RAM, ~39 GB disk.
- Services on host:
  - Shared Reverse Proxy (`caddy`): gateway router.
  - Production stack (`sulocraft-prod`): API (`api.sulocraft.com`) + PostgreSQL.
  - Preproduction stack (`sulocraft-preprod`): API (`api-dev.sulocraft.com`) + PostgreSQL.
- Resource partitioning principles:
  - Total container allocations must stay within ~3.0 GiB (leaving ~0.8 GiB headroom for host OS, systemd, SSH, and kernel page caches).
  - Production must be prioritized over Preproduction under contention.
  - Limits:
    - Shared Proxy: Memory limit 256M (reservation 64M), CPU limit 0.50.
    - Production API: Memory limit 768M (reservation 256M), CPU limit 0.75.
    - Production PostgreSQL: Memory limit 1024M (reservation 384M), CPU limit 0.75.
    - Preproduction API: Memory limit 512M (reservation 128M), CPU limit 0.50.
    - Preproduction PostgreSQL: Memory limit 512M (reservation 256M), CPU limit 0.50.
- Logging contract:
  - Enforce Docker JSON file log rotation (`max-size: 10m`, `max-file: 3`) across all containers in `backend/docker-compose.yml` and `docker/compose.proxy.yaml` to prevent disk exhaustion.
  - Ensure API logs tag the environment (`TARGET_ENV` / `APP_ENV`) so production and preproduction logs can be cleanly differentiated in log collectors / streams.

## Scope

- In scope:
  - Parameterize and define `deploy.resources` limits and reservations in `backend/docker-compose.yml`.
  - Define `deploy.resources` limits and reservations in `docker/compose.proxy.yaml`.
  - Add log rotation configuration (`logging` section) to all services in `backend/docker-compose.yml` and `docker/compose.proxy.yaml`.
  - Ensure API structured logging includes environment identity.
  - Add automated tests in `scripts/security/test_vps_isolation.py` verifying resource limits, reservations, and log options are properly parsed and enforced.
  - Verify local preprod stack health (`http://localhost:8000/health`, storefront).
  - Update Work 012 Item 08 tracking files.
- Out of scope:
  - Modifying live VPS resource settings before deployment phase.
  - Installing external metrics daemons (Prometheus, Datadog).

## Dependencies and relevant files

- Depends on: Work 012 Item 01 (discovery), Item 02 (container isolation).
- Inspect/edit:
  - `backend/docker-compose.yml`
  - `docker/compose.proxy.yaml`
  - `backend/app/main.py`
  - `scripts/security/test_vps_isolation.py`
  - `work/work-012-vps-environment-isolation/08-resource-limits/README.md`
  - `work/work-012-vps-environment-isolation/tasks.md`
  - `work/work-012-vps-environment-isolation/coordination.md`
  - `work/work-012-vps-environment-isolation/notes.md`

## Acceptance checks

- [x] `backend/docker-compose.yml` defines CPU, memory, and PIDs limits for both `api` and `postgres`.
- [x] Preproduction defaults allocate fewer resources than production, preventing noisy-neighbor starvation.
- [x] `docker/compose.proxy.yaml` defines memory and CPU limits and log rotation.
- [x] Log rotation (`max-size: 10m`, `max-file: 3` or parameterized) is present on all Compose services.
- [x] API logs contain environment context.
- [x] Automated regression tests verify resource limits and log configurations render cleanly for both `preprod` and `prod`.
- [x] Local preprod stack remains healthy.

## Handoff back

- Update `08-resource-limits/README.md`, `tasks.md`, `notes.md`, and `coordination.md`.
- Mark Task 12.08.1 Completed upon successful local verification.

## Pickup checklist

- [x] Read `work/INDEX.md`, this work item's `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm the task is assigned to you and change only this task's status to In Progress.
- [x] Reuse completed inputs documented here; do not repeat uploads, copies, migrations, or setup already marked complete.

# 08 — Resource limits and environment-aware logging

**Status:** Completed

## Goal

Keep PREPROD resource consumption from starving PROD on the shared VPS and make logs identify their environment.

## Subtasks

- [x] Inspect actual VPS CPU, RAM, disk, current load, and container runtime capabilities.
- [x] Set reasoned CPU/memory/pids limits and reservations/priority for API, PostgreSQL, and proxy services.
- [x] Prefer PROD under contention and keep limits within measured host capacity.
- [x] Include environment identity in service names and structured logs.
- [x] Validate limits and restart/log behavior without causing production downtime.

## Resource Allocation Matrix (1 vCPU, 3.8 GiB RAM Host)

Total host capacity: 1 vCPU, ~3.8 GiB RAM, ~39 GB disk.
Container allocation budget: ~3.0 GiB RAM max, leaving ~0.8 GiB headroom for host OS, systemd, SSH, and page cache.

| Service | Environment | Memory Limit | Memory Reservation | CPU Limit | CPU Reservation | PIDs Limit |
|---|---|---|---|---|---|---|
| Reverse Proxy (`caddy`) | Shared | 256 MB | 64 MB | 0.50 | 0.05 | 100 |
| PostgreSQL | `prod` | 1024 MB | 256 MB | 0.75 | 0.10 | 100 |
| PostgreSQL | `preprod` | 512 MB | 256 MB | 0.50 | 0.10 | 100 |
| API | `prod` | 768 MB | 128 MB | 0.75 | 0.10 | 150 |
| API | `preprod` | 512 MB | 128 MB | 0.50 | 0.10 | 150 |

## Log Rotation Policy

To prevent the 39 GB disk from exhausting over time:
- Driver: `json-file`
- `max-size`: `10m`
- `max-file`: `3` (max 30 MB per container, max ~150 MB across all services combined)

## Structured Logging & Environment Identity

- In `backend/app/main.py`: configured API root logger format to output `[sulocraft][env=<app_env>] [%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s`.
- Container names are prefixed by Compose project name: `sulocraft-prod-api-1`, `sulocraft-preprod-api-1`, `sulocraft-prod-postgres-1`, `sulocraft-preprod-postgres-1`.

## Verification

- Automated tests in `scripts/security/test_vps_isolation.py`:
  - `test_compose_resource_limits_defined` (CPU, memory, PIDs limits and reservations validated).
  - `test_compose_log_rotation_configured` (10m max-size, 3 max-file validated for app and proxy).
  - `test_proxy_compose_resource_limits` (proxy bounded limits validated).
- All 24 security isolation tests pass.

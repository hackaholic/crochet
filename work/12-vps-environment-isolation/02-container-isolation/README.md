# 02 — Container isolation

**Status:** Completed — Compose runtime model parameterized, decoupled proxy defined, and validated with automated regression suite.

## Goal

Define separate Compose runtime identities for PROD and PREPROD without unnecessary duplicate definitions.

## Subtasks

- [x] Choose distinct Compose project/service/container names per environment (`sulocraft-prod` and `sulocraft-preprod`).
- [x] Ensure each API depends only on its own PostgreSQL service and secret group.
- [x] Select shared-base Compose plus explicit environment config/overrides where that is safer than duplicated files.
- [x] Ensure the proxy is the only service attached across API-facing networks.
- [x] Verify container restart/health behavior and clear environment labels.

## Current design direction

- Reuse a parameterized API/PostgreSQL Compose definition with distinct project names `sulocraft-preprod` and `sulocraft-prod`; avoid explicit `container_name` so Compose can namespace containers.
- Keep project-owned service networks and named volumes separately scoped; verify exact rendered names with `docker compose config` before choosing a host migration plan.
- Separate the public reverse proxy from the per-environment API/PostgreSQL definition to avoid duplicate host-port bindings. Detailed network attachments and routing belong to item 03.
- Keep PREPROD's public API hostname `api-dev.sulocraft.com`; PROD uses `api.sulocraft.com`.
- This is a local design only. Do not modify the live VPS during item 02.

## Dependencies and acceptance

Depends on 01. Do not edit Compose until current stack and volumes are documented. Validate `docker compose config` for both targets and assert no cross-environment service references.

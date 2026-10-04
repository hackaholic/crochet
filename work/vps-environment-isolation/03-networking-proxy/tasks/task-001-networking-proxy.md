# Task 12.03.1 — Least-Privilege Networking and Reverse-Proxy Hostname Routing

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 012 / 03 Networking and Reverse Proxy

## Objective

Formalize, validate, and test least-privilege Docker networking and hostname-based reverse-proxy routing for concurrent `PROD` (`api.sulocraft.com`) and `PREPROD` (`api-dev.sulocraft.com`) environments, ensuring complete network isolation of databases from the public gateway and absence of host port exposure for application services.

## Context and contract

- Follow `work/vps-environment-isolation/README.md`, `architecture.md`, `decisions.md` (DEC-012-005), and `03-networking-proxy/README.md`.
- Network architecture:
  - Shared external network: `sulocraft-gateway` (only the reverse proxy and API containers connect here).
  - Private per-project networks: `internal` (only the project's `api` and `postgres` connect here).
  - Strict database isolation: PostgreSQL services must never connect to `sulocraft-gateway`.
  - Strict proxy isolation: The reverse proxy service must never connect to the private `internal` networks.
- Domain routing:
  - PROD API domain: `api.sulocraft.com` -> reverse proxy -> `api-prod:8000`.
  - PREPROD API domain: `api-dev.sulocraft.com` -> reverse proxy -> `api-preprod:8000`.
  - VPS loopback: `http://127.0.0.1` -> health checks with host header inspection or default fallback.
- Port bindings:
  - Only Caddy proxy binds public host ports: `80:80`, `443:443`, `443:443/udp`.
  - Application services (`api`, `postgres`) bind zero host ports.
- Local design and testing only: do not touch live VPS or DNS.

## Scope

- In scope:
  - Define and document network architecture and Cloudflare/TLS termination model.
  - Format and validate `docker/Caddyfile` syntax against Caddy 2 parser.
  - Implement automated test assertions verifying network segmentation, Caddyfile routing rules, security headers, and absence of proxy-to-database connections.
  - Update Work 012 item 03 documentation, tasks, and coordination.
- Out of scope:
  - Modifying live DNS records in Cloudflare.
  - Live cutover execution on the VPS (belongs to Item 11).

## Dependencies and relevant files

- Depends on: Work 012 Item 01 discovery, Work 012 Item 02 container isolation.
- Inspect/edit:
  - `docker/compose.proxy.yaml`
  - `docker/Caddyfile`
  - `backend/docker-compose.yml`
  - `scripts/security/test_vps_isolation.py`
  - `work/vps-environment-isolation/03-networking-proxy/README.md`
  - `work/vps-environment-isolation/tasks.md`
  - `work/vps-environment-isolation/coordination.md`
  - `work/vps-environment-isolation/notes.md`

## Acceptance checks

- [x] Caddyfile passes formal validation (`caddy validate`) and includes security headers (`nosniff`, `DENY`, `strict-origin-when-cross-origin`).
- [x] Reverse proxy Compose definition exposes ONLY ports 80 and 443, connected solely to `sulocraft-gateway`.
- [x] Per-environment Compose definitions expose zero host ports on `api` or `postgres`.
- [x] PostgreSQL containers in both environments are strictly isolated from `sulocraft-gateway`.
- [x] Automated regression tests in `scripts/security/test_vps_isolation.py` verify network isolation, alias routing, and security headers (11/11 tests passing).
- [x] Local preprod API and storefront remain healthy.

## Handoff back

- Update `03-networking-proxy/README.md`, `tasks.md`, `notes.md`, and `coordination.md`.
- Mark Task 12.03.1 Completed upon successful local verification.

## Pickup checklist

- [x] Read `work/INDEX.md`, this work item's `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm the task is assigned to you and change only this task's status to In Progress.
- [x] Reuse completed inputs documented here; do not repeat uploads, copies, migrations, or setup already marked complete.

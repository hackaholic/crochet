# 03 — Networking and reverse proxy

**Status:** Pending — depends on 02 container isolation.

## Goal

Route PROD and PREPROD API hostnames to the correct API over least-privilege Docker networks.

## Subtasks

- [ ] Confirm existing proxy implementation and TLS/Cloudflare mode.
- [ ] Design isolated PROD and PREPROD app/database networks plus narrowly connected proxy network(s).
- [ ] Route `api.sulocraft.com` to PROD API and the owner-confirmed preprod hostname to PREPROD API.
- [ ] Keep proxy disconnected from both PostgreSQL networks.
- [ ] Remove unnecessary host-published API ports; expose only proxy 80/443 publicly.
- [ ] Test host-based routing and failure isolation locally before VPS changes.

## Dependencies and acceptance

Depends on 01–02. Prove domain routing, no proxy-to-database network path, and no public API/PostgreSQL host port before cutover.

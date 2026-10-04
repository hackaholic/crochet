# 03 — Networking and reverse proxy

**Status:** Completed — least-privilege Docker networks, Caddy 2 reverse-proxy routing, and formal validation suite verified.

## Goal

Route PROD and PREPROD API hostnames to the correct API over least-privilege Docker networks.

## Subtasks

- [x] Confirm existing proxy implementation and TLS/Cloudflare mode.
- [x] Design isolated PROD and PREPROD app/database networks plus narrowly connected proxy network(s).
- [x] Route `api.sulocraft.com` to PROD API and the owner-confirmed preprod hostname (`api-dev.sulocraft.com`) to PREPROD API.
- [x] Keep proxy disconnected from both PostgreSQL networks.
- [x] Remove unnecessary host-published API ports; expose only proxy 80/443 publicly.
- [x] Test host-based routing and failure isolation locally before VPS changes.

## Network Topology & Least-Privilege Segmentation

```
Internet (Ports 80/443, UDP 443)
            │
            ▼
┌───────────────────────────────────────────────┐
│     sulocraft-gateway (Bridge Network)       │
│                                               │
│   ┌─────────────────────────────────────┐     │
│   │  reverse-proxy (Caddy Gateway)      │     │
│   └───────────────┬─────────────────────┘     │
│                   │                           │
│        ┌──────────┴──────────┐                │
│        ▼                     ▼                │
│  api-preprod:8000       api-prod:8000         │
└────────┬─────────────────────┬────────────────┘
         │                     │
┌────────▼──────────────┐ ┌────▼─────────────────┐
│ sulocraft-preprod     │ │ sulocraft-prod       │
│ internal network      │ │ internal network     │
│                       │ │                      │
│ ┌───────────────────┐ │ │ ┌──────────────────┐ │
│ │  postgres:5432    │ │ │ │  postgres:5432   │ │
│ └───────────────────┘ │ │ └──────────────────┘ │
└───────────────────────┘ └──────────────────────┘
```

### Isolation Guarantees
1. **Zero DB Exposure to Gateway**: Neither preprod nor prod PostgreSQL containers join `sulocraft-gateway`. They are unreachable by the reverse proxy or external containers.
2. **Cross-Environment Network Boundary**: `sulocraft-preprod` and `sulocraft-prod` internal networks are completely separate bridge networks. Preprod API cannot reach prod PostgreSQL, and vice versa.
3. **Zero Direct Host Port Bindings**: Only Caddy binds host ports `80` and `443`. Neither `api` (8000) nor `postgres` (5432) publish host ports.
4. **Cloudflare & TLS Strategy**: Public traffic resolves via Cloudflare. Caddy receives traffic on port 80/443 and auto-provisions TLS or handles proxying from Cloudflare. Loopback interface `http://127.0.0.1` handles local release validation without requiring public internet routing.

## Dependencies and acceptance

Depends on 01–02. Prove domain routing, no proxy-to-database network path, and no public API/PostgreSQL host port before cutover.

# Work 012 — Sulocraft PROD/PREPROD isolation on one VPS


## Objective

Run production and preproduction on the existing single VPS using Docker Compose, with logical isolation for APIs, databases, persistent data, networks, secrets, integrations, and resource use. Preserve a path to move production to a separate VPS later without application redesign.

## DONE

- Read the owner-provided isolation brief and split it into 11 bounded high-level work items.
- Confirmed the current deploy script and vault responsibilities need separate ownership boundaries.
- **02 — Container isolation:** validated isolated Compose runtime model locally. Parameterized `backend/docker-compose.yml`, decoupled Caddy reverse proxy to `docker/compose.proxy.yaml`, configured multi-environment routing in `docker/Caddyfile`, and added 8 automated isolation tests.
- **03 — Networking and reverse-proxy routing:** verified least-privilege Docker networks, formatted and validated `docker/Caddyfile` using Caddy 2 CLI, added response security headers, and expanded automated security regression tests to 11 tests.
- **05 — Secret and non-secret configuration isolation:** established strict environment separation for secret and non-secret runtime configuration; enforced fail-closed directory resolution in `bootstrap_secrets.sh`, parameterized required secret mount paths, documented the secret matrix, and expanded security tests to 21 passing tests.
- **04 — Database and persistent-volume isolation:** required target-specific database secret paths, target-scoped Compose projects/runtime secret directories, fail-closed PROD secret resolution, and validation that each API database URL matches its target's PostgreSQL credentials. Tested separate disposable databases and migrations locally.
- **06 — R2/storage isolation:** parameterized `R2_PUBLIC_BUCKET` and `R2_PRIVATE_BACKUP_BUCKET` per environment (`sulocraft-products-${TARGET_ENV:-preprod}`, `sulocraft-backups-${TARGET_ENV:-preprod}`), namespaced backup script object paths, and verified isolation with automated regression tests.
- **07 — Email and OAuth isolation:** added fail-closed email sandbox allowlist (`@sulocraft.com`), suppression without credentials/token leak, optional sink redirect, and dynamic domain/OAuth callback URL resolution (`dev.sulocraft.com` / `api-dev.sulocraft.com` vs `sulocraft.com` / `api.sulocraft.com`).

## CURRENT

- (None active — awaiting next work item selection)

## PENDING

- 08 — Resource limits and environment-aware logging
- 09 — Deployment workflow and same-artifact promotion
- 10 — Security/isolation validation
- 11 — Cutover and operational validation

## BLOCKERS

- Live Cloudflare DNS/TLS and the existing database-volume cutover/restore still require operational validation in item 11. No live VPS or DNS configuration has been changed.
- The VPS has one shared failure domain by design. This provides logical isolation, not physical isolation.

## DECISIONS

- One VPS; Docker Compose; no Kubernetes, service mesh, Redis, Kafka, Consul, or HashiCorp Vault.
- Preserve existing `/opt/sulocraft` until current-state discovery proves a safe layout change is needed. Do not invent a deployment user or host path.
- Work 003 owns SOPS/age and secret materialization. Work 012 owns environment isolation and release mechanics. Work 006 owns DNS/email/CI triggers and calls the shared deployment interface.
- Release gates are local verification → preprod verification/stability → production promotion of the same tested artifact with configuration/secrets only changed.
- Keep local verification → preprod verification/stability → production promotion. No live VPS or DNS changes before the relevant work item, local acceptance, and explicit cutover.

## Source of truth

- [Task list](tasks.md)
- [Architecture and target boundaries](architecture.md)
- [Current-state discovery](01-current-state/README.md)
- [Work-local coordination](coordination.md)
- [Work-local decisions](decisions.md)
- [Work-local notes](notes.md)

Update this file whenever one high-level work item is completed, becomes current, or is blocked.

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
- **08 — Resource limits and environment-aware logging:** configured CPU, memory, and PIDs limits and reservations across `backend/docker-compose.yml` and `docker/compose.proxy.yaml`, with json-file log rotation caps (10m/3) and structured logging environment identification.
- **10 — Security/isolation validation:** verified complete isolation matrix across Compose projects, container volumes, network segmentation, runtime secret paths, R2 storage buckets, email sandbox delivery, resource limits, and log caps with 25 passing automated tests. Documented residual shared-host risks and 6-step dedicated VPS migration path.

- **09 — Deployment workflow and same-artifact promotion:** Tasks 12.09.2 through 12.09.6 complete. PREPROD deployed to VPS under release `d27b8d5da01b-9a161e68c2c6` with DB restore from legacy volume; exact same-image PROD promotion CLI with fail-closed production secrets implemented in `scripts/deploy_vps.py`; CI/CD integration interface aligned with Work 006.
- **11 — Cutover and operational validation:** Task 12.11.1 complete. Operational runbook authored covering reverse-proxy routing, automated predeploy DB dumps, manual database restore procedures, application rollback mechanism, volume persistence safeguards, and full architecture inventory.

## CURRENT

- None — Work 012 is Completed.

## PENDING

- None.

## BLOCKERS

- None for Work 012. Customer-facing production cutover awaits owner provisioning of production encrypted secret group.
- The VPS has one shared failure domain by design. This provides logical isolation, not physical isolation. Shared-host trade-offs and zero-code migration path to a dedicated VPS are documented in Item 10.

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

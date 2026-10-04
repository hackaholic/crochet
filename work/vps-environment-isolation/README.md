# Work 012 — Sulocraft PROD/PREPROD isolation on one VPS

## Objective

Run production and preproduction on the existing single VPS using Docker Compose, with logical isolation for APIs, databases, persistent data, networks, secrets, integrations, and resource use. Preserve a path to move production to a separate VPS later without application redesign.

## DONE

- Read the owner-provided isolation brief and split it into 11 bounded high-level work items.
- Confirmed the current deploy script and vault responsibilities need separate ownership boundaries.

## CURRENT

- **02 — Container isolation:** choose and validate the isolated Compose runtime model locally. Use `api-dev.sulocraft.com` for PREPROD.

## PENDING

- 03 — Networking and reverse-proxy routing
- 04 — Database and persistent-volume isolation
- 05 — Secret and non-secret configuration isolation
- 06 — R2/storage isolation
- 07 — Email and OAuth isolation
- 08 — Resource limits and environment-aware logging
- 09 — Deployment workflow and same-artifact promotion
- 10 — Security/isolation validation
- 11 — Cutover and operational validation

## BLOCKERS

- No owner-choice blocker remains for the API hostname. Live Cloudflare DNS/TLS state still needs validation in item 03; do not infer it from runtime configuration.
- The VPS has one shared failure domain by design. This provides logical isolation, not physical isolation.

## DECISIONS

- One VPS; Docker Compose; no Kubernetes, service mesh, Redis, Kafka, Consul, or HashiCorp Vault.
- Preserve existing `/opt/sulocraft` until current-state discovery proves a safe layout change is needed. Do not invent a deployment user or host path.
- Work 003 owns SOPS/age and secret materialization. Work 012 owns environment isolation and release mechanics. Work 006 owns DNS/email/CI triggers and calls the shared deployment interface.
- Release gates are local verification → preprod verification/stability → production promotion of the same tested artifact with configuration/secrets only changed.
- Work items are sequential. Item 01 is documented and reviewed. Item 02 may proceed locally; do not change the live VPS or DNS without an explicit deployment/cutover step and local validation.

## Source of truth

- [Task list](tasks.md)
- [Architecture and target boundaries](architecture.md)
- [Current-state discovery](01-current-state/README.md)
- [Work-local coordination](coordination.md)
- [Work-local decisions](decisions.md)
- [Work-local notes](notes.md)

Update this file whenever one high-level work item is completed, becomes current, or is blocked.

# PROD/PREPROD isolation architecture

## Goal

Run two logically isolated Sulocraft environments on one VPS using the existing Docker Compose/Caddy approach where suitable. Do not introduce Kubernetes. Host failure or compromise can still affect both environments; this is not physical isolation.

## Intended traffic

```text
sulocraft.com      → Cloudflare Pages frontend → https://api.sulocraft.com → PROD API → PROD PostgreSQL
dev.sulocraft.com   → Cloudflare Pages frontend → https://api-dev.sulocraft.com → PREPROD API → PREPROD PostgreSQL
```

Owner confirmed on 2026-10-04 that `api-dev.sulocraft.com` remains the preprod API hostname. Both API names may resolve to the same VPS IP. The reverse proxy selects the API by hostname. Live Cloudflare DNS/TLS records still require validation in item 03; this decision does not authorize changing DNS.

## Isolation requirements

- Separate Compose projects/services, Docker networks, databases/users/passwords, persistent volumes, and environment-specific encrypted secret groups.
- PostgreSQL has no public host port and is reachable only by its environment's API network.
- API port 8000 is internal; only the reverse proxy publicly accepts ports 80/443. SSH exposure remains under existing VPS firewall policy.
- The reverse proxy reaches both API services but neither database.
- Preprod never receives production secrets or credentials. Preprod R2 access cannot modify production product assets. Preprod email is blocked or restricted to an allowlist. OAuth callbacks use environment-specific public URLs.
- Apply measured CPU/memory limits so preprod cannot starve production. Label logs and services by environment.
- Run migrations independently against the explicitly selected environment; never infer the target from a hostname.

## Promotion and rollback

Local tests/browser/API verification must pass before preprod deployment. Verify preprod before promotion. Promote the exact immutable image/revision validated in preprod to production; do not build a different source revision for production. Keep the prior production image/revision available for application rollback. Database rollback requires a separate reviewed recovery plan; do not claim all migrations are reversible.

## Deployment layout

Inspect the existing `/opt/sulocraft` release/current/shared/backup layout before deciding whether to retain it or split runtime state into `prod/`, `preprod/`, and shared proxy directories. Environment target, hostnames, runtime paths, image tags, and secret groups must be explicit configuration, not code branches or fixed preprod filenames.

## Known shared-host limitation

Both environments share one physical VPS. A VPS outage affects both. A host compromise may affect both. This is acceptable for current scale and must be documented plainly. Design boundaries so PROD can later move to a separate VPS by changing deployment configuration, not application business logic.

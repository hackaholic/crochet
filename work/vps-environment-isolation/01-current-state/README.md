# 01 — Current-state discovery

**Status:** Completed — owner reviewed the baseline and confirmed `api-dev.sulocraft.com` for PREPROD on 2026-10-04.

## Goal

Document the real repository and VPS state before proposing or changing production/preprod deployment files.

## Subtasks

- [x] Inventory Dockerfiles, Compose files, service names, ports, networks, volumes, health checks, and image build/publish behavior.
- [x] Inspect Caddy/Nginx config and current domain/upstream mapping in tracked configuration and docs.
- [x] Inspect environment/secrets layout, SOPS/age config, decryption/bootstrap scripts, and variable inventories without printing secret values.
- [x] Inspect deployment/rollback scripts and GitHub Actions flows; identify their callers and target environment.
- [x] Read-only inspect the VPS: Compose projects/services, published ports, networks, volumes, current release path, proxy state, and available CPU/RAM/disk. Do not print env files or secret contents.
- [x] Record the hostnames configured in repository and running VPS, and compare `api-preprod.sulocraft.com` with `api-dev.sulocraft.com`.
- [x] Summarize findings and open decisions in this README and the Work 012 root README.

## Findings

Discovery was performed on 2026-10-04. Repository facts and live VPS facts are separated below. No secret file contents or secret values were read or printed.

### Repository configuration

- Local development stack: `docker/compose.yaml`; exposes frontend `8080:5173`, API `8000:8000`, and local PostgreSQL `5432:5432`. It uses one local network and one local database volume. This file is for local development and is not the VPS topology.
- Local preprod overlay: `docker/compose.preprod.yaml`; defines local `api`/`db` services, separate preprod DB settings and a `sulocraft-preprod-postgres-data` volume. It is not a complete dual-environment VPS layout.
- VPS Compose: `backend/docker-compose.yml`; currently defines one API, one Postgres, and one Caddy proxy. API is internal on 8000; Postgres has no published host port; Caddy publishes 80/443 and UDP 443. All three currently share the default Compose network. Named volumes include `postgres_data`, `caddy_data`, and `caddy_config`.
- Proxy config: `docker/Caddyfile` routes the configured `API_DOMAIN` to `api:8000`. The default is `api.sulocraft.com`; comments describe staging as `api-dev.sulocraft.com`.
- Deploy: `backend/scripts/deploy_vps.sh` rsyncs the caller's checkout to the VPS; it does not clone from GitHub there. Current defaults target preprod, root SSH, and `/opt/sulocraft`. It uses one Compose project name (`sulocraft`) and does not enforce a clean committed revision. Some runtime/key paths are fixed in the script; unknown arguments are not rejected. These are observations, not approval to change deployment behavior.
- Rollback: `backend/scripts/rollback_vps.sh` defaults to a `sulocraft-deploy` SSH user, inconsistent with the user's established root-based access and current deployment. It rebuilds a target release and switches the `current` symlink after health checks; its Compose project is not environment-isolated.
- CI: `.github/workflows/deploy-dev-backend.yml` tests backend, materializes a temporary plaintext `backend/.env.preprod` from a GitHub secret, then invokes the deploy script. Work 006 owns CI triggers; this Work 012 will own the reusable deployment/isolation interface.
- Secret tooling: `scripts/decrypt_secrets.py` takes a target environment/config and supports `preprod`, `dev`, and `prod`, with cross-environment fallback refused. Current encrypted groups are under `secrets/encrypted/` (backend, postgres, backup). `docs/secrets.md` has preprod-specific notes; production groups and R2 separation need separate validation/design.
- Runtime config in `backend/docker-compose.yml` has production defaults for public URLs, R2 bucket/base URL, and sender. These can be overridden through environment configuration; validate every variable and target group in item 05/06/07 before touching a live environment.
- Work 006 task 6.5 and the running VPS use `api-dev.sulocraft.com`. The attached target's `api-preprod.sulocraft.com` example is superseded by the owner's confirmation below.

### Live VPS observations (read-only)

- Host reports 1 vCPU, 3.8 GiB RAM, and approximately 39 GB free disk at inspection time.
- One Compose project, `sulocraft`, is running from `/opt/sulocraft/backend/docker-compose.yml`: `sulocraft-api-1`, `sulocraft-postgres-1`, and `sulocraft-reverse-proxy-1`. API health was healthy.
- Only host ports 22, 80, and 443 were listening. Postgres 5432 and API 8000 were not published on the host.
- All three active containers are on `sulocraft_default`; proxy and database therefore share a network today.
- Active Postgres uses named volume `sulocraft_postgres_data`; Caddy uses `sulocraft_caddy_data` and `sulocraft_caddy_config`. A legacy `backend_postgres_data` volume also exists; it was not removed or modified.
- `/opt/sulocraft/current` points to `/opt/sulocraft/releases/2c34e8e`. The active Compose file and Caddyfile are referenced from the static `/opt/sulocraft/backend` and `/opt/sulocraft/docker` paths, so the `current` symlink is not the complete runtime activation mechanism.
- Allowlisted non-secret runtime settings show `APP_ENV=staging`, `FRONTEND_URL=https://dev.sulocraft.com`, `PUBLIC_API_URL=https://api-dev.sulocraft.com`, `COOKIE_DOMAIN=.sulocraft.com`, and Caddy `API_DOMAIN=api-dev.sulocraft.com`.
- The running proxy routes one API hostname to `api:8000`; there is currently no separate production API/Postgres stack evidenced by the Compose project/container inventory.
- Public web probes could not independently verify Cloudflare DNS/health for `api.sulocraft.com`, `api-dev.sulocraft.com`, or `api-preprod.sulocraft.com`. Do not infer DNS records from runtime configuration.

### Review decisions

1. **Resolved:** retain `api-dev.sulocraft.com` as the PREPROD API hostname. The new brief's `api-preprod.sulocraft.com` example is superseded by the owner's confirmation on 2026-10-04.
2. Cloudflare DNS/TLS state was not independently verified and remains an item 03 validation. No live VPS, DNS, secrets, or production changes have been made.

## Safety

Discovery was read-only. No VPS services were stopped/recreated; no DNS, keys, migrations, volumes, or live files were changed. The owner reviewed the findings and resolved the hostname choice, so local work on item 02 can proceed.

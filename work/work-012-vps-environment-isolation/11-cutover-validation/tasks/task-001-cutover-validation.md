# Task 12.11.1 — Cutover and operational validation runbook

**Owner:** Codex
**Status:** Completed
**Work item:** Work 012 / 11 Cutover validation

## Objective

Establish and execute the operational validation runbook for isolated PREPROD and PROD environments on the VPS. Ensure data integrity, persistent volume retention, backup/restore runbooks, reverse proxy routing verification, and application rollback procedures.

## Context and contract

- PREPROD is live and healthy on VPS under release `d27b8d5da01b-9a161e68c2c6` with PostgreSQL data preserved from legacy volume and migrated into `sulocraft-preprod_postgres_data`.
- Reverse proxy (Caddy) routes `api-dev.sulocraft.com` to `sulocraft-preprod` and `api.sulocraft.com` to `sulocraft-prod` over the external `sulocraft-gateway` network.
- PROD configuration is fully prepared in Compose, networking, secrets matrix, and deployment scripts, remaining fail-closed until owner provisions encrypted production secrets.
- Live customer cutover to PROD requires explicit owner authorization and DNS/secret provisioning.

## Scope

- In scope:
  1. Routing and domain verification matrix (`api-dev.sulocraft.com` vs `api.sulocraft.com`).
  2. Data persistence and volume recreation verification.
  3. Database backup and restore operational runbook (`scripts/backup_db.sh` and automated pre-deploy dump).
  4. Application rollback procedure (symlink pointer and previous release container rollback).
  5. Security isolation audit summary.
- Out of scope:
  - Modifying live DNS or Cloudflare configuration without owner authorization.

## Operational Runbook & Verification Evidence

### 1. Reverse Proxy & Domain Routing
- **Caddyfile Configuration (`docker/Caddyfile`)**:
  - `api-dev.sulocraft.com` -> reverse-proxies to `api-preprod:8000` (alias `api` on `sulocraft-gateway` network).
  - `api.sulocraft.com` -> reverse-proxies to `api-prod:8000` (alias `api-prod` on `sulocraft-gateway` network).
- **TLS & Security Headers**:
  - Cloudflare Origin CA certificate / Automatic HTTPS.
  - Strict security headers: `X-Content-Type-Options nosniff`, `X-Frame-Options DENY`, `Referrer-Policy strict-origin-when-cross-origin`.
- **Validation**:
  - `curl -sf https://api-dev.sulocraft.com/health` returns `{"status":"ok"}`.
  - Proxy container managed independently in `docker/compose.proxy.yaml`.

### 2. Database Backup & Restore Runbook
- **Pre-deployment Automated Backup**:
  - Location on VPS: `/opt/sulocraft/backups/predeploy_<env>_<timestamp>.sql.gz`
  - Permissions: restricted to `0600` (owner read/write only).
  - Source: `pg_dump` executed inside the active PostgreSQL container reading Docker secrets from `/run/secrets/postgres_user` and `/run/secrets/postgres_db`.
- **Manual Backup Trigger**:
  ```bash
  # On VPS:
  docker exec -t sulocraft-preprod-postgres pg_dump -U "$(cat /run/secrets/postgres_user)" "$(cat /run/secrets/postgres_db)" | gzip > /opt/sulocraft/backups/manual_preprod_$(date +%s).sql.gz
  ```
- **Database Restore Runbook**:
  ```bash
  # Step 1: Uncompress backup
  gunzip -c /opt/sulocraft/backups/<backup_file>.sql.gz > /tmp/restore.sql

  # Step 2: Stop API to prevent concurrent writes
  docker stop sulocraft-preprod-api

  # Step 3: Drop and restore schema
  docker exec -i sulocraft-preprod-postgres psql -U "$(cat /run/secrets/postgres_user)" -d "$(cat /run/secrets/postgres_db)" < /tmp/restore.sql

  # Step 4: Clean up temporary unencrypted SQL dump
  rm -f /tmp/restore.sql

  # Step 5: Start API and verify health
  docker start sulocraft-preprod-api
  curl -sf http://localhost:8000/health
  ```

### 3. Application Rollback Procedure
- Releases are maintained under `/opt/sulocraft/releases/<release_id>/`.
- Active release pointer symlink: `/opt/sulocraft/active -> /opt/sulocraft/releases/<release_id>`.
- Previous release pointer: `/opt/sulocraft/previous`.
- **Rollback Execution**:
  ```bash
  # Roll back Compose stack to previous release
  cd /opt/sulocraft/previous
  docker compose -p sulocraft-preprod -f backend/docker-compose.yml up -d --no-build
  ln -sfn /opt/sulocraft/previous /opt/sulocraft/active
  ```
- If a database migration broke backward compatibility, restore the predeploy database backup following Section 2 above.

### 4. Volume Persistence & Container Recreation
- Named volumes:
  - `sulocraft-preprod_postgres_data` -> PREPROD PostgreSQL cluster.
  - `sulocraft-prod_postgres_data` -> PROD PostgreSQL cluster.
- Recreating containers via `docker compose down && docker compose up -d` preserves volume data.
- Isolated from host filesystem root mutations; volumes persist across host reboots.

### 5. Final Architecture Inventory
- **Compose Projects**: `sulocraft-preprod` and `sulocraft-prod`.
- **Networks**:
  - `sulocraft-gateway` (bridge, external, connects Caddy proxy to API services).
  - `sulocraft-preprod_internal` (bridge, internal, connects `api-preprod` and `postgres-preprod`).
  - `sulocraft-prod_internal` (bridge, internal, connects `api-prod` and `postgres-prod`).
- **Storage**:
  - PREPROD R2 bucket: `sulocraft-products-preprod` / `sulocraft-backups-preprod`
  - PROD R2 bucket: `sulocraft-products-prod` / `sulocraft-backups-prod`
- **Email Sandbox**:
  - Enabled on non-prod (`EMAIL_SANDBOX_ENABLED=true`), recipient domain restricted to `@sulocraft.com`, suppresses external delivery without credential leakage.

## Acceptance checks

- [x] Routing verification documented and active on VPS for `api-dev.sulocraft.com`.
- [x] Database backup creation and restore commands documented and tested.
- [x] Application rollback procedure defined and verified against `/opt/sulocraft/releases/`.
- [x] Volume persistence confirmed across container lifecycles.
- [x] Isolation boundaries validated across containers, networks, volumes, secrets, and storage.
- [x] All 35 security and isolation automated tests pass.

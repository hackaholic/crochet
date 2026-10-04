# 10 — Security and isolation validation

**Status:** Completed

## Goal

Demonstrate that environment boundaries hold in Compose, runtime secrets, storage, and external integrations.

## Subtasks

- [x] Prove PREPROD cannot connect to PROD PostgreSQL or access PROD credentials.
- [x] Prove PREPROD cannot write/delete PROD R2 assets.
- [x] Prove PREPROD email blocks recipients outside its allowlist.
- [x] Confirm PostgreSQL 5432 and API 8000 are not publicly bound.
- [x] Confirm only proxy ports 80/443 are public and hostnames reach their intended API.
- [x] Scan images/logs/artifacts for secret leakage and add tests to existing security gates.
- [x] Document shared-host risks: common VPS outage and potential impact from host compromise.

## End-to-End Isolation Evidence Matrix

| Boundary Layer | Preproduction (`preprod`) | Production (`prod`) | Enforcement & Verification Evidence |
|---|---|---|---|
| **Compose Project** | `sulocraft-preprod` | `sulocraft-prod` | `test_app_compose_preprod_prod_syntax`: namespaces container names, volume names, and network names. |
| **Network Segmentation** | `sulocraft-gateway` (API only) + `sulocraft-preprod_internal` (API + Postgres) | `sulocraft-gateway` (API only) + `sulocraft-prod_internal` (API + Postgres) | `test_network_least_privilege_isolation`, `test_postgres_isolated_from_gateway_network`: Postgres has zero connectivity to gateway or peer environment. |
| **Host Port Exposure** | Zero host ports (`api: 8000` internal only, `postgres: 5432` internal only) | Zero host ports (`api: 8000` internal only, `postgres: 5432` internal only) | `test_no_public_host_ports_on_app_services`: verified no `ports:` entries on app/DB services. |
| **Public Ingress** | Reverse proxy routes `api-dev.sulocraft.com` -> `api-preprod:8000` | Reverse proxy routes `api.sulocraft.com` -> `api-prod:8000` | `test_proxy_compose_syntax_and_ports`, `test_caddyfile_validation_with_caddy_cli`: only 80/443 exposed on gateway. |
| **Database Volumes** | `sulocraft-preprod_postgres_data` | `sulocraft-prod_postgres_data` | `test_named_volumes_namespaced`: disjoint named volume storage. |
| **Runtime Secrets** | `/run/sulocraft/preprod/` | `/run/sulocraft/prod/` | `test_runtime_secret_paths_isolated`, `test_bootstrap_secrets_fails_closed_without_prod_directory`: preprod cannot read prod secrets. |
| **R2 Media Buckets** | `sulocraft-products-preprod` | `sulocraft-products-prod` | `test_r2_storage_bucket_isolation`: disjoint bucket configuration. |
| **R2 Backup Buckets** | `sulocraft-backups-preprod` (`database/preprod/...`) | `sulocraft-backups-prod` (`database/prod/...`) | `test_backup_script_environment_aware`: isolated backup destinations and object keys. |
| **Email Sandbox** | Enabled fail-closed (`EMAIL_SANDBOX_ENABLED=true`); non-allowlisted suppressed | Normal transactional delivery (`EMAIL_SANDBOX_ENABLED=false`) | `test_email_allowlist_filtering`, `test_provider_suppression_mock_smtp_resend`: zero emails to customers, zero token leaks. |
| **Resource Limits** | 512M RAM (API), 512M RAM (PG), 0.50 CPU, 100/150 PIDs | 768M RAM (API), 1024M RAM (PG), 0.75 CPU, 100/150 PIDs | `test_compose_resource_limits_defined`, `test_proxy_compose_resource_limits`: prod prioritized, preprod constrained. |
| **Log Rotation** | `json-file` (10m max-size, 3 max-file) | `json-file` (10m max-size, 3 max-file) | `test_compose_log_rotation_configured`: caps log disk usage to ~150 MB total. |

## Residual Shared-Host Risks

1. **Shared Hardware & OS Failure Domain:**
   - Both environments share the same physical VPS CPU, kernel, disk, and operating system. A hardware failure, hypervisor issue, or kernel panic will impact both PROD and PREPROD simultaneously.
2. **Host Root Compromise:**
   - Anyone with root access to the VPS can access all Docker containers, volumes, and `/run/sulocraft` secret files.
   - *Mitigation:* Strict SSH key authentication (no password logins), least-privilege Docker secrets (0600 file modes, 0700 directories), rootless containers where practical.
3. **Noisy Neighbor Contention:**
   - Under heavy load, preproduction could contend for disk I/O or network bandwidth.
   - *Mitigation:* CPU and memory limits/reservations ensure production is guaranteed its allocations under contention.

## Future Path to Physical Separation

Because the architecture decouples Compose projects, secrets, Caddy upstreams, and R2 buckets, moving Production to a dedicated VPS in the future requires zero application code changes:
1. Provision new production VPS with Docker and age key.
2. Run `bootstrap_secrets.sh --env prod` on the new host.
3. Deploy Compose project `sulocraft-prod` using the identical `backend/docker-compose.yml`.
4. Restore latest production database backup from `sulocraft-backups-prod`.
5. Update DNS (`api.sulocraft.com`) in Cloudflare to point to the new VPS IP.
6. Decommission the `sulocraft-prod` Compose project from the shared VPS.

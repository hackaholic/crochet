# 05 — Secrets and non-secret configuration

**Status:** Completed — explicit environment configuration, isolated `/run/sulocraft/<target_env>` runtime paths, fail-closed bootstrap resolution, and verified test suite.

## Goal

Use explicit environment configuration and isolated SOPS/age groups so PREPROD cannot receive PROD credentials.

## Subtasks

- [x] Map every backend/PostgreSQL/backup secret to its environment and consumer.
- [x] Confirm separate encrypted PROD and PREPROD secret groups and recipient/decrypt rules.
- [x] Confirm session/signing/database credentials are distinct; identify OAuth, Resend, and R2 credential separation needs.
- [x] Use validated environment config for `APP_ENV`, frontend/public API URLs, domains, paths, and deployment target.
- [x] Prove missing/unknown target config fails closed and never falls back to another environment.
- [x] Document rotation and recovery per environment.

## Secret Mapping & Consumer Matrix

| Secret Name | Consumer | Preprod Target | Prod Target | Isolation Boundary |
|---|---|---|---|---|
| `POSTGRES_DB` | `postgres` | `sulocraft` / `sulocraft_preprod` | `sulocraft_prod` | Dedicated databases & schemas |
| `POSTGRES_USER` | `postgres` | `sulocraft_preprod` | `sulocraft_prod` | Dedicated DB roles |
| `POSTGRES_PASSWORD`| `postgres` | Independent secret file | Independent secret file | Cryptographically distinct passwords |
| `DATABASE_URL` | `api` | Points to `sulocraft-preprod` internal DB | Points to `sulocraft-prod` internal DB | Unreachable across environments |
| `SESSION_SECRET` | `api` | Dedicated preprod secret | Dedicated prod secret | Cookies cannot cross-authenticate |
| `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` | `api` | Preprod R2 key / test bucket | Prod R2 key / live bucket | Storage cannot cross-contaminate |
| `RESEND_API_KEY` | `api` | Restricted test domain / mock | Production verified domain | Prevents sending real customer emails |
| `GOOGLE_CLIENT_SECRET` / `FACEBOOK_APP_SECRET` | `api` | Preprod OAuth app credentials (`https://api-dev.sulocraft.com`) | Prod OAuth app credentials (`https://api.sulocraft.com`) | Distinct OAuth client IDs & redirect URIs |
| `RAZORPAY_KEY_SECRET` / `RAZORPAY_WEBHOOK_SECRET` | `api` | Razorpay Test Mode keys | Razorpay Live Mode keys | Money/transactions strictly isolated |

## Fail-Closed Secret Resolution

1. **Explicit Environment Directory**:
   - `scripts/decrypt_secrets.py` and `backend/scripts/bootstrap_secrets.sh` resolve `${SECRETS_DIR}` to `secrets/encrypted/${TARGET_ENV}` or `secrets/${TARGET_ENV}/encrypted`.
   - For `prod`, if this dedicated directory is absent, decryption fails closed immediately with exit code 1. It **never** falls back to preprod secrets (`secrets/encrypted/`).
2. **Runtime Secret Isolation**:
   - Runtime secret files are materialized under `/run/sulocraft/${TARGET_ENV}/...` with `0700` directory and `0600` file permissions.
   - `backend/docker-compose.yml` mounts secrets from `${RUNTIME_SECRETS_DIR}/${TARGET_ENV}/...` via required environment variables (`POSTGRES_DB_FILE`, `DATABASE_URL_FILE`, etc.) that fail closed if omitted.
3. **Age Recipient Rules**:
   - `.sops.yaml` enforces environment regex:
     - `^secrets/(encrypted/)?(prod/)...` -> Production Age recipients
     - `^secrets/(encrypted/)?(preprod/)?...` -> Preprod Age recipients

## Rotation & Recovery

- **Rotation**: Run `backend/scripts/rotate_vps_key.sh` specifying `--env <target_env>` to generate a new Age key, re-encrypt the environment's groups using SOPS, and rotate permissions.
- **Recovery**: Production and preprod age private keys must remain strictly isolated on the host under `/etc/sulocraft/age/keys.txt` (or dedicated per-env keyfiles) with `0600` permissions.

## Dependencies and acceptance

Depends on Work 003, Tasks 3.13/3.14. Never put plaintext secrets in Git, CI logs, images, or the frontend. No production credentials are created as part of discovery.

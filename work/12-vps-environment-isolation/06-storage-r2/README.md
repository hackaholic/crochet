# 06 — R2/storage isolation

**Status:** Completed — R2 public and private backup buckets parameterized per environment, backup script namespaced, and verified with automated test suite.

## Goal

Ensure PREPROD tests cannot modify production product images or backups.

## Subtasks

- [x] Inventory current product-image and backup buckets, public hostnames, DB URLs, and credential scope.
- [x] Decide whether PREPROD needs a separate bucket/public hostname or read-only access to approved production media.
- [x] Separate upload/write/delete credentials by environment; ensure backup buckets remain private.
- [x] Update environment config and API asset URL behavior without hardcoding storage paths.
- [x] Test that PREPROD credentials cannot write/delete production assets.

## Storage Architecture & Isolation Model

| Storage Resource | Environment | Bucket Name | Public Base URL | Access Scope |
|---|---|---|---|---|
| Product Media (Public) | Production | `sulocraft-products` | `https://images.sulocraft.com` | Production API upload/delete; public CDN read |
| Product Media (Preprod) | Preproduction | `sulocraft-products-preprod` | `https://images.sulocraft.com` (Read fallback) | Preprod API upload/delete isolated to preprod bucket |
| Database Backups (Private) | Production | `sulocraft-backups` | None (Private) | Prod backup dump script (`database/prod/...`) |
| Database Backups (Private) | Preproduction | `sulocraft-backups-preprod` | None (Private) | Preprod backup dump script (`database/preprod/...`) |

### Isolation Guarantees
1. **Dynamic Bucket Defaults**:
   - `backend/docker-compose.yml` defaults `R2_PUBLIC_BUCKET` to `sulocraft-products-${TARGET_ENV:-preprod}` and `R2_PRIVATE_BACKUP_BUCKET` to `sulocraft-backups-${TARGET_ENV:-preprod}`.
   - Preproduction environments never default to the production bucket `sulocraft-products`.
2. **Backup Script Isolation**:
   - `backend/scripts/backup_db.sh` prefixes object names by target environment: `database/${TARGET_ENV}/sulocraft_db_${TIMESTAMP}.sql.gz`.
   - Preprod backup executions target `sulocraft-backups-preprod`, preventing overwrite or deletion of production backups.
3. **Read Access vs Write Boundary**:
   - Preproduction storefront displays media via public CDN (`images.sulocraft.com`) using unauthenticated HTTPS GET requests.
   - Write/upload/delete operations use environment-scoped `R2_ACCESS_KEY_ID` and `R2_SECRET_ACCESS_KEY` credentials that must strictly limit write access to the preprod bucket.

## Dependencies and acceptance

Depends on 01 and 05. No asset copy, bucket creation, deletion, or credential change during discovery; changes require a reviewed migration plan.

# Task 12.06.1 — R2 Object Storage and Backup Isolation

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 012 / 06 R2/Storage Isolation

## Objective

Establish strict storage isolation between `PREPROD` and `PROD` so that preproduction tests, uploads, and automated database backups cannot write to, modify, overwrite, or delete production media assets or production backup snapshots.

## Context and contract

- Follow `work/12-vps-environment-isolation/README.md`, `architecture.md`, `decisions.md`, and `06-storage-r2/README.md`.
- Storage separation rules:
  - Production buckets: `sulocraft-products` (public media) and `sulocraft-backups` (private backups).
  - Preproduction buckets: `sulocraft-products-preprod` (or `sulocraft-products-dev`) and `sulocraft-backups-preprod` (or `sulocraft-backups-dev`).
  - Preprod credentials (`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`) must only grant access to preprod buckets.
  - Preprod read access: Storefront can display approved product images using the public CDN URL (`https://images.sulocraft.com` or `https://images-dev.sulocraft.com`), but preprod write/delete operations must never target the production bucket.
  - Backups: Must target environment-scoped private buckets (`sulocraft-backups-${TARGET_ENV}`).
- Local design and configuration only: do not create or delete live Cloudflare buckets without owner approval.

## Scope

- In scope:
  - Parameterize R2 bucket and backup settings in `backend/docker-compose.yml` dynamically based on `TARGET_ENV`.
  - Update `backend/scripts/backup_db.sh` to use environment-scoped backup bucket defaults.
  - Document R2 storage architecture, bucket policies, and credential scopes in `06-storage-r2/README.md`.
  - Add automated tests in `scripts/security/test_vps_isolation.py` proving preprod and prod resolve to separate buckets and backup destinations.
- Out of scope:
  - Live bucket creation or migration in Cloudflare dashboard.
  - Modifying live VPS backup scripts.

## Dependencies and relevant files

- Depends on: Work 012 Item 01 discovery, Item 05 secrets and config.
- Inspect/edit:
  - `backend/docker-compose.yml`
  - `backend/app/core/config.py`
  - `backend/scripts/backup_db.sh`
  - `scripts/security/test_vps_isolation.py`
  - `work/12-vps-environment-isolation/06-storage-r2/README.md`
  - `work/12-vps-environment-isolation/tasks.md`
  - `work/12-vps-environment-isolation/coordination.md`
  - `work/12-vps-environment-isolation/notes.md`

## Acceptance checks

- [x] Rendered Compose config for `preprod` and `prod` selects distinct `R2_PUBLIC_BUCKET` and `R2_PRIVATE_BACKUP_BUCKET` names.
- [x] Database backup logic targets an environment-scoped backup bucket and does not mix preprod and prod dumps.
- [x] Automated regression tests verify storage parameter isolation between environments (26/26 tests passing).
- [x] Local preprod API and storefront remain healthy.

## Handoff back

- Update `06-storage-r2/README.md`, `tasks.md`, `notes.md`, and `coordination.md`.
- Mark Task 12.06.1 Completed upon successful local verification.

## Pickup checklist

- [x] Read `work/INDEX.md`, this work item's `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm the task is assigned to you and change only this task's status to In Progress.
- [x] Reuse completed inputs documented here; do not repeat uploads, copies, migrations, or setup already marked complete.

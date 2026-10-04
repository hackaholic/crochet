# Task 12.10.1 — End-to-End Security & Isolation Validation

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 012 / 10 Security and Isolation Validation

## Objective

Deliver an automated, end-to-end security and isolation validation suite proving that PREPROD and PROD environments on the single VPS are strictly logically isolated across networks, databases, secrets, object storage, email delivery, and public ingress, while documenting shared-host residual risks and the migration path to physical VPS separation.

## Context and contract

- Reference: `work/work-012-vps-environment-isolation/README.md`, `architecture.md`, `decisions.md`, and `10-security-validation/README.md`.
- Target environment boundaries:
  - Container & Network: Disjoint Compose projects (`sulocraft-preprod` vs `sulocraft-prod`), private bridge networks (`sulocraft-preprod_internal` vs `sulocraft-prod_internal`), zero host-bound ports on app or DB, gateway network access restricted to APIs only.
  - Database: Distinct PostgreSQL volumes (`sulocraft-preprod_postgres_data` vs `sulocraft-prod_postgres_data`), isolated credentials, separate migrations.
  - Secrets: Disjoint mount paths (`/run/sulocraft/preprod/` vs `/run/sulocraft/prod/`), fail-closed bootstrap refusal on missing target secrets.
  - Storage: Distinct public R2 buckets (`sulocraft-products-preprod` vs `sulocraft-products-prod`), distinct private backup buckets (`sulocraft-backups-preprod` vs `sulocraft-backups-prod`), namespaced backup paths (`database/${TARGET_ENV}/...`).
  - Email: Fail-closed recipient sandbox suppressing external delivery in non-prod, allowlist bypass for `@sulocraft.com`, zero token leakage in logs.
  - Public Ingress: Only reverse proxy exposes 80/443; Caddy routes `api-dev.sulocraft.com` to `api-preprod:8000` and `api.sulocraft.com` to `api-prod:8000`.
- Shared-host reality: Logical isolation cannot prevent kernel compromise or catastrophic host outage from impacting both environments.

## Scope

- In scope:
  - Comprehensive automated security validation test suite (`scripts/security/test_vps_isolation.py` and dedicated security runners).
  - Validation of cross-environment network non-reachability, secret directory isolation, R2 bucket partition, and email sandbox enforcement.
  - Verification of no plaintext secrets or credentials in logs, test output, or committed config.
  - Complete documentation of shared-host residual risks and step-by-step procedure for migrating PROD to a dedicated VPS in the future.
  - Local verification gate and health checks.
- Out of scope:
  - Modifying live VPS or Cloudflare DNS during this task.
  - Attempting physical hardware isolation on a single VPS.

## Dependencies and relevant files

- Depends on: Work 012 Items 02, 03, 04, 05, 06, 07, 08.
- Inspect/edit:
  - `scripts/security/test_vps_isolation.py`
  - `scripts/security/scan-config.sh`
  - `work/work-012-vps-environment-isolation/10-security-validation/README.md`
  - `work/work-012-vps-environment-isolation/tasks.md`
  - `work/work-012-vps-environment-isolation/coordination.md`
  - `work/work-012-vps-environment-isolation/notes.md`

## Acceptance checks

- [x] Automated test suite verifies cross-environment isolation across:
  - Container project namespacing and volume isolation
  - Network segmentation (Postgres unreachable from gateway network and from peer environment)
  - Zero host ports on API and PostgreSQL
  - Target-scoped secret file paths with fail-closed resolution
  - Disjoint R2 public and backup buckets
  - Fail-closed email sandbox and domain callback URL resolution
  - Resource limits and log rotation caps
- [x] Config security scan passes all checks (`bash scripts/security/scan-config.sh`).
- [x] No credential or sensitive token leakage detected in logs or test outputs.
- [x] Residual shared-host risks (noisy neighbor, kernel panic, root compromise) and separate VPS migration path documented in `10-security-validation/README.md`.
- [x] Local preprod API and storefront remain healthy.

## Handoff back

- Update `10-security-validation/README.md`, `tasks.md`, `notes.md`, and `coordination.md`.
- Mark Task 12.10.1 Completed upon successful test verification.

## Pickup checklist

- [x] Read `work/INDEX.md`, this work item's `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm the task is assigned to you and change only this task's status to In Progress.
- [x] Reuse completed inputs documented here; do not repeat uploads, copies, migrations, or setup already marked complete.

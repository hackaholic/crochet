# Task 12.05.1 — Secret & Non-Secret Configuration Isolation

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 012 / 05 Secrets and Non-Secret Configuration

## Objective

Establish strict environment separation for secret and non-secret runtime configuration so that `PREPROD` and `PROD` run from distinct, isolated secret materialization directories (`/run/sulocraft/preprod` and `/run/sulocraft/prod`), fail closed if production encrypted groups are absent, and prevent any cross-environment credential leaks or fallbacks.

## Context and contract

- Follow `work/work-012-vps-environment-isolation/README.md`, `architecture.md`, `decisions.md`, and `05-secrets-config/README.md`.
- Environment parity & fail-closed security:
  - Preprod and production use the same Compose definition and bootstrap mechanisms.
  - Target environment determines secret materialization paths: `/run/sulocraft/${TARGET_ENV}/...`.
  - Non-preprod environments (`prod`) MUST fail closed if their dedicated encrypted directory does not exist; silent fallback to preprod credentials is strictly prohibited.
- Secret mapping:
  - Database (`postgres`): `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.
  - API Backend (`api`): `DATABASE_URL`, `SESSION_SECRET`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `RESEND_API_KEY`, `GOOGLE_CLIENT_SECRET`, `FACEBOOK_APP_SECRET`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`.
  - Backup: Database access credentials.
- No live production secrets are created or stored in this task.

## Scope

- In scope:
  - Parameterize default secret mount paths in `backend/docker-compose.yml` to `/run/sulocraft/${TARGET_ENV:-preprod}/...`.
  - Enforce fail-closed secret directory resolution in `backend/scripts/bootstrap_secrets.sh` for non-preprod environments.
  - Default `RUNTIME_SECRETS_DIR` in `backend/scripts/bootstrap_secrets.sh` to `/run/sulocraft/${TARGET_ENV}`.
  - Document secret matrix and rotation/recovery policy in `05-secrets-config/README.md`.
  - Add automated test assertions in `scripts/security/test_vps_isolation.py` proving secret path isolation and fail-closed resolution.
- Out of scope:
  - Generating live production secrets or age keys.
  - Deploying to live VPS.

## Dependencies and relevant files

- Depends on: Work 003 Tasks 3.13/3.14, Work 012 Items 01–03.
- Inspect/edit:
  - `backend/docker-compose.yml`
  - `backend/scripts/bootstrap_secrets.sh`
  - `.sops.yaml`
  - `scripts/security/test_vps_isolation.py`
  - `work/work-012-vps-environment-isolation/05-secrets-config/README.md`
  - `work/work-012-vps-environment-isolation/tasks.md`
  - `work/work-012-vps-environment-isolation/coordination.md`
  - `work/work-012-vps-environment-isolation/notes.md`

## Acceptance checks

- [x] Rendered Compose config for `preprod` and `prod` points to separate runtime secret paths (`/run/sulocraft/preprod/...` vs `/run/sulocraft/prod/...`).
- [x] `backend/scripts/bootstrap_secrets.sh` fails closed when run with `--env prod` without explicit prod encrypted directory.
- [x] Automated regression tests verify runtime secret directory isolation and fail-closed bootstrap behavior (21/21 security tests passing).
- [x] No plaintext secrets exist in tracked files or tests.
- [x] Local preprod API and storefront remain healthy.

## Handoff back

- Update `05-secrets-config/README.md`, `tasks.md`, `notes.md`, and `coordination.md`.
- Mark Task 12.05.1 Completed upon successful local verification.

## Pickup checklist

- [x] Read `work/INDEX.md`, this work item's `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm the task is assigned to you and change only this task's status to In Progress.
- [x] Reuse completed inputs documented here; do not repeat uploads, copies, migrations, or setup already marked complete.

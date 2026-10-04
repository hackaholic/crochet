# 05 — Secrets and non-secret configuration

**Status:** Pending — depends on 01 discovery; integrates Work 003.

## Goal

Use explicit environment configuration and isolated SOPS/age groups so PREPROD cannot receive PROD credentials.

## Subtasks

- [ ] Map every backend/PostgreSQL/backup secret to its environment and consumer.
- [ ] Confirm separate encrypted PROD and PREPROD secret groups and recipient/decrypt rules.
- [ ] Confirm session/signing/database credentials are distinct; identify OAuth, Resend, and R2 credential separation needs.
- [ ] Use validated environment config for `APP_ENV`, frontend/public API URLs, domains, paths, and deployment target.
- [ ] Prove missing/unknown target config fails closed and never falls back to another environment.
- [ ] Document rotation and recovery per environment.

## Dependencies and acceptance

Depends on Work 003, Tasks 3.13/3.14. Never put plaintext secrets in Git, CI logs, images, or the frontend. No production credentials are created as part of discovery.

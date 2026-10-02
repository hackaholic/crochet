# Task 6.3 — GitHub Actions CI/CD workflow hardening with protected secrets

**Owner:** Gemini
**Status:** Pending

## Objective

Harden the GitHub Actions continuous deployment workflow `.github/workflows/deploy.yml` to trigger on push to `dev`, execute backend and frontend test suites, back up the database on the VPS, transfer encrypted SOPS secrets, run Alembic migrations, and perform health checks before concluding.

## Context and contract

GitHub Actions secrets must only store SSH deployment credentials and SOPS encrypted group inputs. The age private key resides exclusively on the VPS at `/etc/sulocraft/age/keys.txt`.

## Scope

- In scope:
  - Run `pytest` and `npm test` as required build gates.
  - Automate SSH deployment execution to VPS.
  - Include automated pre-migration database snapshot.
  - Fail closed and abort if health check fails.
- Out of scope:
  - Production `main` branch deployment (restricted to manual release tags).

## Dependencies and relevant files

- Depends on: Work 003 SOPS/age vault.
- Inspect/edit:
  - `.github/workflows/deploy.yml`
  - `backend/scripts/deploy_vps.sh`

## Acceptance checks

- [ ] A test commit pushed to `dev` triggers the action, runs all tests, and executes deployment.
- [ ] Pipeline aborts cleanly if any test fails, without modifying VPS state.

## Handoff back

- Update `work/work-006-dns-email-cd/tasks.md` and `notes.md`.

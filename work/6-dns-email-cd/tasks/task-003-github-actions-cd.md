# Task 6.3 — GitHub Actions CI/CD workflow hardening with protected secrets

**Owner:** Gemini
**Status:** Pending

## Objective

Harden the GitHub Actions workflow `.github/workflows/deploy.yml` to trigger the preprod stage on push to `dev` only after backend/frontend test gates pass, then invoke the shared Work 012 deployment command with protected environment configuration. The reusable deploy command owns backups, encrypted SOPS bootstrap, migrations, activation, health checks, and failure recovery. Production promotion is a separate gated action after preprod stability is accepted.

## Context and contract

GitHub Actions secrets must only store SSH deployment credentials and non-secret deployment configuration; encrypted SOPS groups are versioned with the application. The age private key resides exclusively on the VPS at `/etc/sulocraft/age/keys.txt`. Follow local → preprod → production gates and promote the same tested revision/artifact.

## Scope

- In scope:
  - Run `pytest` and `npm test` as required build gates.
  - Pass protected SSH and environment configuration to the shared Work 012 deployment command.
  - Abort before deployment if tests or required configuration fail.
- Out of scope:
  - Production `main` branch deployment (restricted to manual release tags).

## Dependencies and relevant files

- Depends on: Work 003 SOPS/age vault and Work 012 reusable VPS deployment command.
- Inspect/edit:
  - `.github/workflows/deploy.yml`
  - Work 012 `./deploy_vps.sh` interface

## Acceptance checks

- [ ] A test commit pushed to `dev` triggers the action, runs all tests, and executes deployment.
- [ ] Pipeline aborts cleanly if any test fails, without modifying VPS state.

## Handoff back

- Update `work/6-dns-email-cd/tasks.md` and `notes.md`.

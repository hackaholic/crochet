# Task 6.3 — GitHub Actions CI/CD workflow hardening with protected secrets

**Owner:** Gemini
**Status:** In Progress
**Work item:** Work 006 / Continuous deployment

## Objective

Harden the GitHub Actions workflow `.github/workflows/deploy-dev-backend.yml` to trigger the preprod stage on push to `dev` only after backend test gates pass, then invoke the shared deployment command with protected environment configuration. The deployment command owns backups, encrypted SOPS bootstrap via the VPS host age key, migrations, activation, health checks, and failure recovery.

## Context and contract

GitHub Actions secrets must only store SSH deployment credentials (`VPS_SSH_PRIVATE_KEY`, `VPS_KNOWN_HOSTS`, `VPS_HOST`, `VPS_USER`). Encrypted SOPS groups are versioned in git with the application under `secrets/encrypted/`. The age private key resides exclusively on the VPS at `/etc/sulocraft/age/keys.txt`. No plaintext `.env` files are stored in GitHub Secrets.

## Subtasks

- [x] **6.3.1 — Document SSH deployment credential setup & inventory**:
  - Clarified SSH key direction: GitHub Actions runner is SSH client; VPS is SSH server.
  - Public key (`id_ed25519.pub`) added to VPS `~/.ssh/authorized_keys`.
  - Private key (`id_ed25519`) stored in GitHub Repository Secrets as `VPS_SSH_PRIVATE_KEY`.
  - Host key stored as `VPS_KNOWN_HOSTS` via `ssh-keyscan`.
  - Connection parameters: `VPS_HOST` and `VPS_USER`.
- [ ] **6.3.2 — Modernize `.github/workflows/deploy-dev-backend.yml`**:
  - Replace legacy plaintext `PREPROD_ENV_FILE` injection with SOPS/age encrypted secrets bootstrap.
  - Invoke `backend/scripts/deploy_vps.sh --env preprod --host "${VPS_USER}@${VPS_HOST}"`.
  - Add fail-closed secret validation in the SSH configuration step.
- [ ] **6.3.3 — Enforce test gate before deployment**:
  - Use `astral-sh/setup-uv` for fast, cached backend dependency management.
  - Require all unit and integration tests to pass before triggering the deploy job (`needs: test`).
- [ ] **6.3.4 — Post-deployment health verification**:
  - Verify container status and API `/health` endpoint after deployment.
  - Ensure failure triggers automatic rollback and leaves previous release symlink intact.

## Dependencies and relevant files

- Depends on: Work 003 SOPS/age vault and Work 012 VPS environment isolation.
- Inspect/edit:
  - `.github/workflows/deploy-dev-backend.yml`
  - `backend/scripts/deploy_vps.sh`
  - `work/work-006-dns-email-cd/`

## Acceptance checks

- [ ] GitHub Actions workflow does not require plaintext secrets or `.env` files in GitHub Secrets.
- [ ] Push to `dev` triggers the action, runs all tests, and executes preprod deployment.
- [ ] Pipeline aborts cleanly if any test fails, without modifying VPS state.
- [ ] SSH private key is never printed or logged during workflow execution.

## Handoff back

- Update `work/work-006-dns-email-cd/tasks.md`, `coordination.md`, and `notes.md`.

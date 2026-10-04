# Task 12.09.6 — CI/CD alignment and operator deployment interface

**Owner:** Codex
**Status:** Completed
**Work item:** Work 012 / 09 Deployment workflow

## Objective

Document the operator CLI deployment interface and provide a clean, stable contract for Work 006 CI/CD workflows to invoke `./deploy_vps.sh --env preprod` and `./deploy_vps.sh --env prod --release-id <release_id>` without duplicating build, release packaging, or promotion logic.

## Context and contract

- Work 012 owns environment isolation, Compose configuration, deployment CLI (`./deploy_vps.sh`), and same-artifact promotion.
- Work 006 owns CI pipeline triggers and workflow policy (`.github/workflows/deploy-dev-backend.yml`).
- Work 012 provides a single entry point:
  - `./deploy_vps.sh --env preprod`: builds local release, verifies health, rsyncs archive to VPS, restores/migrates DB, verifies `https://api-dev.sulocraft.com/health`.
  - `./deploy_vps.sh --env prod --release-id <id>`: takes existing release artifact tested in PREPROD and promotes to PROD with fail-closed production secrets check.
- Work 006 CI workflows call these commands and pass credentials via environment variables or SOPS/Age keys as documented in `docs/github-actions-ssh-setup.md`.

## Scope

- In scope: Contract definition for CI invocation, documentation of CLI arguments and environment variables, verification that `./deploy_vps.sh` satisfies CI runner requirements.
- Out of scope: Modifying Work 006's active pipeline files or creating new GitHub workflow triggers.

## Acceptance checks

- [x] Standardized CLI interface is documented in `docs/` and Work 012 item 09 README.
- [x] Automated CLI flags (`--help`, `--env`, `--release-id`, `--promote`, `--verified-commit`, `--dry-run`) provide explicit error messages on missing or invalid arguments.
- [x] CI runner compatibility: runs non-interactively, logs structured output, exits with status 0 on success and non-zero on error.
- [x] Release artifact is self-contained in `.deploy/releases/<release_id>/` with `manifest.json` and `api-image.tar`.

## Handoff back

- Work 006 can reference `./deploy_vps.sh` as the single canonical deployment runner.
- Documented in Work 012 item 09 tasks and README.

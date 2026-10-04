# Task 12.09.2 — Required environment selection and deployment config

**Owner:** Codex
**Status:** Completed
**Work item:** Work 012 / 09 Deployment workflow

## Objective

Make the root deployment entry point select PREPROD or PROD only through an explicit `--env` argument and resolve target-specific deployment settings without silently defaulting or crossing environment boundaries.

## Context and contract

- Follow [Work 012](../../README.md), [deployment workflow](../README.md), [architecture](../../architecture.md), and [decision DEC-012-007](../../decisions.md#dec-012-007--one-deploy-command-with-an-explicit-environment-target).
- Final operator commands are `./deploy_vps.sh --env preprod` and `./deploy_vps.sh --env prod`.
- PREPROD serves `dev.sulocraft.com` and uses `api-dev.sulocraft.com`; PROD uses the production hostnames.
- One VPS and the existing `/opt/sulocraft` layout are retained. Each environment still has its own Compose project, data volume, network, runtime-secret directory, and encrypted secret group.
- The currently installed local Compose command is `docker-compose`; use it for local Compose configuration checks.
- Deployment configuration is YAML. Runtime secrets remain in encrypted SOPS groups, never in the YAML file.
- Do not push or deploy to the VPS as part of this subtask.

## Scope

- In scope: explicit target parsing, safe config loading/validation, target-to-stack mapping, dry preflight output, and focused tests.
- Out of scope: remote rsync/SSH execution, actual Compose up, database cutover, production secret creation, CI workflow edits, and live deployment.

## Dependencies and relevant files

- Depends on completed Work 012 items 01–08 and 10 plus Work 003 secret bootstrap contracts.
- Inspect/edit: `deploy_vps.sh`, `scripts/deploy_vps.py`, `backend/docker-compose.yml`, `backend/tests/test_vps_release_artifact.py`, this Work 012 folder, and the deployment runbook.

## Acceptance checks

- [x] Missing or unknown `--env` is rejected before any filesystem, SSH, or Docker mutation.
- [x] `preprod` resolves only `sulocraft-preprod`, `/run/sulocraft/preprod`, and the PREPROD encrypted group; PROD resolves only its own path and fails closed while its encrypted group is absent.
- [x] Host, paths, SSH settings, runtime secret root, public URLs, and Compose settings are read from YAML config; secret values are excluded from output.
- [x] Preflight reports the selected environment and missing prerequisites without deploying.
- [x] Focused tests pass; `docker-compose config --quiet` validates both target definitions with disposable secret paths.
- [x] No Git push or VPS/Cloudflare state change occurred.

## Handoff back

- Update Work 012 item 09, `tasks.md`, `notes.md`, and `coordination.md` with verification and remaining work.
- Keep remote transfer/deployment as the next bounded subtask; do not claim end-to-end automation is ready after preflight alone.
- Leave credentials/private data out of logs and handoff notes.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 012 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm this task is assigned to Codex and mark only it In Progress.
- [x] Reuse completed isolation and secret-bootstrap work; do not repeat setup or modify VPS state.

## Result

- Root `./deploy_vps.sh` now requires `--env preprod|prod` and includes a no-mutation `--preflight` mode.
- Added `deploy/vps-config.example.yaml` and local ignored `.deploy/vps-config.yaml`. PREPROD uses the existing encrypted SOPS group directory; PROD maps to a dedicated directory and fails closed because its files are not provisioned.
- Verification: 13 focused tests pass; `docker-compose config --quiet` passes for both Compose project targets; `bash -n`, `py_compile`, and `git diff --check` pass.
- This validates configuration only; remote deployment is not yet implemented.

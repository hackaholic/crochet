# Task 3.14 — Make vault deployment environment-configurable

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 003

## Objective

Make secret decryption and deployment select the target environment at runtime. Preprod must use the same application code, deployment workflow, service topology, and security controls intended for production, so production promotion requires configuration/credential selection only.

## Context and contract

- Follow the [Work 003 README](../README.md), [task list](../tasks.md), [decisions](../decisions.md), and the [Gemini workflow](../../GEMINI_WORKFLOW_PROMPT.md).
- Owner requirement: deployment environment and paths must be configurable through an explicit config/env file or command-line argument. Do not hard-code a preprod-only file, directory, host, or runtime path in deployment logic.
- Environment parity decision: `preprod` is the production rehearsal. Do not create a separate code path, Compose architecture, or manual procedure for production. Differences are explicit environment configuration and that environment's encrypted secrets. Production must fail closed if its configuration or secret groups are missing; it must never fall back to preprod values.
- Current authorized secret groups are encrypted preprod inputs at `secrets/encrypted/{backend,postgres,backup}.enc.env`. Reuse and verify them; do not decrypt into tracked files, invent production credentials, or repeat key setup.

## Scope

- In scope: define a single environment selection/configuration interface for local decrypt and VPS deployment; support a named target (currently `preprod`) selected from CLI, environment variables, or an explicitly supplied config file; configure secret-group directory, runtime secret directory, VPS host/root, age key path, and Compose inputs; validate required values and reject unknown environments; keep secrets out of logs; add tests using temporary configuration and dummy encrypted groups; update the runbook and this work's state.
- Out of scope: creating production secrets, rotating live credentials, changing DNS, or deploying/activating production.

## Dependencies and relevant files

- Depends on: Tasks 3.3, 3.8, 3.12, and 3.13.
- Inspect/edit: `scripts/decrypt_preprod_secrets.py`, `scripts/decrypt_secrets.py`, `docker/compose.preprod.yaml`, `backend/scripts/bootstrap_secrets.sh`, `backend/scripts/deploy_vps.sh`, `backend/scripts/rotate_vps_key.sh`, `.gitignore`, `docs/secrets.md`, and focused tests.

## Acceptance checks

- [x] The selected environment is not hard-coded as `preprod` in helper/deploy logic; CLI/environment/config selection works and has documented precedence (`--env`, `--config`, `SULOCRAFT_ENV`, `APP_ENV`).
- [x] A supplied config/env file can select the current preprod encrypted groups and local runtime paths; no static `.env.preprod` filename is required by the scripts.
- [x] The same deployment entry point, application artifact, and service topology can be selected for preprod and prod by configuration only; prod cannot silently fall back to preprod paths or secrets.
- [x] Missing/unknown environment or required path fails closed before decryption or deployment; no secret values are printed.
- [x] Tests cover config/argument/environment selection and prove one environment's secret paths cannot be silently reused for another (`scripts/security/test_decrypt_secrets.py`).
- [x] Existing preprod encrypted groups still decrypt and local Compose startup works with the chosen runtime configuration.
- [x] No VPS deploy is performed; Codex owns final integrated local review and Task 3.10 release.

## Completion details

- Created `scripts/decrypt_secrets.py` supporting `--env <preprod|dev|prod>`, `--config <path>`, and resolution hierarchy (CLI > config file > environment variable > default).
- Implemented strict fail-closed cross-environment isolation: non-preprod environments require dedicated encrypted directories and fail closed if missing.
- Updated `scripts/decrypt_preprod_secrets.py` as a backward-compatible wrapper delegating to `decrypt_secrets.py --env preprod`.
- Updated `backend/scripts/bootstrap_secrets.sh` and `backend/scripts/deploy_vps.sh` to accept `--env <env>`, resolve environment-specific directories, and forward the target environment without hardcoding preprod.
- Added comprehensive unit and regression tests in `scripts/security/test_decrypt_secrets.py` (5/5 passing). Updated `docs/secrets.md`.

## Handoff back

- Update this task's status, Work 003 `tasks.md`, `notes.md`, and `coordination.md` with exact commands/results and blockers.
- Return the exact runtime config example and command for the current preprod deployment without including credential values.
- Leave credentials/private data out of logs and handoff notes.

## Pickup checklist

- [ ] Read `work/INDEX.md`, this work item's `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [ ] Confirm the task is assigned to you and change only this task's status to In Progress after Task 3.13 is returned.
- [ ] Reuse the existing encrypted preprod groups and key recipients; do not repeat setup.

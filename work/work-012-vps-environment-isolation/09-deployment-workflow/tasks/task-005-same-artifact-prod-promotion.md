# Task 12.09.5 — Same-artifact PROD promotion CLI with fail-closed configuration

**Owner:** Codex
**Status:** Completed
**Work item:** Work 012 / 09 Deployment workflow

## Objective

Implement same-artifact PROD promotion CLI semantics (`./deploy_vps.sh --env prod [--release-id <release_id>] [--promote]`) that guarantees the exact immutable image tar and manifest tested in PREPROD are deployed to PROD without rebuild, while enforcing fail-closed checks on required production secrets and target configuration.

## Context and contract

- Follow `work/work-012-vps-environment-isolation/README.md`, `architecture.md`, `09-deployment-workflow/README.md`, and `decisions.md` (DEC-012-002, DEC-012-007).
- Deployment must use one immutable image ID/tag based on commit SHA in PREPROD and PROD; never rebuild from source for PROD.
- Keep the local → preprod → production gate: locally tested, preprod tested/stable, then explicit production promotion.
- Production promotion changes config and secrets only; never introduce preprod-only code paths.
- Enforce fail-closed security: missing production secrets (`secrets/encrypted/prod/backend.enc.env` and `postgres.enc.env`) or missing target configurations MUST immediately abort deployment before network transfer or host mutation.

## Scope

- In scope: CLI flag parsing for `--release-id` and `--promote`, release artifact verification (manifest schema, tar checksum SHA-256), fail-closed production secret verification, target runtime env rendering with `API_IMAGE=sulocraft-api:<release_id>`, automated promotion regression tests.
- Out of scope: Live production cutover, DNS changes for `api.sulocraft.com`, generating production secrets.

## Dependencies and relevant files

- Depends on Tasks 12.09.2, 12.09.3, and 12.09.4.
- Code modified: `scripts/deploy_vps.py`
- Tests added: `backend/tests/test_vps_release_artifact.py`

## Acceptance checks

- [x] CLI supports `--env prod` with optional `--release-id` or `--promote`.
- [x] Deployment validates presence and integrity of prepared release directory `.deploy/releases/<release_id>/` and `manifest.json`.
- [x] Artifact SHA-256 in manifest is verified against `api-image.tar`.
- [x] Environment resolution fails closed with `ReleaseError` if `secrets/encrypted/prod` lacks required encrypted env files.
- [x] Target runtime environment is rendered with `API_IMAGE=sulocraft-api:<release_id>`.
- [x] Re-run proof: no Docker build command is executed during PROD promotion; the pre-built tar archive is transferred and loaded directly.
- [x] Automated unit tests in `backend/tests/test_vps_release_artifact.py` verify same-artifact reuse and fail-closed secret enforcement.

## Handoff back

- Updated `scripts/deploy_vps.py` and `backend/tests/test_vps_release_artifact.py`.
- Verified 12/12 passing tests in `backend/tests/test_vps_release_artifact.py`.

# Task 12.09.3 — Locally verified immutable API release artifact

**Owner:** Codex
**Status:** Completed
**Work item:** Work 012 / 09 Deployment workflow

## Objective

Build the API image locally for `linux/amd64`, identify it by the verified source revision, and package it with an integrity manifest so PREPROD and PROD can run the same image without rebuilding on the VPS.

## Context and contract

- Follow [Work 012](../../README.md), [deployment workflow](../README.md), [DEC-012-002](../../decisions.md#dec-012-002--preserve-the-three-stage-release-gate), and [Task 12.09.2](task-002-target-config-preflight.md).
- Final operator commands are `./deploy_vps.sh --env preprod` and `./deploy_vps.sh --env prod`.
- Local build and verification must precede any PREPROD deployment. PROD promotes the same accepted image; no VPS-side source build or Git clone.
- The repository may be dirty during PREPROD development. Include a deterministic source-tree fingerprint in the release ID and manifest so distinct working trees cannot overwrite one another; never reuse a release after its source fingerprint changes. PROD must promote only a PREPROD-accepted immutable image.

## Scope

- In scope: clean-source verification, local image build with Docker, archive and SHA-256 manifest integrity, release reuse, and tests.
- Out of scope: VPS rsync/SSH, Compose rollout, DB cutover, PROD secrets, Git push, and live deployment.

## Dependencies and relevant files

- Depends on Task 12.09.2, the Dockerfile, Compose configuration, and passing backend/local storefront verification.
- Inspect/edit: `scripts/deploy_vps.py`, root `deploy_vps.sh`, `backend/docker-compose.yml`, `backend/tests/test_vps_release_artifact.py`, and Work 012 item 09 docs.

## Acceptance checks

- [x] Build is refused for a mismatched verified base revision; dirty changes are fingerprinted in the release ID and manifest.
- [x] Docker image is built locally for `linux/amd64`; the Docker daemon completes the build.
- [x] Archive, image ID, source revision, and SHA-256 are recorded and validated on reuse.
- [x] Focused deployment tests and local API/storefront verification pass.
- [x] No Git push or Cloudflare change occurred as part of artifact preparation. VPS rollout was performed separately under Task 12.09.4.

## Handoff back

- Update Work 012 item 09, `tasks.md`, `notes.md`, and `coordination.md` with verification and remaining work.
- Next task is remote PREPROD delivery of this artifact with backup, health gate, and rollback.
- Leave credentials/private data out of logs and handoff notes.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 012 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm this task is assigned to Codex and mark only it In Progress.
- [x] Do not repeat target-config/preflight work from Task 12.09.2.

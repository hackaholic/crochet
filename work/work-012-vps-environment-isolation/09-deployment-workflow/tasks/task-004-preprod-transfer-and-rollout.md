# Task 12.09.4 — Transfer and deploy PREPROD release

**Owner:** Codex
**Status:** Completed
**Work item:** Work 012 / 09 Deployment workflow

## Objective

Make `./deploy_vps.sh --env preprod` transfer the locally verified immutable API image to `/opt/sulocraft`, preserve and import the existing PREPROD database on first cutover, then activate and health-check the isolated PREPROD Compose project with rollback available.

## Context and contract

- Follow [Work 012](../../README.md), [deployment workflow](../README.md), and [DEC-012-002](../../decisions.md#dec-012-002--preserve-the-three-stage-release-gate) through [DEC-012-007](../../decisions.md#dec-012-007--one-deploy-command-with-an-explicit-environment-target).
- The only operator entry point is `./deploy_vps.sh --env preprod`; helper scripts are implementation details and must not require separate operator invocation.
- Deployment target settings are read from YAML `.deploy/vps-config.yaml`. GitHub Actions SSH secrets are not needed by the local command; local SSH identity/known-host settings come from this YAML config.
- The current Caddy route on the VPS uses the `api` gateway alias. Keep this route working while connecting the proxy to the configured shared gateway network.
- Existing PREPROD database volume and backup must remain recoverable. The first isolated deployment restores the legacy database; later deployments back up the active isolated database and reuse its target-scoped volume.
- PROD stays fail-closed until its dedicated encrypted secret groups and same-artifact promotion task are complete.

## Scope

- In scope: rsync of the source release and image archive, artifact checksum validation, secret bootstrap from the existing SOPS/age interface, gateway attachment, target-scoped Compose rollout, first-cutover DB restore, subsequent-release DB backup, health checks, and rollback.
- Out of scope: Git push, Cloudflare changes, production deployment, and changing the VPS deployment root or owner.

## Dependencies and relevant files

- Depends on Tasks 12.09.2 and 12.09.3, Work 003's existing secret bootstrap, Work 012 items 02–08, local Docker/browser/API verification, and explicit owner authorization for this preprod rollout.
- Inspect/edit: `deploy_vps.sh`, `scripts/deploy_vps.py`, `scripts/deploy_vps_remote.sh`, `.deploy/vps-config.yaml`, `deploy/vps-config.example.yaml`, `backend/docker-compose.yml`, and deployment tests/docs.

## Acceptance checks

- [x] `./deploy_vps.sh --env preprod` is the only operator command; SSH/rsync helper remains internal.
- [x] YAML config selects host, `/opt/sulocraft`, runtime secret root, gateway network/alias, URLs, and encrypted secret groups.
- [x] Focused release, isolation, and secret-bootstrap tests pass; PREPROD Compose configuration validates.
- [x] Local API health and storefront rendering were verified before transfer.
- [x] VPS verified the archive checksum and created mode-0600 database backup `/opt/sulocraft/backups/predeploy_preprod_d27b8d5da01b-9a161e68c2c6.sql.gz`; preserved the legacy volume and restored its data into the isolated PREPROD volume.
- [x] PREPROD API/PostgreSQL containers are healthy; `https://api-dev.sulocraft.com/health` and `https://dev.sulocraft.com/` pass. Active release pointer changed after health checks.
- [x] Rollout logic recognizes the isolated target project on repeat deployments and backs up that target DB before replacement.
- [x] No Git push, Cloudflare update, or PROD change occurred.

## Handoff back

- Update Work 012 item 09, `tasks.md`, `notes.md`, and `coordination.md` with deployment result, release ID, safe verification details, and remaining blockers.
- Do not record secret values, private key contents, or database contents.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 012 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and the active release-artifact contract.
- [x] Confirm Codex owns this task and mark only this task In Progress.
- [x] Reuse the existing SOPS/age key and encrypted PREPROD groups; do not repeat vault setup.
- [x] Local Docker/browser/API checks pass; VPS cutover is complete and externally verified.

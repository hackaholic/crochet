# 09 — Deployment workflow

**Status:** Pending — depends on 01–08 design and Work 003 vault integration.

## Goal

Deploy isolated environments with one reusable, configurable command and enforce local → preprod → production gates.

## Subtasks

- [ ] Inspect existing `backend/scripts/deploy_vps.sh`, config/secret interfaces, Compose files, GitHub workflow, release paths, and rollback behavior.
- [ ] Define a root-level command that deploys only a locally verified, clean, committed revision to an explicit target.
- [ ] Build/tag an immutable backend image by commit SHA and preserve that exact image for preprod testing and production promotion; never use `latest`.
- [ ] Use encrypted target-specific secrets and environment config; do not clone from GitHub on the VPS or transfer plaintext `.env` files.
- [ ] Back up the selected environment DB, migrate only that DB, health-check, and activate with rollback to the previous image on failure.
- [ ] Add tests/fake remote for target selection, environment boundaries, image identity, secret exclusion, and failure handling.
- [ ] Have Work 006 CI invoke this deployment interface after required local/CI gates rather than duplicate deployment logic.
- [ ] Document three promotion phases and production promotion of the same tested image by config/secrets only.

## Dependencies and acceptance

Depends on 01–08, Work 003 Tasks 3.13/3.14, and the three-phase project rule. Live preprod/prod actions happen only after acceptance and explicit owner authorization.

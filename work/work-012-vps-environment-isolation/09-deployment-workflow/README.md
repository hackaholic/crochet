# 09 — Deployment workflow

**Status:** Completed — PREPROD transfer and rollout verified; same-artifact PROD promotion CLI with fail-closed secrets implemented ([Task 12.09.5](tasks/task-005-same-artifact-prod-promotion.md)); CI/CD alignment documented ([Task 12.09.6](tasks/task-006-ci-alignment.md)).

## Goal

Deploy isolated environments with one reusable, configurable command and enforce local → preprod → production gates.

## Required operator interface

```bash
./deploy_vps.sh --env preprod   # PREPROD, serving dev.sulocraft.com
./deploy_vps.sh --env prod      # promote the accepted PREPROD image to production
```

`--env` is required and accepts only `preprod` or `prod`; it must never default to an environment. The command uses one image for both environments and selects each environment's Compose project, database, networks, runtime secrets, and deployment settings from validated configuration. Production promotion must fail unless the exact image has already passed local verification and PREPROD acceptance.

## Subtasks

- [x] 09.1 — Inspect current deploy script, secret/config interfaces, Compose, CI, release paths, rollback, and docs. Result: rsync + target-scoped Compose/bootstrap and health checks exist, but the VPS still builds the app and there is no proven same-artifact promotion gate.
- [x] 09.2 — Required `--env` selection, YAML target config, and no-mutation preflight implemented and tested. Contract: [Task 12.09.2](tasks/task-002-target-config-preflight.md).
- [x] 09.3 — Build and locally verify a commit-tagged immutable API image and checksum manifest, then prepare the transfer package. Contract: [Task 12.09.3](tasks/task-003-local-release-artifact.md).
- [x] 09.4 — Transfer and deploy to PREPROD using target-scoped secrets/config, DB backup/restore, health gate, and safe app rollback. Contract: [Task 12.09.4](tasks/task-004-preprod-transfer-and-rollout.md). Live release `d27b8d5da01b-9a161e68c2c6` is healthy at `api-dev.sulocraft.com`; see Work 012 notes.
- [x] 09.5 — Promote the exact accepted PREPROD image to PROD; production may change environment config/secrets only. Contract: [Task 12.09.5](tasks/task-005-same-artifact-prod-promotion.md).
- [x] 09.6 — Document operator use and provide the stable interface to Work 006 CI; do not change Work 006-owned workflows in this task. Contract: [Task 12.09.6](tasks/task-006-ci-alignment.md).
- [x] Existing safeguard — deployment DB backup reads credentials from mounted Docker secret files and aborts safely if backup generation fails.

## Dependencies and acceptance

Depends on Work 01 discovery, Work 003's documented SOPS/age interface, Work 012 isolation interfaces, and the three-phase project rule. Live preprod/prod actions happen only after acceptance and explicit owner authorization.

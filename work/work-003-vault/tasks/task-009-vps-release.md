# Task 3.10 — VPS release scope moved to Work 012

**Owner:** Codex
**Status:** Moved — VPS deployment is a separate work item
**Work item:** Work 003 (historical pointer)

## Scope correction

Work 003 owns the SOPS/age vault, encrypted secret groups, local decrypt behavior, and key safety. It does not own VPS deployment orchestration. VPS preflight, source selection, backups, migrations, health checks, rollback, and the one-command deploy flow are tracked in [Work 012 Task 12.1](../../vps-environment-isolation/09-deployment-workflow/tasks/task-001-one-command-promotion.md). Work 006 owns GitHub Actions trigger/CI configuration and will call the Work 012 command.

Do not implement deployment from this historical pointer; use the linked Work 012 contract.

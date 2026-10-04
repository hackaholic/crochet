# Work 012 — PROD/PREPROD isolation task status

## Completed

- [x] 01 — Current-state discovery; documented repo and read-only VPS baseline, owner confirmed `api-dev.sulocraft.com` for PREPROD.
- [x] 02 — Container isolation: [Task 12.02.1](02-container-isolation/tasks/task-001-container-isolation.md) (Gemini); parameterized Compose runtime with dynamic project scoping (`sulocraft-prod` and `sulocraft-preprod`), decoupled reverse proxy gateway (`docker/compose.proxy.yaml`), and automated regression tests in `scripts/security/test_vps_isolation.py`.
- [x] 03 — Networking and reverse-proxy routing: [Task 12.03.1](03-networking-proxy/tasks/task-001-networking-proxy.md) (Gemini); least-privilege Docker network segmentation (`sulocraft-gateway` vs private `internal`), validated `docker/Caddyfile` with automated Caddy 2 CLI validation, security headers, and domain routing (`api.sulocraft.com` & `api-dev.sulocraft.com`).
- [x] 04 — Database and persistent-volume isolation: [Task 12.04.1](04-database-isolation/tasks/task-001-db-isolation-audit.md), [Task 12.04.2](04-database-isolation/tasks/task-002-db-runtime-isolation.md) (Codex); distinct target-scoped secret paths, Compose projects and volumes; API/database credential consistency validation; independent disposable migrations.
- [x] 05 — Secret and non-secret configuration isolation: [Task 12.05.1](05-secrets-config/tasks/task-001-secrets-config-isolation.md) (Gemini); runtime secret paths, fail-closed bootstrap resolution, and credential inventory.

- [x] 06 — R2/storage isolation: [Task 12.06.1](06-storage-r2/tasks/task-001-storage-isolation.md) (Gemini); dynamic bucket defaults (`sulocraft-products-${TARGET_ENV:-preprod}`, `sulocraft-backups-${TARGET_ENV:-preprod}`), environment-scoped backup script object paths, and automated tests.
- [x] 07 — Email and OAuth isolation: [Task 12.07.1](07-email-oauth-isolation/tasks/task-001-email-oauth-isolation.md) (Gemini); fail-closed email sandbox recipient allowlist (`@sulocraft.com`), suppression logging without credential leak, redirect mailbox support, and dynamic domain/OAuth callback resolution (`dev.sulocraft.com` / `api-dev.sulocraft.com` vs `sulocraft.com` / `api.sulocraft.com`).
- [x] 08 — Resource limits and environment-aware logging: [Task 12.08.1](08-resource-limits/tasks/task-001-resource-limits-logging.md) (Gemini); CPU/memory/pids limits in Compose, json-file log rotation (10m/3), and structured logging with environment identification.
- [x] 10 — Security/isolation validation: [Task 12.10.1](10-security-validation/tasks/task-001-security-isolation-validation.md) (Gemini); automated test suite validating multi-environment network, secret, DB, storage, and email boundaries.

## In Progress

- [ ] 09 — Deployment workflow and same-artifact promotion: Tasks [12.09.2](09-deployment-workflow/tasks/task-002-target-config-preflight.md), [12.09.3](09-deployment-workflow/tasks/task-003-local-release-artifact.md), and [12.09.4](09-deployment-workflow/tasks/task-004-preprod-transfer-and-rollout.md) are complete. PREPROD is deployed and healthy; exact-image PROD promotion (12.09.5) and Work 006 CI alignment (12.09.6) remain.

## Pending

- [ ] 11 — Cutover and operational validation

## Blocked

- No current blocker. Production remains unable to start until its own encrypted secret groups/config are provisioned; live database cutover and restore validation belong to item 11.

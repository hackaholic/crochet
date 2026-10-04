# Work 003 coordination

This file is the work-local coordination entry point. The work folder is the source of truth: read this file with README.md, tasks.md, decisions.md, and only the assigned task contract.

## Current handoffs

- **Returned by Gemini:** [Task 3.13 — Isolate backend tests from shared development databases](tasks/task-013-isolate-backend-test-database.md), [Task 3.14 — Make vault deployment environment-configurable](tasks/task-014-configurable-deployment-environments.md), [Task 3.11 — Idempotent catalogue seed associations](tasks/task-011-seed-idempotency.md), [Task 3.6 — Safe VPS age-key bootstrap](tasks/task-005-vps-key-bootstrap.md), [Task 3.3 — VPS secret bootstrap and deploy](tasks/task-003-vps-deploy.md), [Task 3.7 — Guarded age-key rotation](tasks/task-006-age-key-rotation.md), and [Task 3.4 — Vault/deploy regression tests](tasks/task-004-vault-tests.md). Gemini completed Task 3.13 with fail-closed DB protection, dynamic fixture tracking, disposable container runner `backend/scripts/run_isolated_tests.sh`, and 100% full-suite passing (173/173 tests) without touching preprod data.
- **Completed (Codex):** [Task 3.8 — SOPS recipients and encrypted preprod groups](tasks/task-007-sops-encryption.md); SOPS groups decrypt with both authorized keys. Task 3.5 is complete (`anu:anu` mode `0600`).
- **Completed (Codex + Gemini):** [Task 3.9 — Local Docker rebuild and verification](tasks/task-008-seed-repair-verification.md). API and PostgreSQL are healthy, frontend runs cleanly, `/health` and storefront endpoints return HTTP 200, and seed idempotency is verified.
- **Codex integration:** [Task 3.2 — Local preprod decrypt helper](tasks/task-002-local-preprod-decrypt.md) is complete. [Task 3.10 — Encrypted preprod release](tasks/task-009-vps-release.md) depends on Work 012's deployment interface at [Task 12.1](../vps-environment-isolation/09-deployment-workflow/tasks/task-001-one-command-promotion.md).

## Return protocol

The assigned agent updates the exact contract, tasks.md, notes.md, and this file before returning the task. The global registry at docs/handoffs.md points here; it does not duplicate this work's status.

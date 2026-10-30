# Task 26.4 — Prove configuration parity and update runbooks

**Owner:** Codex  
**Status:** Completed
**Work item:** Work 026

## Objective

Prove the same application setting is resolved consistently from local direct environment values and preprod/prod SOPS-rendered files, and document the safe local/preprod/prod commands.

## Context and contract

- Follow Work 026 README/tasks/decisions and Tasks 26.1–26.3.
- This is an integration/acceptance task; do not duplicate implementation or repeat secret provisioning.
- No deployment is authorized by this task. Local verification must pass before any future preprod deployment.

## Scope

- In scope: parity/failure-isolation tests, safe Compose config render checks, runbook updates in the relevant secret/deployment docs, local Docker/API checks.
- Out of scope: connecting to or changing the VPS, promoting production, printing secrets, UI redesign.

## Dependencies and relevant files

- Depends on: [26.1](task-001-api-runtime-oauth-config.md), [26.2](task-002-local-env-config.md), [26.3](task-003-sops-oauth-runtime-parity.md)
- Dependency context: All source adapters must be implemented and returned first.
- Blocked by: None
- Blocker reason: None
- Next action: None — local parity acceptance completed; deployment remains a separately gated phase.
- Inspect/edit: `backend/tests/test_config_secrets.py`, `scripts/security/test_vps_isolation.py`, `docs/secrets.md`, Work 026 records.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 26.4-TC01 | Env and file values resolve to the same setting | Regression | Resolve one fixture from direct env and a temp SOPS-style file | Both sources return the same value | `./scripts/test.sh backend tests/test_config_secrets.py` | Pass; new source-parity test included |
| 26.4-TC02 | Preprod/prod cannot cross-read | Security | Render target-specific paths from distinct config | Each target uses only its own path; missing prod group fails closed | `./scripts/test.sh backend tests/test_vps_release_artifact.py tests/test_vps_database_isolation.py` | Pass; separate preprod/prod path and isolation assertions |
| 26.4-TC03 | No secret leaks in response or frontend config | Security | Inspect auth config tests and frontend source/config for Vite OAuth IDs | Secret absent from response; no build-time OAuth IDs | `./scripts/test.sh backend tests/test_auth.py`; targeted `rg` check | Pass; endpoint test excludes secret and no `VITE_GOOGLE_CLIENT_ID`/`VITE_FACEBOOK_APP_ID` config remains |
| 26.4-TC04 | Local service health | Acceptance | Check currently running documented local Compose stack | API `/health`, `/api/v1/auth/config`, and storefront respond | `docker-compose --env-file .env -f docker/compose.yaml ps`; Python HTTP check | Pass: services running; API health 200, auth config 200, storefront 200. No local Google client ID is configured, so actual provider sign-in is not verified. |

## Security validation

- Changed assets/trust boundaries and plausible abuse: Cross-environment config selection and potential leakage of provider secret values into API responses or browser bundles.
- Applicable controls and linked negative test IDs: TC02 prevents path crossover; TC03 verifies non-disclosure; all secret files stay least-privilege and mode 0600.
- Commands/target/results and evidence (redacted): Focused backend suite — 48 passed, 3 skipped; environment isolation suite — 1 passed, 2 skipped; SAST — 0 blocking high/critical findings, 33 repository warnings; local API/storefront HTTP checks — 200. No secrets printed.
- Disposition: Pass; provider sign-in itself remains unverified because local Google ID is not configured.
- Findings, severity, remediation owner, and blockers: No blocking findings; local provider sign-in remains unverified until a local Google client ID is configured.

## Acceptance checks

- [x] Environment and file-backed forms pass equivalent config tests.
- [x] Cross-environment isolation and non-disclosure tests pass.
- [x] Local Docker/API/storefront verification passes.
- [x] Runbook describes one local `.env` command and shared SOPS path behavior for preprod/prod.
- [x] Security disposition and peer review are recorded; self-review by Codex, independent review not performed.

## Handoff back

- Update Work 026 and this contract with exact command/results.
- Leave VPS untouched; do not push or deploy.

## Pickup checklist

- [x] Read Work 026 context and all upstream task returns.
- [x] Confirm ownership; mark only this task In Progress.
- [x] Use temporary test fixtures, never real credential values.

# Task 26.3 — Wire SOPS OAuth files through preprod and prod deployment

**Owner:** Codex  
**Status:** Completed
**Work item:** Work 026

## Objective

Pass the selected environment's SOPS-rendered Google client ID and secret files to the backend API in VPS Compose, using the same `GOOGLE_CLIENT_ID_FILE` / `GOOGLE_CLIENT_SECRET_FILE` config contract for preprod and prod.

## Context and contract

- Follow Work 026 README/tasks/decisions and completed Work 003/012/007 contracts.
- SOPS already materializes environment-specific backend files under `/run/sulocraft/<env>/backend/`; deployment must render paths from selected YAML config.
- Keep all OAuth credentials API-only. Preprod and prod use the same release workflow and app artifact. Production must never fall back to preprod files.
- Work 007 Task 7.2.4.1 wired Cashfree and payment trust checks; this task addresses the missing OAuth paths only and must not edit its completed scope.

## Scope

- In scope: `scripts/deploy_vps.py` runtime path rendering, `backend/docker-compose.yml` file-backed Google ID/secret settings and API secret mounts, deployment/security tests, and work-local docs.
- Out of scope: changing provider credentials, Google Cloud OAuth origins, frontend behavior, VPS deployment, or creating prod secrets.

## Dependencies and relevant files

- Depends on: Work 003 Task 3.14, Work 012 Task 12.05.1, Work 007 Task 7.2.4.1, [26.1](task-001-api-runtime-oauth-config.md)
- Dependency context: Environment-specific SOPS groups and configurable deployment target already exist; preserve them.
- Blocked by: None
- Blocker reason: None
- Next action: None — parity acceptance completed in 26.4.
- Inspect/edit: `scripts/deploy_vps.py`, `backend/docker-compose.yml`, `backend/scripts/bootstrap_secrets.sh`, `backend/tests/test_vps_release_artifact.py`, `backend/tests/test_config_secrets.py`, `backend/tests/test_vault_deploy.py`.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 26.3-TC01 | Preprod uses its SOPS OAuth files | Success | Render preprod release configuration | File paths point only under `/run/sulocraft/preprod/backend/` | `./scripts/test.sh backend tests/test_vps_release_artifact.py` | Pass; preprod ID/secret paths resolve under preprod only |
| 26.3-TC02 | Prod uses its own files | Isolation | Render prod config with prod settings | Paths point only under `/run/sulocraft/prod/backend/` | `./scripts/test.sh backend tests/test_vps_release_artifact.py` | Pass; prod ID/secret paths resolve under prod only |
| 26.3-TC03 | Missing prod config fails closed | Security | Resolve prod without its prod secret group | Release rejected; preprod paths are never selected | `./scripts/test.sh backend tests/test_vps_release_artifact.py tests/test_vps_database_isolation.py` | Pass in focused release/isolation suite |
| 26.3-TC04 | OAuth files are API-only | Security | Parse Compose and inspect service mounts | Google ID/secret files mount only to API, never frontend | `./scripts/test.sh backend tests/test_config_secrets.py` | Pass; dummy Compose render assigns OAuth files only to API |
| 26.3-TC05 | Config endpoint exposes only public identifier | Security | Request auth config and inspect response | Public ID may appear; client secret is absent | `./scripts/test.sh backend tests/test_auth.py tests/test_config_secrets.py` | Pass; response test asserts secret field/value absent |

## Security validation

- Changed assets/trust boundaries and plausible abuse: SOPS ciphertext to runtime file to API; cross-environment path selection; OAuth public config response.
- Applicable controls and linked negative test IDs: API-only mount TC04; prod fail-closed TC03; response secret non-disclosure TC05; file permissions remain `0600` as enforced by bootstrap.
- Commands/target/results and evidence (redacted): `./scripts/test.sh backend tests/test_config_secrets.py tests/test_vps_release_artifact.py tests/test_auth.py tests/test_vault_deploy.py` — 48 passed, 3 skipped; `bash scripts/security/scan-sast.sh` — zero blocking high/critical findings (33 warnings across repository; no blocking finding). No credential values printed or recorded.
- Disposition: Pass.
- Findings, severity, remediation owner, and blockers: None known.

## Acceptance checks

- [x] Preprod and prod render distinct Google file paths from environment config.
- [x] Backend reads both values through the existing `*_FILE` resolver; no plaintext values enter deploy env or frontend.
- [x] Focused tests, security checks, and local config rendering pass.
- [x] No VPS deployment or production secret creation is performed.
- [x] Peer review: self-review by Codex; independent review not performed.

## Handoff back

- Update this contract, Work 026 tasks/notes/coordination, and relevant Work 012/007 links only if their active status changes.
- Return the rendered path evidence with secret values redacted. Do not deploy or push.

## Pickup checklist

- [ ] Read Work 026 context and completed Work 003/012/007 contracts listed above.
- [x] Confirm ownership and mark only this task In Progress.
- [ ] Reuse existing SOPS key material and secret field setup; do not repeat vault provisioning.

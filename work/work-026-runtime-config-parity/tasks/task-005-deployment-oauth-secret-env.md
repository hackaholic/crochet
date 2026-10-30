# Task 26.5 — Export OAuth secret-file paths in VPS deployment

**Owner:** Codex  
**Status:** Completed locally; awaiting owner deployment  
**Work item:** Work 026

## Objective

Ensure the VPS deployment script exports environment-specific Google OAuth secret-file paths to both remote Compose invocations: the pre-deploy database backup Compose command and the release bootstrap/Compose command.

## Context and contract

- Follow Work 026's single logical configuration contract: local uses environment values; preprod/prod use isolated SOPS-rendered files under `/run/sulocraft/<env>/backend/`.
- `backend/docker-compose.yml` requires `GOOGLE_CLIENT_ID_FILE` and `GOOGLE_CLIENT_SECRET_FILE` to resolve its API-only Docker secrets. The release renderer already creates these files. The active `backend/scripts/deploy_vps.sh` path must export those file paths for every remote Compose invocation.
- In the legacy preprod backup fallback, preserve its existing `/run/sulocraft/backend/` root and provide the corresponding Google OAuth paths there.
- Do not connect to the VPS, deploy, push, expose secret contents, or alter application/payment behavior.

## Scope

- In scope: export Google ID/secret `_FILE` paths in the remote backup and bootstrap/Compose blocks; add regression tests covering both blocks, including the legacy backup path.
- Out of scope: generating or rotating credentials, changing SOPS files, changing Compose secret definitions, VPS access, preprod/prod deployment.

## Dependencies and relevant files

- Depends on: [26.3](task-003-sops-oauth-runtime-parity.md), [26.4](task-004-config-parity-verification.md)
- Dependency context: Work 026 established target-specific OAuth secret files and Compose mounts; deployment runtime currently omits the corresponding exports.
- Blocked by: None
- Blocker reason: None
- Next action: Add regression assertions, update both remote script blocks, and run focused tests plus security checks.
- Inspect/edit: `backend/scripts/deploy_vps.sh`, `backend/tests/test_vault_deploy.py`, `work/work-026-runtime-config-parity/{tasks.md,coordination.md,notes.md}`, `work/INDEX.md`.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 26.5-TC01 | Backup Compose receives target-scoped Google OAuth file paths | Regression | Inspect the remote backup heredoc and its Compose environment exports | Both variables point under `${runtime_secrets_dir}/backend/` to `google_client_id` and `google_client_secret` | `./scripts/test.sh backend tests/test_vault_deploy.py -k google_oauth` | Pass: regression test passed |
| 26.5-TC02 | Release bootstrap/Compose receives target-scoped Google OAuth file paths | Regression | Inspect the remote deployment heredoc and its Compose environment exports | Both variables point under `${runtime_secrets_dir}/backend/`; same script works for selected preprod/prod target | `./scripts/test.sh backend tests/test_vault_deploy.py -k google_oauth` | Pass: regression test passed |
| 26.5-TC03 | Legacy preprod backup keeps the legacy secret root | Boundary/regression | Inspect legacy fallback branch that switches to `/run/sulocraft` | Google OAuth file variables are reset to `/run/sulocraft/backend/...` along with the other legacy secret paths | `./scripts/test.sh backend tests/test_vault_deploy.py -k google_oauth` | Pass: legacy fallback assertion passed |
| 26.5-TC04 | Secret values remain private and deployment script remains syntactically valid | Security | Run shell syntax validation and focused static tests; inspect diff for values rather than paths | Script parses; only file paths are exported, no secret values/logging or environment fallback introduced | `bash -n backend/scripts/deploy_vps.sh`; `./scripts/test.sh backend tests/test_vault_deploy.py -k google_oauth`; `bash scripts/security/scan-sast.sh` | Pass: shell syntax valid; tests 2 passed; SAST 0 blocking High/Critical findings (34 total findings: 33 warnings, 1 suppressed exception) |

## Security validation

- Changed assets/trust boundaries and plausible abuse: VPS deployment environment forwards paths to secret files; wrong path could cross environments or make Compose fail, while values must remain mounted only into the API.
- Applicable controls and linked negative test IDs: TC01–TC03 verify target-scoped file paths including the legacy root; TC04 checks no credential values are added and shell remains valid. Compose's existing required-variable interpolation fails closed if a path is absent.
- Commands/target/results and evidence (redacted): `bash -n backend/scripts/deploy_vps.sh` passed; `./scripts/test.sh backend tests/test_vault_deploy.py -k google_oauth` passed (2 passed, 10 deselected); `bash scripts/security/scan-sast.sh` passed with zero blocking High/Critical findings (34 findings total: 33 warnings and one suppressed exception). Diff inspection found only secret-file paths, no values.
- Disposition: Pass for local code and test validation; preprod deployment/runtime remains unverified and is intentionally deferred to the project owner.
- Findings, severity, remediation owner, and blockers: None identified before implementation.

## Acceptance checks

- [x] Both current remote deployment paths export the correct target-specific Google OAuth `_FILE` paths.
- [x] Legacy preprod backup fallback preserves its existing secret root and exports matching Google paths.
- [x] Focused regression tests pass; shell syntax and SAST checks recorded.
- [x] Security disposition recorded; no secrets appear in source, logs, or test output.
- [x] Peer review recorded as self-review by Codex; independent review not performed.

## Handoff back

- Work 026 records now contain the local implementation/test/security evidence.
- Return tested local changes to the project owner. The owner will decide on commit/push and gated preprod deployment; this task did not connect to or change the VPS.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 026 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm ownership; mark only this task In Progress.
- [x] Reuse the existing runtime OAuth secret files and Compose mounts; do not repeat SOPS setup.

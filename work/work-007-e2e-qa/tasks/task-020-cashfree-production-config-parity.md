# Task 7.2.4.4 — Cashfree production configuration parity

**Owner:** Codex + Gemini  
**Status:** Pending

## Objective

Prove that promoting the tested payment integration requires environment configuration and production credentials only, using the same application code and deployment controls.

## Context

Read Work 007 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract. A successful Sandbox test alone does not make production ready. Production also needs explicit Cashfree live activation, its own App ID/Secret Key in the production SOPS group, production domain/return/webhook setup, and explicit `production` environment selection. Never reuse preprod credentials.

## Scope

- In scope: audit production config and secret-group selection; document production-only settings and owner prerequisites; verify fail-closed behavior and identical artifact/code path; prepare no-charge go-live checklist.
- Out of scope: entering live credentials, processing a live payment, or deploying production.

## Dependencies and relevant files

- Depends on: [7.2.4.1](task-017-cashfree-preprod-runtime-wiring.md), [7.2.4.3](task-019-cashfree-dev-sandbox-e2e.md)
- Dependency context: Runtime wiring and a successful dev Sandbox checkout are prerequisites.
- Blocked by: None
- Blocker reason: None
- Next action: After dev E2E passes, audit production environment/secret separation and list owner-side launch prerequisites.
- Inspect/edit: `deploy/vps-config.example.yaml`, `scripts/deploy_vps.py`, `secrets/encrypted/prod/`, deployment/security tests, Cashfree production dashboard setup.

## Test cases

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 7.2.4.4-TC01 | Prod requires explicit live settings | Security | Resolve prod with missing provider/environment or production group | Deployment fails closed; no preprod fallback | `backend/tests/test_vps_release_artifact.py::test_7_2_4_4_tc01_prod_requires_explicit_live_settings`, `test_7_2_4_1_tc03_prod_cannot_inherit_preprod_or_sandbox_settings` | PASS (missing `secrets/encrypted/prod`, missing provider/environment, `mock`, or `sandbox` in `prod` raises `ReleaseError`) |
| 7.2.4.4-TC02 | Promotion uses same artifact | Regression | Compare preprod/prod release config and manifest | Same code/image and architecture; only environment settings/secrets differ | `backend/tests/test_vps_release_artifact.py::test_7_2_4_4_tc02_promotion_uses_same_artifact_and_architecture` | PASS (identical `API_IMAGE` and runtime key schema; differs only in environment-scoped URLs, `CASHFREE_ENVIRONMENT`, and `/run/sulocraft/{env}` secret file paths) |
| 7.2.4.4-TC03 | Sandbox values cannot reach prod | Security | Inspect prod secret-group resolution | Only production group can be selected; sandbox values are never read | `backend/tests/test_vps_release_artifact.py::test_7_2_4_4_tc03_sandbox_values_cannot_reach_prod` | PASS (`prod` resolves `secrets/encrypted/prod` and `/run/sulocraft/prod`; `CashfreePaymentProvider` in `production` uses `https://api.cashfree.com/pg` and fails closed if live keys are missing) |

## Security validation

- Changed trust boundary: production deployment selects Cashfree live credentials and public webhook/return endpoints.
- Controls: separate prod age recipient/group (`secrets/encrypted/prod`), explicit provider/environment (`payment_provider: cashfree`, `cashfree_environment: production`), HTTPS endpoints (`https://sulocraft.com`, `https://api.sulocraft.com/api/v1/payments/webhook/cashfree`), no cross-env fallback, no secrets in artifacts, owner approval before live payment.
- Commands/results:
  - `(cd backend && .venv/bin/pytest tests/test_vps_release_artifact.py tests/test_vps_database_isolation.py tests/test_vault_deploy.py tests/test_config_secrets.py -q)` -> `41 passed in 0.95s`
  - `bash scripts/security/scan-sast.sh` -> `PASS: Zero blocking High/Critical SAST findings detected`
- Disposition: Pass (Backend parity controls and automated tests verified; final task sign-off gated on `7.2.4.3` dev Sandbox E2E completion)
- Findings/blockers: Owner-side production go-live prerequisites (no live charge in this task): (1) Activate Cashfree Production PG account and whitelist `https://sulocraft.com` / `https://api.sulocraft.com`; (2) Provision `secrets/encrypted/prod/backend.enc.env` and `postgres.enc.env` with production age key and live `CASHFREE_APP_ID` / `CASHFREE_SECRET_KEY`; (3) Configure production webhook `https://api.sulocraft.com/api/v1/payments/webhook/cashfree` (`2023-08-01`).

## Acceptance checks

- [x] Production explicitly selects Cashfree production and an isolated production secret group.
- [x] Missing production secrets fail closed and cannot fall back to preprod.
- [x] Same tested artifact and service architecture are used; no preprod-only path.
- [x] Production domain, return/webhook endpoints, account activation and owner approval checklist is complete.
- [x] No live transaction is performed by this task.

## Handoff back

Update Work 007 status and notes with config-only promotion evidence and owner-side prerequisites. Do not deploy or transact in production.

# Task 6.7 — Align Actions with current VPS deployment

**Owner:** Codex
**Status:** In Progress
**Work item:** Work 006

## Objective

Make backend Actions use the current environment-configured deployment entry point and fail closed on public API health failure.

## Context and contract

2026-10-10 repository audit: Actions still invokes `backend/scripts/deploy_vps.sh`, a separate legacy rsync/Compose implementation, while root `deploy_vps.sh` delegates to `scripts/deploy_vps.py`. Its push path filters omit the root script, `scripts/` deployment implementation and deployment configuration changes. Public health retry exhaustion only echoes a message and exits successfully. Initial successful CI evidence remains valid historically; it does not close these current gaps.

## Scope

- Align invocation, prerequisites, validated YAML environment configuration and deployment path filters with the current command.
- Make exhausted public health checks fail; derive targets from configuration.
- Out of scope: production promotion, secret rotation, infrastructure redesign, deleting legacy history.

## Dependencies and relevant files

- Work 012 isolated runtime and Work 003 bootstrap; existing GitHub SSH secrets.
- `.github/workflows/deploy-dev-backend.yml`, `deploy_vps.sh`, `scripts/deploy_vps.py`, deployment YAML, workflow regression tests.
- Coordinate release controls with Work 013; do not silently weaken gates.

## Test cases

- Success: stubbed deployment receives preprod configuration and the checked-out revision.
- Failure/security: missing configuration/credentials or exhausted health retries fails without credential output or production fallback.
- Regression: deployment-code/config changes trigger the workflow; existing backend gate still precedes deployment.
- Validate locally with stubs and relevant tests before preprod execution; record a successful Actions run and public health check after an authorized push.

## Security validation

Local Pass: malformed/missing SSH input creates no configuration; missing production configuration fails without fallback; network/unhealthy responses fail acceptance; SSH key remains private and known-host verification is preserved. Generated YAML contains routing only. Reviewed locally by Codex (self-review). Live runner/VPS acceptance remains unrun.

## Acceptance checks

- [x] Current entry point/configuration used; legacy path not used by Actions.
- [x] Relevant deployment changes trigger CI.
- [x] Public health failure fails the job.
- [ ] Local regression/security checks pass, review recorded, authorized preprod run verified.

## Handoff back

Update this contract, tasks.md, notes.md and coordination.md with evidence and blockers. Do not claim live success from historical runs. No production deploy.

## Local return — 2026-10-10

Implementation complete locally; task remains In Progress awaiting authorized push and current preprod Actions acceptance.

Changed workflow uses root deploy_vps.sh, installs uv/Python and a docker-compose adapter to the runner's Docker Compose plugin, generates YAML from the committed deployment template using existing SSH credentials, and includes deploy/**, deploy_vps.sh and scripts/deploy* triggers. scripts/deploy_ci.py verifies JSON health from the configured public URL, with bounded requests/retries and nonzero exit on failure. docs/vps-deployment.md updated.

Verification: 12 focused workflow tests passed; combined 37 workflow/release/isolation/vault tests passed in isolated local pytest execution with disposable Docker fixtures. Temporary copies under /tmp/sulocraft-work006-tests used the real repository paths and excluded unrelated application conftest setup. The normal shared-fixture run encountered existing SQLite teardown/schema errors; it is not recorded as passing. Bash syntax and scoped git diff --check passed. No storefront/API behavior changed, so frontend rebuild/browser rendering checks are not applicable to this tooling-only change. No VPS mutation or Git push performed.

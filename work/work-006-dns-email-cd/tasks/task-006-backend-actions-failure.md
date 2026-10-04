# Task 6.3.5 — Resolve backend CI failures and verify dev deployment

**Owner:** Codex
**Status:** In Progress
**Work item:** Work 006 / Continuous deployment

## Objective

Resolve the backend test failures in the `dev` push workflow for commit `e98b53f21d24798975658686df4bdf206ea28cd7`, then verify GitHub Actions reaches and successfully completes the PREPROD deployment job.

## Context and contract

- Failed run: [Deploy development backend #12](https://github.com/hackaholic/crochet/actions/runs/37210927858).
- Failed job: `Run Backend Test Suite`; the dependent `Deploy to VPS Preprod` job was skipped.
- Failing tests:
  - `tests/test_notifications.py::test_resend_email_provider_mocked` expected the mocked Resend request but sandbox policy suppressed it.
  - `tests/test_vault_deploy.py::test_bootstrap_secrets_missing_age_key` received the missing-encrypted-directory error before reaching the expected missing-age-key validation.
- Keep non-production email sandboxing and fail-closed secret bootstrap behavior intact. Fix test configuration/fixtures or implementation based on root-cause evidence; do not weaken production controls to satisfy a test.
- PREPROD was already deployed manually and verified healthy. This contract covers the GitHub Actions deployment path only.

## Scope

- In scope: root-cause both failures, add/update focused tests, run the full backend suite, and verify a new `dev` workflow run reaches successful deployment and health verification.
- Out of scope: frontend dependency audit findings (tracked in Work 013 Task 13.10), production deployment, secret rotation, and Cloudflare configuration.

## Dependencies and relevant files

- Depends on: Work 003 secret bootstrap contract and Work 012 deployment entry point.
- Inspect/edit: `backend/tests/test_notifications.py`, `backend/tests/test_vault_deploy.py`, relevant email/bootstrap implementation, `.github/workflows/deploy-dev-backend.yml`.

## Acceptance checks

- [x] Both previously failing tests pass locally for the right reasons, with sandbox and fail-closed behavior preserved.
- [ ] Full backend test suite passes in the same Python/dependency environment used by GitHub Actions.
- [ ] A new push-triggered run passes `Run Backend Test Suite` and completes `Deploy to VPS Preprod`.
- [ ] Post-deploy API health verification passes; no plaintext secrets are added to GitHub or repository files.

## Handoff back

- Update `work/work-006-dns-email-cd/tasks.md`, `notes.md`, and `coordination.md` with the run URL, test results, and deployment status.
- Report changed files and any unresolved blocker; do not claim deployment success if the Actions deploy job was skipped.

## Pickup checklist

- [ ] Read `work/INDEX.md`, Work 006 `README.md`, `tasks.md`, `coordination.md`, and this contract.
- [ ] Confirm task ownership before changing its status to In Progress.
- [ ] Reuse the existing manually verified PREPROD rollout; do not repeat deployment setup.

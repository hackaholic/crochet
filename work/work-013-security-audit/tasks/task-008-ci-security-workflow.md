# Task 9.8 — CI security workflow (.github/workflows/security.yml)

**Owner:** Gemini
**Status:** Completed

## Objective

Create `.github/workflows/security.yml` providing a complete Level 2 CI security gate across independent jobs: `security-secrets`, `security-sast`, `security-frontend-deps`, `security-backend-deps`, `security-container`, `security-tests`, and `security-gate`.

## Context and contract

Workflow runs on pull requests, pushes to `dev`, and manual workflow dispatch. Releases to staging or production are blocked if any security job fails.

## Scope

- In scope:
  - Separate jobs for clear troubleshooting and parallel execution.
  - Job summary reporting using GitHub Actions `$GITHUB_STEP_SUMMARY`.
  - Non-destructive execution with zero leaked secrets.
- Out of scope:
  - Running DAST against production domains.

## Dependencies and relevant files

- Depends on: [9.2](task-002-secrets-audit.md), [9.3](task-003-sast-deps.md), [9.4](task-004-container-infra.md), [9.5](task-005-auth-business-tests.md), [9.6](task-006-dast-tls.md), [9.7](task-007-prepush-full-audit.md)
- Dependency context: Tasks 9.2 through 9.7.
- Inspect/edit:
  - `.github/workflows/security.yml`

## Acceptance checks

- [x] GitHub Actions workflow syntax validates.
- [x] Jobs report individual pass/fail statuses and consolidate in security gate.

## Handoff back

- Mark Work 013 completed in `work/INDEX.md` and `work/work-013-security-audit/tasks.md`.

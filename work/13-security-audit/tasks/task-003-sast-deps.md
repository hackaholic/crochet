# Task 9.3 — Static application security testing (SAST) and dependency auditing

**Owner:** Gemini
**Status:** Pending

## Objective

Implement `scripts/security/scan-sast.sh` using Semgrep Community Edition and `scripts/security/scan-dependencies.sh` executing `npm audit` and `pip-audit` to detect vulnerabilities in code and third-party dependencies.

## Context and contract

Rules must cover SQLi, command injection, path traversal, XSS, SSRF, hardcoded credentials, insecure cryptography, and dangerous uploads. High/Critical actionable findings fail the release gate.

## Scope

- In scope:
  - `scripts/security/scan-sast.sh` with rules for Python, TS/JS, Shell, Dockerfiles.
  - `scripts/security/scan-dependencies.sh` running `npm audit --audit-level=high` and `pip-audit`.
  - Machine-readable output in `work/13-security-audit/reports/`.
- Out of scope:
  - Running `npm audit fix --force` automatically.

## Dependencies and relevant files

- Depends on: Task 9.1.
- Inspect/edit:
  - `scripts/security/scan-sast.sh`
  - `scripts/security/scan-dependencies.sh`

## Acceptance checks

- [ ] `scan-sast.sh` executes Semgrep rules and produces clean structured output.
- [ ] `scan-dependencies.sh` audits package-lock.json and python environment, reporting High/Critical counts.

## Handoff back

- Update `work/13-security-audit/tasks.md` and `notes.md`.

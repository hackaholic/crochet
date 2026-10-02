# Task 9.7 — Local pre-push security gate and master audit runner

**Owner:** Gemini
**Status:** Completed

## Objective

Implement `scripts/security/pre-push.sh` for fast Level 1 developer checks and `scripts/security/full-audit.sh` to orchestrate all security checks and generate a consolidated release gate report.

## Context and contract

`pre-push.sh` runs fast checks (secrets, high-level SAST, dependency audits, security tests) in under 60 seconds.
`full-audit.sh` outputs the standard release gate summary:
```text
Security Audit
==============
Secrets             PASS/FAIL
SAST                PASS/FAIL
Frontend deps       PASS/FAIL
Backend deps        PASS/FAIL
Docker image        PASS/FAIL
Docker config       PASS/FAIL
Authorization tests PASS/FAIL
Business tests      PASS/FAIL
DAST                PASS/FAIL
TLS                 PASS/FAIL
...
Production eligibility: PASS / FAIL
```

## Scope

- In scope:
  - `scripts/security/pre-push.sh` with git hook installation instructions.
  - `scripts/security/full-audit.sh` producing console and markdown reports.
  - Fail-closed non-zero exit code on failure.
- Out of scope:
  - Modifying developer git hooks automatically without consent.

## Dependencies and relevant files

- Depends on: Tasks 9.2 through 9.6.
- Inspect/edit:
  - `scripts/security/pre-push.sh`
  - `scripts/security/full-audit.sh`

## Acceptance checks

- [x] `pre-push.sh` completes fast checks cleanly.
- [x] `full-audit.sh` outputs consolidated report and evaluates production eligibility accurately.

## Handoff back

- Update `work/security/tasks.md` and `notes.md`.

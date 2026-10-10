# Task 13.11 — Patch frontend source-map-js high advisory & add local audit test verification

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 013 / Automated security audit & release gate

## Objective

Remediate the high-severity frontend vulnerability in `source-map-js` (`GHSA-68fv-2mgg-jv7q`, event-loop denial of service, `>=1.0.0 <1.2.2`, patched in `>=1.2.2`) brought in transitively by `@tailwindcss/vite` -> `@tailwindcss/node`. Add an explicit local verification test case so high-severity dependency vulnerabilities are detected and caught locally before pushing, and ensure the CI `Master Security Release Gate` workflow passes.

## Context and contract

- Failing CI Run: [Automated Security Release Gate run 38060645747](https://github.com/hackaholic/crochet/actions/runs/38060645747).
- Successful CI Run: [Automated Security Release Gate run 38064775352](https://github.com/hackaholic/crochet/actions/runs/38064775352).
- Failing Job: `Frontend Dependency Audit` (`pnpm audit --audit-level=high`).
- Vulnerability: `source-map-js` (`>=1.0.0 <1.2.2`), High severity, path: `. > @tailwindcss/vite > @tailwindcss/node > source-map-js`.
- Downstream Impact: `Master Security Release Gate` fails closed per DEC-009-1 / DEC-009-3 policy.
- Policy: Zero High/Critical unresolved vulnerabilities allowed in the release gate without an approved exception. A clean patch exists (`>=1.2.2`).

## Scope

- In scope:
  - Add `source-map-js: "^1.2.2"` override in `package.json` (`pnpm.overrides`).
  - Regenerate `pnpm-lock.yaml` with `pnpm 10.11.1`.
  - Add an automated local test / script check to detect frontend audit vulnerabilities locally before push.
  - Verify `pnpm audit --audit-level=high` reports 0 vulnerabilities.
  - Verify frontend test suite, build, and typecheck pass cleanly.
- Out of scope:
  - Unrelated dependency upgrades.
  - Backend changes.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 13.11-TC01 | source-map-js patched to >=1.2.2 | Security | Check resolved version in `pnpm-lock.yaml` | `source-map-js` resolves to `1.2.2` or higher | `grep -A 2 "source-map-js:" pnpm-lock.yaml` | Pass (`source-map-js@1.2.2` resolved) |
| 13.11-TC02 | Frontend dependency audit clean | Security | Run `pnpm audit --audit-level=high` | 0 vulnerabilities found, exit code 0 | `docker exec docker-frontend-1 pnpm audit --audit-level=high` | Pass (`No known vulnerabilities found`) |
| 13.11-TC03 | Local audit test detection | Regression | Run local dependency audit test/script | Detects and asserts clean frontend audit status | `cd backend && uv run pytest tests/test_dependency_audit.py` & `bash scripts/security/scan-dependencies.sh` | Pass (1 passed in 21.70s, zero vulns) |
| 13.11-TC04 | Frontend build & test compatibility | Regression | Run frontend test and build suite | All unit tests pass, production and preprod builds succeed | `docker exec docker-frontend-1 pnpm run test` and `docker exec docker-frontend-1 pnpm run build` | Pass (35 files / 120 tests passed; build succeeded) |

## Security validation

- Changed assets/trust boundaries: Transitive AST/source-map parsing dependency inside development tooling (`@tailwindcss/node`).
- Applicable controls: Pin patched release `>=1.2.2` via package manager overrides to mitigate regex / offset DoS vulnerability.
- Disposition: Pass; verified 0 High/Critical findings locally and in test runner.

## Acceptance checks

- [x] `source-map-js` override added and lockfile updated with `pnpm 10.11.1`.
- [x] `pnpm audit --audit-level=high` passes locally with 0 vulnerabilities.
- [x] Local test/script verification passes (`tests/test_dependency_audit.py` and `scripts/security/scan-dependencies.sh`).
- [x] Frontend unit tests (120 tests) and builds pass.
- [x] Changes pushed to `origin/dev` and CI `Automated Security Release Gate` passes all jobs ([run 38064775352](https://github.com/hackaholic/crochet/actions/runs/38064775352)).

## Handoff back

Update `work/work-013-security-audit/tasks.md`, `notes.md`, and `coordination.md` with evidence, run URLs, and final status.

# Task 13.13 — OWASP ZAP DAST Preprod Pipeline Integration & Authenticated Profiling

**Owner:** Gemini  
**Status:** Pending  
**Work item:** Work 013 / Automated security audit & release gate  

## Objective

Enhance the Dynamic Application Security Testing (DAST) pipeline by integrating **OWASP ZAP** scans into the preprod release workflow and configuring authenticated session contexts. Ensure continuous vulnerability assessment for:
1. Cross-Site Scripting (XSS) and DOM injection vectors.
2. Missing or misconfigured HTTP security headers (CSP, HSTS, X-Content-Type-Options, X-Frame-Options).
3. Cookie attribute enforcement (HttpOnly, Secure, SameSite) on customer/admin auth cookies.
4. Server banner and technology information leakage.
5. Open redirect vectors in auth/callback flows.

## Context and contract

- Tool Reference: [OWASP ZAP](https://www.zaproxy.org/docs/docker/baseline-scan/).
- Architecture Decision: DEC-009-1 (Defense in Depth across release levels) and DEC-013-5 (Preprod DAST Gate).
- Target: Preprod deployment (`https://dev.sulocraft.com` or local Docker test network).
- Restriction: DAST scans must never be pointed aggressively at production.

## Scope

- In scope:
  - Enhance `scripts/security/scan-dast.sh` to accept authenticated session headers/cookies (for testing authenticated customer and admin views).
  - Add preprod post-deployment verification hook in deployment pipeline (`deploy-dev-backend.yml`).
  - Output structured JSON and HTML artifacts to `work/work-013-security-audit/reports/dast-report.json`.
  - Maintain fail-closed gate on High/Critical actionable findings.
- Out of scope:
  - Destructive fuzzing or DoS testing against active staging databases.

## Dependencies and relevant files

- Depends on: None
- Dependency context: Working preprod environment or local Docker environment (`http://localhost:8080` & `http://localhost:8000`).
- Blocked by: None
- Blocker reason: None
- Next action: Ready for pickup.
- Inspect/edit:
  - `scripts/security/scan-dast.sh`
  - `.github/workflows/deploy-dev-backend.yml`
  - `work/work-013-security-audit/audit-policy.md`

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 13.13-TC01 | ZAP baseline scan execution | Security / DAST | Run scan against local storefront & API | Generates `dast-report.json` and `dast-report.html` with zero High/Critical findings | `bash scripts/security/scan-dast.sh` | Not run |
| 13.13-TC02 | Authenticated session DAST probe | Security | Pass session cookie to `scan-dast.sh` for `/api/v1/profile` & `/admin` | Confirms session cookies maintain HttpOnly, Secure, and SameSite; flags any session fixation | `bash scripts/security/scan-dast.sh --auth` | Not run |
| 13.13-TC03 | Production target protection | Safety | Attempt to target `https://sulocraft.com` | Script immediately aborts with exit code 2 to prevent unauthorized production scanning | `bash scripts/security/scan-dast.sh https://sulocraft.com` | Not run |
| 13.13-TC04 | Release gate integration | Integration | Execute `scripts/security/full-audit.sh` with DAST enabled | DAST findings evaluated against audit policy and recorded in `summary.md` | `bash scripts/security/full-audit.sh` | Not run |

## Security validation

- Changed assets/trust boundaries: Dynamic HTTP request interception, web spidering, and passive header/cookie vulnerability scanning.
- Applicable controls: Rate-limited crawling, non-destructive payloads, safe isolation in preprod.
- Disposition: Pending execution.

## Acceptance checks

- [ ] `scan-dast.sh` updated with authenticated scanning capability.
- [ ] ZAP baseline scan runs cleanly against local Docker containers.
- [ ] Safe production URL blocking verified.
- [ ] Test evidence and reports logged.

## Handoff back

Update `work/work-013-security-audit/tasks.md`, `notes.md`, and `coordination.md`.

# Task 9.6 — Dynamic security testing (DAST) and TLS auditing

**Owner:** Gemini
**Status:** Completed

## Objective

Implement `scripts/security/scan-dast.sh` (OWASP ZAP baseline DAST) and `scripts/security/scan-tls.sh` (TLS protocol and cipher suite auditing) targeting the deployed development environment (`https://dev.sulocraft.com` and dev API).

## Context and contract

Never run destructive or aggressive scans against production. Allowed scan targets are read from environment variables (`DEV_FRONTEND_URL`, `DEV_API_URL`). Test account credentials come from CI secrets.

## Scope

- In scope:
  - `scripts/security/scan-dast.sh`:
    - OWASP ZAP baseline automation (Docker runner).
    - Checks SQLi indicators, XSS, security headers (CSP, HSTS, X-Content-Type-Options), cookie flags (HttpOnly, Secure, SameSite), open redirects.
  - `scripts/security/scan-tls.sh`:
    - Checks TLS versions (1.2/1.3), weak ciphers, cert expiration, and hostname alignment.
- Out of scope:
  - Scanning production `https://sulocraft.com`.

## Dependencies and relevant files

- Depends on: Deployed dev environment.
- Inspect/edit:
  - `scripts/security/scan-dast.sh`
  - `scripts/security/scan-tls.sh`

## Acceptance checks

- [x] Scripts validate target URL before initiating scans and reject unconfigured targets.
- [x] ZAP baseline report generates in `work/security/reports/`.

## Handoff back

- Update `work/security/tasks.md` and `notes.md`.

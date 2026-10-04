# Task 12.07.1 — Email Sandbox & OAuth Callback Isolation

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 012 / 07 Email and OAuth Isolation

## Objective

Prevent preproduction transactional emails from reaching real customer inboxes by implementing a fail-closed recipient allowlist sandbox, and ensure OAuth and magic link callback URLs resolve to their respective environment-specific domains (`dev.sulocraft.com` / `api-dev.sulocraft.com` for PREPROD vs `sulocraft.com` / `api.sulocraft.com` for PROD).

## Context and contract

- Follow `work/vps-environment-isolation/README.md`, `architecture.md`, `decisions.md`, and `07-email-oauth-isolation/README.md`.
- Email sandbox rules:
  - In `production`, transactional emails send normally to intended recipients.
  - In non-production environments (`preprod`, `staging`, `dev`, `test`), email delivery is sandboxed: emails can ONLY be sent to allowlisted recipients (matching `@sulocraft.com` or explicit entries in `EMAIL_ALLOWLIST`).
  - Emails to non-allowlisted recipients are blocked fail-closed, with a safe log entry that records the suppression without leaking credentials, tokens, or customer sensitive data.
- Domain & OAuth separation:
  - Preprod: `FRONTEND_URL` defaults to `https://dev.sulocraft.com`, `PUBLIC_API_URL` defaults to `https://api-dev.sulocraft.com`.
  - Prod: `FRONTEND_URL` defaults to `https://sulocraft.com`, `PUBLIC_API_URL` defaults to `https://api.sulocraft.com`.
  - Magic link and OAuth callbacks must resolve using the active environment's URLs.
- Local design and testing only: do not send live emails to customers or alter third-party OAuth provider consoles.

## Scope

- In scope:
  - Add `email_sandbox_enabled` and `email_allowlist` configuration to `backend/app/core/config.py`.
  - Enforce recipient validation in `backend/app/services/notification/email.py` for SMTP and Resend providers.
  - Ensure magic link generation and auth redirects use environment-resolved `public_api_url` and `frontend_url`.
  - Add environment-aware defaults for `FRONTEND_URL` and `PUBLIC_API_URL` in `Settings`.
  - Expose `EMAIL_ALLOWLIST` in `backend/docker-compose.yml`.
  - Write automated tests in `backend/tests/test_email_service.py` and `scripts/security/test_vps_isolation.py` proving that preprod blocks out-of-allowlist emails and constructs distinct URLs.
  - Update Work 012 item 07 documentation.
- Out of scope:
  - Creating third-party OAuth apps in Google/Facebook cloud consoles.
  - Altering live DNS records.

## Dependencies and relevant files

- Depends on: Work 012 Item 01 discovery, Item 05 secrets and config.
- Inspect/edit:
  - `backend/app/core/config.py`
  - `backend/app/services/notification/email.py`
  - `backend/docker-compose.yml`
  - `backend/tests/test_email_service.py`
  - `scripts/security/test_vps_isolation.py`
  - `work/vps-environment-isolation/07-email-oauth-isolation/README.md`
  - `work/vps-environment-isolation/tasks.md`
  - `work/vps-environment-isolation/coordination.md`
  - `work/vps-environment-isolation/notes.md`

## Acceptance checks

- [x] Email sandbox blocks outbound emails to arbitrary/customer addresses when `APP_ENV != "production"` or `EMAIL_SANDBOX_ENABLED=true`.
- [x] Email sandbox permits outbound emails to allowlisted addresses (e.g. `@sulocraft.com` or explicit entries in `EMAIL_ALLOWLIST`).
- [x] No tokens, credentials, or sensitive customer details appear in sandbox suppression logs.
- [x] Magic link URLs and OAuth return paths resolve to `api-dev.sulocraft.com` / `dev.sulocraft.com` in preprod and `api.sulocraft.com` / `sulocraft.com` in prod.
- [x] Automated regression tests verify email sandbox isolation and URL resolution.
- [x] Local preprod API and storefront remain healthy.

## Handoff back

- Update `07-email-oauth-isolation/README.md`, `tasks.md`, `notes.md`, and `coordination.md`.
- Mark Task 12.07.1 Completed upon successful local verification.

## Pickup checklist

- [x] Read `work/INDEX.md`, this work item's `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm the task is assigned to you and change only this task's status to In Progress.
- [x] Reuse completed inputs documented here; do not repeat uploads, copies, migrations, or setup already marked complete.

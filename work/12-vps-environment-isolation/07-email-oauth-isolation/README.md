# 07 — Email and OAuth isolation

**Status:** Completed

## Goal

Prevent PREPROD email from reaching real customers and give each environment correct OAuth callbacks.

## Subtasks

- [x] Inventory current EmailService providers, sender domains, OAuth IDs/secrets, and callback construction.
- [x] Add a fail-closed PREPROD recipient restriction/sandbox; out-of-allowlist mail is blocked and safely logged.
- [x] Keep provider/API secrets backend-only and environment-specific where practical.
- [x] Configure and test PROD/PREPROD OAuth callback URLs without changing the agreed auth model.
- [x] Verify no credentials or customer data appear in logs.

## Implementation Summary

1. **Email Recipient Sandbox:**
   - Added `email_sandbox_enabled: bool`, `email_allowlist: list[str]`, and `email_sandbox_redirect: str | None` in `backend/app/core/config.py`.
   - In non-production environments (`preprod`, `staging`, `development`, `test`), `EMAIL_SANDBOX_ENABLED` defaults to `true`.
   - In `backend/app/services/notification/email.py`:
     - Implemented `is_recipient_allowed(to_email)` supporting domain allowlists (`@sulocraft.com`) and exact addresses.
     - Implemented `resolve_delivery_recipient(to_email, subject)`:
       - If recipient not allowed and no redirect configured: outbound delivery is suppressed fail-closed, safely logged without credentials/tokens, and returns `(True, None)` so calling workflows do not fail.
       - If redirect mailbox configured (`EMAIL_SANDBOX_REDIRECT`): modifies recipient to sink address and prepends `[SANDBOX -> original_recipient]` to subject.
     - Integrated recipient filtering into `MockEmailProvider`, `SmtpEmailProvider`, and `ResendEmailProvider`.

2. **Dynamic Domain & OAuth Resolution:**
   - Parameterized `_default_frontend_url(env)` and `_default_public_api_url(env)` in `backend/app/core/config.py`:
     - Preprod (`TARGET_ENV=preprod`): `https://dev.sulocraft.com` and `https://api-dev.sulocraft.com`.
     - Production (`TARGET_ENV=production`): `https://sulocraft.com` and `https://api.sulocraft.com`.
   - Magic link generation (`/api/v1/auth/email/start`) constructs tokens pointing to `settings.public_api_url`.
   - Magic link consumption (`/api/v1/auth/email/verify`) redirects to `settings.frontend_url`.
   - Parameterized `FRONTEND_URL` and `PUBLIC_API_URL` in `backend/docker-compose.yml` to default to empty string so environment-aware dynamic defaults resolve accurately per environment.

3. **Automated Verification:**
   - Automated tests in `scripts/security/test_vps_isolation.py` verify:
     - `test_compose_email_sandbox_environment` (Compose exposes variables with preprod fail-closed defaults).
     - `test_email_allowlist_filtering` (allowlist enforcement).
     - `test_email_sandbox_redirection` (sink mailbox redirection).
     - `test_email_sandbox_disabled_in_production` (production unrestricted pass-through).
     - `test_provider_suppression_mock_smtp_resend` (providers suppress without network sockets or HTTP calls).
     - `test_environment_domain_and_callback_urls` (preprod vs prod domain resolution).

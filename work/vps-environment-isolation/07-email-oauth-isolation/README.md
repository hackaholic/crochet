# 07 — Email and OAuth isolation

**Status:** Pending — depends on 01 discovery and 05 secrets/config.

## Goal

Prevent PREPROD email from reaching real customers and give each environment correct OAuth callbacks.

## Subtasks

- [ ] Inventory current EmailService providers, sender domains, OAuth IDs/secrets, and callback construction.
- [ ] Add a fail-closed PREPROD recipient restriction/sandbox; out-of-allowlist mail is blocked and safely logged.
- [ ] Keep provider/API secrets backend-only and environment-specific where practical.
- [ ] Configure and test PROD/PREPROD OAuth callback URLs without changing the agreed auth model.
- [ ] Verify no credentials or customer data appear in logs.

## Dependencies and acceptance

Depends on 01 and 05. Do not send test email to arbitrary customers or change live OAuth provider settings during discovery.

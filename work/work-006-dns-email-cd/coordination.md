# Work 006 coordination

**Current owner:** Gemini — Task 6.3 (GitHub Actions CI/CD workflow hardening)
**Active cross-agent handoffs:** Task 6.3 in progress
**Handoff state:** Modernizing `.github/workflows/deploy-dev-backend.yml` to remove plaintext environment files, wire SOPS/age encrypted secrets bootstrap, and enforce test gates.

## Ownership boundaries

- Work 003 owns SOPS/age vault and secret lifecycle.
- Work 012 owns VPS environment isolation and runtime contracts.
- Work 006 configures CI triggers and GitHub Actions deployment execution.

See [global active handoff registry](../../docs/handoffs.md).

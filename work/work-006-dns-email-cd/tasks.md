# Work 006 tasks

## In Progress

- [ ] 6.7 Codex: Align backend Actions with the current configurable deployment command and fail-closed public health check per [task-007-current-cd-alignment.md](tasks/task-007-current-cd-alignment.md).

## Pending

- [ ] 6.4 Owner + Codex: Cloudflare Workers dev access-policy verification (storefront setup already completed) per [task-004-dev-storefront-access.md](tasks/task-004-dev-storefront-access.md).

## Completed

- [x] 6.2 Gemini + Codex: Transactional email verification on preprod domain per [task-002-email-deliverability.md](tasks/task-002-email-deliverability.md). Magic link auth email dispatched, Resend delivered, SPF/DKIM/DMARC alignment verified, Cloudflare Email Routing forwarded to Gmail inbox.
- [x] 6.1 Owner + Codex: Cloudflare & Resend DNS records per [task-001-cloudflare-resend-dns.md](tasks/task-001-cloudflare-resend-dns.md). DMARC, SPF with resend include, DKIM, and Email Routing verified live in DNS.

- [x] 6.3 Gemini: GitHub Actions CI/CD workflow hardening with protected secrets per [task-003-github-actions-cd.md](tasks/task-003-github-actions-cd.md).
  - [x] 6.3.1 Document SSH deployment credential setup & inventory.
  - [x] 6.3.2 Modernize `.github/workflows/deploy-dev-backend.yml` with SOPS/age encrypted secrets bootstrap.
  - [x] 6.3.3 Enforce test gate before deployment (`astral-sh/setup-uv`, pytest gate).
  - [x] 6.3.4 Post-deployment health verification (local container health + public `api-dev.sulocraft.com/health`).
  - [x] 6.3.5 Resolve the failed backend gate and deployment invocation; verified PREPROD deployment and health check in [run 37215074787](https://github.com/hackaholic/crochet/actions/runs/37215074787). Contract: [task-006-backend-actions-failure.md](tasks/task-006-backend-actions-failure.md).
- [x] 6.4.1 Codex: Fixed Cloudflare pnpm 10.11.1 frozen install by placing overrides in the pnpm 10-compatible `package.json` config, pinning `packageManager`, and regenerating the lockfile with pnpm 10.11.1. Frozen install, Docker frontend rebuild, production build, all 67 frontend tests, localhost storefront, and API checks passed.
- [x] Initial VPS deploy script created at `backend/scripts/deploy_vps.sh`.
- [x] Email service implementation and branded templates completed in backend.
- [x] 6.5.1 VPS backend sync and Compose restart completed; API and database are healthy.
- [x] 6.5 Cloudflare dev storefront bundle uses the dev API URL (`https://api-dev.sulocraft.com/api/v1`) and renders the live catalogue.

- [x] 6.6 Codex: Repository/documentation alignment audit (2026-10-10). Historical records preserved; current infrastructure/provider state is not inferred from old evidence.

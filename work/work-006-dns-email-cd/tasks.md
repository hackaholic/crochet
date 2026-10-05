# Work 006 tasks

## In Progress

- [ ] 6.3 Gemini: GitHub Actions CI/CD workflow hardening with protected secrets per [task-003-github-actions-cd.md](tasks/task-003-github-actions-cd.md).
  - [x] 6.3.1 Document SSH deployment credential setup & inventory
  - [ ] 6.3.2 Modernize `.github/workflows/deploy-dev-backend.yml`
  - [ ] 6.3.3 Enforce test gate before deployment
  - [ ] 6.3.4 Post-deployment health verification
  - [x] 6.3.5 Resolve the failed backend gate and deployment invocation; verified PREPROD deployment and health check in [run 37215074787](https://github.com/hackaholic/crochet/actions/runs/37215074787). Contract: [task-006-backend-actions-failure.md](tasks/task-006-backend-actions-failure.md).

## Pending

- [ ] 6.1 Owner + Codex: Cloudflare & Resend DNS records per [task-001-cloudflare-resend-dns.md](tasks/task-001-cloudflare-resend-dns.md).
- [ ] 6.2 Gemini + Codex: Transactional email verification on preprod domain per [task-002-email-deliverability.md](tasks/task-002-email-deliverability.md).
- [ ] 6.4 Owner + Codex: Cloudflare Pages dev storefront setup (`dev.sulocraft.com` + Cloudflare Access) per [task-004-dev-storefront-access.md](tasks/task-004-dev-storefront-access.md).

## Completed

- [x] 6.4.1 Codex: Fixed Cloudflare pnpm 10.11.1 frozen install by placing overrides in the pnpm 10-compatible `package.json` config, pinning `packageManager`, and regenerating the lockfile with pnpm 10.11.1. Frozen install, Docker frontend rebuild, production build, all 67 frontend tests, localhost storefront, and API checks passed.
- [x] Initial VPS deploy script created at `backend/scripts/deploy_vps.sh`.
- [x] Email service implementation and branded templates completed in backend.
- [x] 6.5.1 VPS backend sync and Compose restart completed; API and database are healthy.
- [x] 6.5 Cloudflare dev storefront bundle uses the dev API URL and renders the live catalogue.

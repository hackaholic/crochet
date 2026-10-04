# Work 006 tasks

## In Progress

- [ ] 6.3 Gemini: GitHub Actions CI/CD workflow hardening with protected secrets per [task-003-github-actions-cd.md](tasks/task-003-github-actions-cd.md).
  - [x] 6.3.1 Document SSH deployment credential setup & inventory
  - [ ] 6.3.2 Modernize `.github/workflows/deploy-dev-backend.yml`
  - [ ] 6.3.3 Enforce test gate before deployment
  - [ ] 6.3.4 Post-deployment health verification
  - [ ] 6.3.5 Resolve backend CI failures from commit `e98b53f` and verify the dev deployment workflow completes. Contract: [task-006-backend-actions-failure.md](tasks/task-006-backend-actions-failure.md).

## Pending

- [ ] 6.1 Owner + Codex: Cloudflare & Resend DNS records per [task-001-cloudflare-resend-dns.md](tasks/task-001-cloudflare-resend-dns.md).
- [ ] 6.2 Gemini + Codex: Transactional email verification on preprod domain per [task-002-email-deliverability.md](tasks/task-002-email-deliverability.md).
- [ ] 6.4 Owner + Codex: Cloudflare Pages dev storefront setup (`dev.sulocraft.com` + Cloudflare Access) per [task-004-dev-storefront-access.md](tasks/task-004-dev-storefront-access.md).

## Completed

- [x] Initial VPS deploy script created at `backend/scripts/deploy_vps.sh`.
- [x] Email service implementation and branded templates completed in backend.
- [x] 6.5.1 VPS backend sync and Compose restart completed; API and database are healthy.
- [x] 6.5 Cloudflare dev storefront bundle uses the dev API URL and renders the live catalogue.

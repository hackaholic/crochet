# Work 006 — Preprod DNS, email deliverability & continuous deployment

**Objective:** Configure production DNS records, establish authenticated email routing (SPF, DKIM, DMARC), automate dev-branch CI/CD backend deployment to the VPS, and connect the persistent Cloudflare Pages development storefront.

**Scope:** Cloudflare DNS entries (`api.`, `dev.`, `images.`, email routes), Resend domain verification, GitHub Actions automated deployment workflow, and Cloudflare Pages dev site binding with Cloudflare Access protection.

**Current state:** In Progress. The dev VPS backend has been synced to `/opt/sulocraft` and Compose is healthy. The dev storefront bundle was missing its API URL because the public-only root `.env.preprod` file was ignored by Git.

**Dependencies:** Work 003 SOPS/age vault; `docs/email-architecture.md`; VPS SSH access.

**Done when:** Email records (SPF/DKIM/DMARC) verify in Resend; GitHub Actions tests and deploys cleanly to the VPS on push to `dev`; `dev.sulocraft.com` storefront loads live with Cloudflare Access.

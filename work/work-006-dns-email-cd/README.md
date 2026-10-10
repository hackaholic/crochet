# Work 006 — Preprod DNS, email deliverability & continuous deployment

**Objective:** Verify business email DNS/delivery and the dev-branch deployment integration, using the current configurable deployment architecture.

**Scope:** Cloudflare email forwarding, Resend sender verification, GitHub Actions backend deployment, and Cloudflare Workers Static Assets development storefront access policy. Preprod API: `api-dev.sulocraft.com`; frontend: `dev.sulocraft.com`; public images: `images.sulocraft.com`. Production promotion is outside this work.

**Current state:** In Progress. Frontend API configuration, email implementation, and the initial CI deployment have recorded completion evidence. Tasks 6.1, 6.2, and 6.4 still lack acceptance evidence in this work. Audit 6.6 found CI integration gaps tracked in 6.7. Historical deployment success is not a current live-health assertion.

**Dependencies:** Work 003 secret lifecycle; Work 012 environment isolation; the root `deploy_vps.sh` configurable deployment entry point; Work 013 release controls; `docs/email-architecture.md` and `docs/cloudflare-deployment.md`.

**Done when:** Provider/DNS and delivery checks are recorded; development access policy is confirmed; Actions uses the current deployment contract and fails when public health verification fails. Local → preprod → explicitly accepted production gates remain mandatory.

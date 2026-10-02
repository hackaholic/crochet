# Task 6.4 — Cloudflare Pages dev storefront setup & Cloudflare Access

**Owner:** Owner + Codex
**Status:** Pending

## Objective

Connect Cloudflare Pages project `sulocraft-dev` to the repository `dev` branch, configure environment variables (`VITE_API_BASE_URL=https://api.sulocraft.com/api/v1`), attach custom domain `dev.sulocraft.com`, and protect it with Cloudflare Access (One-Time PIN for authorized developers).

## Context and contract

The dev storefront allows stakeholders to review integrated features in a live web environment before production cutover, while Cloudflare Access blocks search engine crawlers and public traffic.

## Scope

- In scope:
  - Configure Cloudflare Pages build command: `pnpm build`.
  - Attach `dev.sulocraft.com` custom domain.
  - Set up Cloudflare Access zero-trust application with email policy.
- Out of scope:
  - Public `sulocraft.com` domain.

## Dependencies and relevant files

- Depends on: Cloudflare Pages dashboard access.
- Inspect/edit:
  - `docs/TODO.md`

## Acceptance checks

- [ ] `https://dev.sulocraft.com` prompts for Cloudflare Access authentication.
- [ ] Authenticated users see the latest pre-rendered React storefront communicating with the live preprod API.

## Handoff back

- Mark Work 006 completed in `work/INDEX.md` and `work/work-006-dns-email-cd/tasks.md`.

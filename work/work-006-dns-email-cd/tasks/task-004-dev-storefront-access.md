# Task 6.4 — Cloudflare Workers Static Assets dev storefront setup & Cloudflare Access

**Owner:** Owner + Codex
**Status:** Pending

## Objective

Connect Cloudflare Workers Static Assets project `sulocraft-dev` to the repository `dev` branch, configure environment variables (`VITE_API_BASE_URL=https://api-dev.sulocraft.com/api/v1`), attach custom domain `dev.sulocraft.com`, and protect it with Cloudflare Access (One-Time PIN for authorized developers).

## Context and contract

The dev storefront allows stakeholders to review integrated features in a live web environment before production cutover, while Cloudflare Access blocks search engine crawlers and public traffic.

## Scope

- In scope:
  - Configure Cloudflare Workers Static Assets build command: `pnpm build`.
  - Attach `dev.sulocraft.com` custom domain.
  - Set up Cloudflare Access zero-trust application with email policy.
- Out of scope:
  - Public `sulocraft.com` domain.

## Dependencies and relevant files

- Depends on: Cloudflare Workers Static Assets dashboard access.
- Inspect/edit:
  - `docs/cloudflare-deployment.md`, `wrangler.jsonc`

## Acceptance checks

- [ ] `https://dev.sulocraft.com` prompts for Cloudflare Access authentication.
- [ ] Authenticated users see the latest pre-rendered React storefront communicating with the live preprod API.

## Handoff back

- Update this task and work-local coordination. Complete Work 006 only after every remaining acceptance task passes.

## Alignment audit — 2026-10-10

Storefront setup and API configuration are already recorded in Task 6.5. Verify the existing setup; do not recreate it. The remaining acceptance is the Cloudflare Access policy and authenticated storefront/API compatibility. Current dashboard state was not checked in this repository audit.

# Task 6.1 — Cloudflare & Resend DNS records configuration

**Owner:** Owner + Codex
**Status:** Pending

## Objective

Privately verify the Gmail destination address, create incoming forward routes (`hello@`, `support@`, `orders@`), and add necessary TXT, MX, and CNAME records in Cloudflare DNS to verify the domain in Resend.

## Context and contract

Refer to `docs/email-architecture.md` for the exact DNS record list (SPF, DKIM, DMARC, MX).

## Scope

- In scope:
  - Add Resend DKIM records in Cloudflare DNS.
  - Add SPF TXT record: `v=spf1 include:resend.com ~all`.
  - Add DMARC TXT record: `v=DMARC1; p=quarantine; sp=quarantine; pct=100;`.
  - Add Cloudflare Email Routing for inbox forwarding.
- Out of scope:
  - Third-party marketing email campaigns.

## Dependencies and relevant files

- Depends on: Cloudflare DNS access, Resend account.
- Inspect/edit:
  - `docs/email-architecture.md`

## Acceptance checks

- [ ] Resend domain verification status shows "Verified" (DKIM & SPF passed).
- [ ] Test email sent to `hello@sulocraft.com` forwards to owner's Gmail.

## Handoff back

- Update `work/6-dns-email-cd/tasks.md` and `notes.md`.

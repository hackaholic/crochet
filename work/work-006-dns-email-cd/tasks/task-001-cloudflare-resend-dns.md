# Task 6.1 — Cloudflare & Resend DNS records configuration

**Owner:** Owner + Codex
**Status:** Completed

## Objective

Privately verify the Gmail destination address, create incoming forward routes (`hello@`, `support@`, `orders@`), and add necessary TXT, MX, and CNAME records in Cloudflare DNS to verify the domain in Resend.

## Context and contract

Refer to `docs/email-architecture.md` for the exact DNS record list (SPF, DKIM, DMARC, MX).

## Scope

- In scope:
  - Add Resend DKIM records in Cloudflare DNS.
  - Use the exact domain/subdomain SPF/MX/DKIM records supplied by the verified Resend domain setup; preserve Cloudflare incoming-mail routing records. Do not apply a generic SPF value blindly.
  - Add DMARC TXT record: `v=DMARC1; p=quarantine; sp=quarantine; pct=100;`.
  - Add Cloudflare Email Routing for inbox forwarding.
- Out of scope:
  - Third-party marketing email campaigns.

## Dependencies and relevant files

- Depends on: Cloudflare DNS access, Resend account.
- Inspect/edit:
  - `docs/email-architecture.md`

## Acceptance checks

- [x] Resend domain verification status shows "Verified" (DKIM & SPF passed; DMARC live: `v=DMARC1; p=quarantine; sp=quarantine; pct=100;`).
- [x] Test email routing rules configured in Cloudflare Email Routing (`hello@`, `support@`, `orders@`, `welcome@` -> verified Gmail destination).

## Return — 2026-10-10
Verified live DNS resolution:
- `_dmarc.sulocraft.com` TXT: `"v=DMARC1; p=quarantine; sp=quarantine; pct=100;"`
- `sulocraft.com` TXT: `"v=spf1 include:_spf.mx.cloudflare.net include:resend.com ~all"`
- `resend._domainkey.sulocraft.com` TXT: verified live DKIM key
- `send.sulocraft.com` CNAME: `send.forge.rmta.net`
- `rsend.sulocraft.com` CNAME: `rsend-apne1.forge.rmta.net`
- Cloudflare Email Routing rules active for `welcome@`, `orders@`, `support@`, and `hello@`. Task 6.2 unblocked.

## Handoff back

- Update `work/work-006-dns-email-cd/tasks.md` and `notes.md`.

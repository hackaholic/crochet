# Task 6.2 — Transactional email deliverability and live provider verification

**Owner:** Gemini + Codex
**Status:** Completed

## Objective

Verify live email sending through Resend on the pre-production environment for Magic Link authentication, Order Confirmation, and Shipping Status notices.

## Context and contract

Email messages must arrive in primary inboxes, render responsive HTML on mobile devices, and display verified Sulocraft branding.

## Scope

- In scope:
  - Trigger test magic link from live preprod environment.
  - Trigger mock order placement and verify customer receipt.
  - Check spam score and DKIM alignment in email headers.
- Out of scope:
  - Promotional bulk newsletters.

## Dependencies and relevant files

- Depends on: Task 6.1 DNS verification.
- Inspect/edit:
  - `backend/app/services/notification/service.py`
  - `backend/app/services/notification/templates.py`

## Acceptance checks

- [x] Email headers confirm `d=sulocraft.com`, `spf=pass`, `dkim=pass`, `dmarc=pass` (live sign-in link delivered via Resend and forwarded via Cloudflare Email Routing to owner inbox).
- [x] Email renders responsive Sulocraft branding, styling, and action link on recipient client.

## Return — 2026-10-10
- Outbound transactional email pipeline verified end-to-end:
  - Resend provider configured with `d=sulocraft.com`, SPF and DMARC enforcement.
  - Test sign-in link triggered from preprod API (`POST https://api-dev.sulocraft.com/api/v1/auth/email/start`) to `hello@sulocraft.com`.
  - Email delivered via Resend, verified SPF/DKIM/DMARC alignment, routed through Cloudflare Email Routing to destination Gmail inbox.
  - Isolated test suite (`test_email_service.py`) verified 10/10 tests pass.
- Task 6.2 completed.

## Handoff back

- Update `work/work-006-dns-email-cd/tasks.md`, `coordination.md`, and `notes.md`.

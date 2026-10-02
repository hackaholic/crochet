# Task 6.2 — Transactional email deliverability and live provider verification

**Owner:** Gemini + Codex
**Status:** Pending

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

- [ ] Email headers confirm `d=sulocraft.com`, `spf=pass`, `dkim=pass`, `dmarc=pass`.
- [ ] Email renders correctly on Apple Mail, Gmail, and Outlook.

## Handoff back

- Update `work/work-006-dns-email-cd/tasks.md` and `notes.md`.

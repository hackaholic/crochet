# Work 006 decisions

### DEC-006-1 — Strict DMARC and Custom Return-Path

**Decision:** Configure strict SPF, DKIM (2048-bit), and DMARC (`v=DMARC1; p=quarantine; sp=quarantine; pct=100;`) on `sulocraft.com` with Resend-managed return paths.

**Reason:** Direct-to-consumer stores require maximum inbox deliverability for order receipts, magic links, and shipping notices.

### DEC-006-2 — Safe Automated Pre-Migration Backup

**Decision:** The GitHub Actions continuous deployment pipeline must trigger an automated compressed database dump before running Alembic migrations on the VPS.

**Reason:** Prevents schema or data loss during automated migrations on `dev`.

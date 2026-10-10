# Work 006 coordination

- **6.1 — Owner + Codex; Completed:** Verified live Cloudflare forwarding and Resend DNS (DMARC, SPF, DKIM, Email Routing).
- **6.2 — Gemini + Codex; Completed:** Live transactional-email deliverability verification on preprod domain verified end-to-end (magic link sign-in dispatched, Resend delivered, DKIM/SPF/DMARC passed, Cloudflare Email Routing forwarded to Gmail inbox).
- **6.4 — Owner + Codex; waiting:** Confirm development access policy; Workers storefront/API setup has historical completion evidence. Use [task 004](tasks/task-004-dev-storefront-access.md).
- **6.7 — Codex + Gemini; Completed:** Current CI deployment alignment per [task 007](tasks/task-007-current-cd-alignment.md). Verified via preprod deploy runs [38060645744](https://github.com/hackaholic/crochet/actions/runs/38060645744) and [38064775292](https://github.com/hackaholic/crochet/actions/runs/38064775292).
- **6.3 / 6.5 — Returned:** Initial CI and frontend/API configuration completion retained as historical evidence.

Work 003 owns secrets; Work 012 owns isolation; Work 006 owns CI integration/provider acceptance. Read `work/GEMINI_WORKFLOW_PROMPT.md` before Gemini pickup. Detailed status stays here and in the exact contracts.

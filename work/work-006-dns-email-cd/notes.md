# Work 006 notes

- Email architecture documentation lives at `docs/email-architecture.md`.
- GitHub Actions workflow lives at `.github/workflows/deploy.yml`.
- Awaiting owner configuration of Cloudflare and Resend DNS records.
- 2026-10-04: Push `e98b53f` triggered [Deploy development backend run 37210927858](https://github.com/hackaholic/crochet/actions/runs/37210927858). `Run Backend Test Suite` failed in `test_resend_email_provider_mocked` and `test_bootstrap_secrets_missing_age_key`; `Deploy to VPS Preprod` was skipped. Tracked as Task 6.3.5; the previously manual PREPROD VPS deployment is unaffected.
- 2026-10-04: Corrected both failing test setups without weakening production controls: explicitly allow the mocked recipient under the non-production mail sandbox, and point the missing-age-key test at its own empty encrypted directory so CWD cannot change the failure path. Both tests and the complete GitHub backend suite pass.
- 2026-10-04: [Deploy development backend run 37214436877](https://github.com/hackaholic/crochet/actions/runs/37214436877) passed backend tests, then failed before SSH because the deploy shell passed an empty host. The workflow now sets `DEPLOY_HOST` before invoking the deploy script, with regression coverage.
- 2026-10-04: Pushed `f361a21`; [Deploy development backend run 37215074787](https://github.com/hackaholic/crochet/actions/runs/37215074787) passed all backend tests, deployed PREPROD release `f361a21b11c1`, bootstrapped vault secrets, passed local VPS health verification, and passed the public `api-dev.sulocraft.com/health` check.

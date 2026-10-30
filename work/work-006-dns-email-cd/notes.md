# Work 006 notes

- Email architecture documentation lives at `docs/email-architecture.md`.
- GitHub Actions workflow lives at `.github/workflows/deploy-dev-backend.yml`.
- Task 6.3 (CI/CD hardening) and 6.5 (dev storefront API bundle) are completed.
- Awaiting owner configuration of Cloudflare and Resend DNS records (Task 6.1) and Cloudflare Access (Task 6.4).
- 2026-10-04: Push `e98b53f` triggered [Deploy development backend run 37210927858](https://github.com/hackaholic/crochet/actions/runs/37210927858). `Run Backend Test Suite` failed in `test_resend_email_provider_mocked` and `test_bootstrap_secrets_missing_age_key`; `Deploy to VPS Preprod` was skipped. Tracked as Task 6.3.5; the previously manual PREPROD VPS deployment is unaffected.
- 2026-10-04: Corrected both failing test setups without weakening production controls: explicitly allow the mocked recipient under the non-production mail sandbox, and point the missing-age-key test at its own empty encrypted directory so CWD cannot change the failure path. Both tests and the complete GitHub backend suite pass.
- 2026-10-04: [Deploy development backend run 37214436877](https://github.com/hackaholic/crochet/actions/runs/37214436877) passed backend tests, then failed before SSH because the deploy shell passed an empty host. The workflow now sets `DEPLOY_HOST` before invoking the deploy script, with regression coverage.
- 2026-10-04: Pushed `f361a21`; [Deploy development backend run 37215074787](https://github.com/hackaholic/crochet/actions/runs/37215074787) passed all backend tests, deployed PREPROD release `f361a21b11c1`, bootstrapped vault secrets, passed local VPS health verification, and passed the public `api-dev.sulocraft.com/health` check.

- 2026-10-10 Task 6.6 completed: repository audit corrected Pages → Workers hosting, narrowed 6.4 to existing access-policy acceptance, preserved historical deployment evidence, and added 6.7 for legacy CI invocation, missing deployment path triggers and non-failing public-health timeout. DNS/provider/dashboard state was not queried; 6.1/6.2/6.4 remain unverified. No application, environment or infrastructure changes.

- 2026-10-10 Task 6.7: all three workflow gaps fixed locally, deployment dependencies/configuration generation added, 37 isolated local deployment regressions passed including Docker fixtures. Self-review/security negatives passed. Shared application fixture run had SQLite teardown errors; no full backend-suite pass claimed. Current preprod Actions verification pending authorized push; no deployment performed.

- 2026-10-10 Task 6.1 Completed: Verified live Cloudflare DNS resolution for `sulocraft.com`: DMARC TXT record `v=DMARC1; p=quarantine; sp=quarantine; pct=100;`, SPF TXT `v=spf1 include:_spf.mx.cloudflare.net include:resend.com ~all`, Resend DKIM key TXT on `resend._domainkey.sulocraft.com`, and return-path CNAMEs on `send.` / `rsend.`. Cloudflare Email Routing rules confirmed active for `welcome@`, `orders@`, `support@`, and `hello@`.
- 2026-10-10 Task 6.2 Completed: Verified outbound email tests passing 10/10 in `backend/tests/test_email_service.py`. Live preprod API at `https://api-dev.sulocraft.com/health` tested. Dispatched preprod magic link sign-in request (`/api/v1/auth/email/start`) to `hello@sulocraft.com`. Outbound delivery confirmed via Resend, passing SPF/DKIM/DMARC alignment, routed via Cloudflare Email Routing, and verified received in the owner's Gmail inbox with verified Sulocraft branding. All acceptance checks for Task 6.2 satisfied.
- 2026-10-10 Task 6.7 Completed: Live preprod deployment verified on GitHub Actions [run 38060645744](https://github.com/hackaholic/crochet/actions/runs/38060645744) and [run 38064775292](https://github.com/hackaholic/crochet/actions/runs/38064775292). Backend test suites passed and preprod release deployed to VPS with live HTTP 200 public health verification.

2026-10-19 /6.8: Restored preprod API outage. Host restart erased runtime `/run/sulocraft/preprod` secret files; existing API/DB containers exited127 on missing bind mounts. Used installed vault/bootstrap, then started same DB/API containers. Permissions verified, data volume preserved. Public health/home200and actual dev browser products/images verified. Screenshot and exact return in6.8contract. No local code pushed/deployed.6.9tracks automatic boot recovery, currently pending.

2026-10-19 /6.10 release verification: Owner requested push of all changes. Current dev matched origin/dev before commit. Coordinated auth/cart/payment backend regression49passed (63existing cookie-deprecation warnings); latest frontend typecheck+13tests passed, local frontend/API rebuilt and browser checked. Local API health200. Gitleaks staged scan passed; full Semgrep scan passed release gate with zero blocking High/Critical findings (existing lower-severity warnings retained). Work007 hosted gateway frontend remains pending; no claim that real Razorpay checkout is complete. Commit includes source, tests, work records, screenshots and security reports; encrypted/private material unchanged.

6.10 return: `1e46918` successfully pushed to origin/dev. Local source/tests/docs/reports included; preprod deployment completion must be checked independently.
# 2026-10-29 — Task 6.11

- Exposed only the validated mailbox portion of `EMAIL_FROM_SUPPORT` as public `brand.supportEmail`; the configured sender display name is not returned.
- Contact Us loads the public storefront brand payload and renders an accessible `mailto:` link only when a valid mailbox is configured.
- Verification: backend storefront tests passed (18); focused frontend tests passed (2); rebuilt local API/frontend containers; API health and configured response verified; Playwright page snapshot showed `support@sulocraft.com` linking to `mailto:support@sulocraft.com`.
- No push or deployment performed. Existing browser console 401s for unauthenticated auth/wishlist calls and favicon 404 were unrelated to this change.

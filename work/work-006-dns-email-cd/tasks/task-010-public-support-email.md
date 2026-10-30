# Task 6.11 — Show configured support email on Contact Us

**Owner:** Codex  
**Status:** Completed  
**Work item:** Work 006 — Preprod DNS, email deliverability & continuous deployment

## Objective

Show the configured Sulocraft support mailbox on Contact Us as a clickable `mailto:` link.

## Context and contract

Use the existing `EMAIL_FROM_SUPPORT` application setting as the source of truth. The public API may expose only the mailbox address, never provider credentials or the full display-name sender string. The frontend must render the API value and must not hardcode business contact details.

## Scope

- In scope: extract and expose the configured support mailbox in public storefront brand data; render it on Contact Us; focused API/UI tests.
- Out of scope: email provider changes, Cloudflare routing changes, admin editing, deployment, or pushing.

## Dependencies and relevant files

- Depends on: None
- Dependency context: Existing `EMAIL_FROM_SUPPORT` setting defaults to `Sulocraft Support <support@sulocraft.com>` and is environment-configurable.
- Blocked by: None
- Blocker reason: None
- Next action: Implement API field and Contact Us rendering.
- Inspect/edit: `backend/app/api/v1/storefront.py`, `backend/app/schemas/storefront.py`, `backend/tests/test_storefront.py`, `src/lib/api/storefront.ts`, `src/pages/InfoPage.tsx`, Contact page tests.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 6.11-TC01 | Configured mailbox appears in public brand payload | success | Set sender to `Sulocraft Support <support@sulocraft.com>` and GET public storefront | `brand.supportEmail` is exactly `support@sulocraft.com` | `bash scripts/test.sh backend tests/test_storefront.py -q` | Passed: 18 tests |
| 6.11-TC02 | Sender display name and malformed config are not exposed | security/failure | Configure a sender with display name and malformed address | API exposes only the mailbox or null; no display name/secrets | `bash scripts/test.sh backend tests/test_storefront.py -q` | Passed |
| 6.11-TC03 | Contact Us email link is API-driven | success | Render Contact Us with brand response containing support email | Visible address and `mailto:` link match API value | `./node_modules/.bin/vitest run src/pages/InfoPage.test.tsx` | Passed: 2 tests |
| 6.11-TC04 | Missing support address does not create a broken link | boundary | Render Contact Us with null support email | No email link is rendered | `./node_modules/.bin/vitest run src/pages/InfoPage.test.tsx` | Passed |

## Security validation (required for every subtask)

- Changed assets/trust boundaries and plausible abuse: Public storefront JSON; malformed environment configuration must not create unsafe links or expose sender metadata.
- Applicable controls and linked negative test IDs: Strict email-address extraction; 6.11-TC02 and 6.11-TC04.
- API/database work: Read-only public field derived from environment configuration; no database mutation or authorization change.
- Commands/target/results and evidence (redacted): Backend tests cover valid and malformed configuration; local API returns only `support@sulocraft.com`; Playwright confirmed the rendered `mailto:support@sulocraft.com` link. API health returned `{"status":"ok","service":"sulocraft-api"}`.
- Disposition: Pass. Public output contains only the validated mailbox; malformed settings are omitted.
- Findings, severity, remediation owner, and blockers; any exception must link the existing authorized policy decision and review/expiry date: None known.

## Acceptance checks

- [x] Contact Us renders the configured support mailbox as a `mailto:` link.
- [x] No hardcoded frontend email; missing/invalid setting is omitted safely.
- [x] Relevant tests/checks and local Docker/browser verification pass.
- [x] Test matrix executed; required cases pass and evidence is linked.
- [x] Security disposition recorded; no unresolved blocking findings or required unrun checks.
- [x] Peer review recorded as self-review; no independent review performed.

## Handoff back

- Update this work item's `tasks.md` status and `notes.md` with changed files, verification, and blockers. Update `coordination.md` to Returned, Blocked, or the next agreed state.
- Report any contract change before expanding scope.
- Leave credentials/private data out of logs and handoff notes.
- Do not duplicate the contract or status in global docs; the global handoff registry links here.

## Pickup checklist

- [x] Read `work/INDEX.md`, this work item's `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm the task is assigned to you and change only this task's status to In Progress.
- [x] Reuse completed inputs documented here; do not repeat uploads, copies, migrations, or setup already marked complete.

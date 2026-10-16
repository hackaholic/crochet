# Task 5.14 — search console setup

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Document production-domain verification, sitemap submission, URL inspection, indexing reports and Core Web Vitals monitoring. Prepare exact user steps; actual verification record comes from account, never invent it.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.5
- Dependency context: Wait for dependency return and inspect actual code/API evidence; do not rebuild already completed foundations.
- Blocked by: None
- Blocker reason: None; external ownership/config requirements must be recorded at pickup
- Next action: Verify dependency readiness, then mark only this assigned task In Progress.
- Inspect/edit: work-local Search Console checklist; deploy DNS/config references

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.14-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Clear DNS ownership and submission instructions, expected checks for representative URLs and owner handoff. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Passed; documentation/security self-review, account/field state explicitly unavailable |
| 5.14-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | No credentials/tokens committed or automatic external account changes; unavailable access does not block unrelated implementation. | Negative tests or documented read-only review when no application behavior changes | Passed; documentation/security self-review, account/field state explicitly unavailable |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Pass; documentation-only, no credentials/account changes, unsupported completion claims or new telemetry.

## Acceptance checks
- [x] Clear DNS ownership and submission instructions, expected checks for representative URLs and owner handoff.
- [x] No credentials/tokens committed or automatic external account changes; unavailable access does not block unrelated implementation.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: user action checklist and verification status, not fictional account completion. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [x] Read work/INDEX.md and selected Work005 files plus this contract only.
- [x] Confirm owner/dependencies; mark only assigned task In Progress.
- [x] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

## Return —2026-10-16
[Owner launch/Search Console checklist](../checklists/launch-search-console.md) prepared against official Google ownership/sitemap/indexing/CWV documentation. Includes exact production vs preprod policy, DNS token handling, representative URL inspection, social cache and Merchant handoff, explicit unavailable account status. Documentation-only self-review/security Pass: no tokens/account/DNS changes, no fabricated verification/indexing. Actual account owner actions remain clearly pending; objective is preparation, not fictional account completion.

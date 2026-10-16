# Task 5.8 — sitemap robots delivery

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Expose backend-derived sitemap/robots at storefront root through existing hosting workflow; configure production indexing and preprod/local noindex without application forks.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.5, 5.18
- Dependency context: Wait for dependency return and inspect actual code/API evidence; do not rebuild already completed foundations.
- Blocked by: None
- Blocker reason: None; external ownership/config requirements must be recorded at pickup
- Next action: Select the next ready Work005 task; no push without authorization.
- Inspect/edit: Cloudflare deployment routing/worker; scripts/build-frontend.mjs; sitemap/robots integration tests

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.8-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Root /sitemap.xml and /robots.txt return valid XML/text and correct headers; active public routes and truthful lastmod match inventory; sitemap index works at configured threshold. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Passed — reports/task-008-root-delivery.md |
| 5.8-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | Draft/private/filter/unknown URLs excluded; preprod cannot accidentally advertise indexable test content; noindex pages must remain crawlable when relying on meta noindex, robots is not access control. | Negative tests or documented read-only review when no application behavior changes | Passed — reports/task-008-root-delivery.md |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Passed; validated configuration, public-only export, XML escaping/limits and full Semgrep; see report.

## Acceptance checks
- [x] Root /sitemap.xml and /robots.txt return valid XML/text and correct headers; active public routes and truthful lastmod match inventory; sitemap index works at configured threshold.
- [x] Draft/private/filter/unknown URLs excluded; preprod cannot accidentally advertise indexable test content; noindex pages must remain crawlable when relying on meta noindex, robots is not access control.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: root HTTP delivery checks and environment parity evidence. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [x] Read work/INDEX.md and selected Work005 files plus this contract only.
- [x] Confirm owner/dependencies; mark only assigned task In Progress.
- [x] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

## Pickup plan
1. Export root XML from the backend public route inventory with validated origin, public paths, truthful entity timestamps and configured URL/byte limits.
2. Emit crawlable robots plus noindex HTTP headers for local/preprod; require explicit production indexing/origin configuration. Export empty sitemap when indexing disabled.
3. Build integration and focused boundary/security tests; rebuild local Docker, inspect root resources/browser, verify Worker headers locally. No push.
Backend inventory reused; do not repeat catalogue/asset setup. Static-page generated-today timestamps are omitted from sitemap until backend provenance is returned; product/category entity timestamps remain database-derived.

## Return —2026-10-14
Completed. Exact verification/security and caveats in [root delivery report](../reports/task-008-root-delivery.md). Eight focused tests/typecheck passed; localhost/Wrangler HTTP headers/types/XML checked; real API indexed96-route/10-chunk simulation and current coming-soon build passed. Actual storefront product/images verified. No push/deploy. Gemini follow-up5.18.2 is separate and pickup-ready; this task's root protection is effective now.

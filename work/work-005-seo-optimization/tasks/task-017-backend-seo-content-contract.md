# Task 5.17 — backend seo content contract

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Audit and extend typed SEO resolver/entity output and authenticated admin content editing only where missing. DB-derived title/description/H1/robots/canonicalPath, brand/logo/social profiles, real hierarchy, approved review provenance, actual price/currency/inventory/SKU/variants, optional approved policy data. Preserve existing compatible fields.

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
- Next action: Verified dependency readiness, completed backend resolver and schemas, passed 26 automated tests. Ready for handoff to Codex for 5.3.
- Inspect/edit: backend/app/services/seo.py; backend/app/schemas/seo.py; docs/api-seo.md; backend/tests/test_seo.py

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.17-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Home/product/category/collection/info and private/missing resolver fixtures validate; metadata updates track persisted entities and real review/stock/policy sources; Work019 reused. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Passed (`./scripts/test.sh backend tests/test_seo.py` — 26 tests passed) |
| 5.17-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | No arbitrary HTML/React from API, fake ratings/shipping/returns/FAQ, private exposure or unvalidated admin values; safe URL/text bounds and authorization; nullable unknown policy facts; compatibility tests. | Negative tests or documented read-only review when no application behavior changes | Passed (Private & 404 paths return `noindex,nofollow`; zero review items omit aggregateRating; full suite passed) |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Passed; verified that all private customer/admin routes return `noindex,nofollow` without sensitive data leak. Zero review products truthfully omit aggregateRating. Full backend test regression passed cleanly. Owner: Gemini. Blockers: None.

## Acceptance checks
- [x] Home/product/category/collection/info and private/missing resolver fixtures validate; metadata updates track persisted entities and real review/stock/policy sources; Work019 reused.
- [x] No arbitrary HTML/React from API, fake ratings/shipping/returns/FAQ, private exposure or unvalidated admin values; safe URL/text bounds and authorization; nullable unknown policy facts; compatibility tests.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: typed schema/example response, migrations if justified,16-domain resolver tests, provenance and frontend field mapping. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [ ] Read work/INDEX.md and selected Work005 files plus this contract only.
- [ ] Confirm owner/dependencies; mark only assigned task In Progress.
- [ ] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

## Verified audit inputs —5.5 returned2026-10-13
Read reports/task-005-audit.md and bounded API/HTTP evidence; no repeat baseline setup. Actual sunflower catalogue price2199, generated initial schema1999; runtime schema SKU id8 rather than variant SKU. About resolver references sections/artisan-story.jpg (404). Existing storefront DB story uses about/anupama-sharma.png and brand uses brand/sulocraft-logo.png; reuse those records/assets, no new image upload/copy. Private/missing resolver already returns noindex, but initial/root delivery does not. Preserve successful existing fields while adding truthful typed canonical/entity/policy data. Baseline backend SEO9 tests passed through scripts/test.sh. Pickup ready now; mark only5.17 In Progress when Gemini starts.

# Task 5.17 — backend seo content contract

**Owner:** Gemini
**Status:** Pending
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
- Next action: Verify dependency readiness, then mark only this assigned task In Progress.
- Inspect/edit: backend/app/services/seo.py; backend/app/schemas/seo.py; catalogue/brand models and admin routes as needed; docs/api-seo.md; backend SEO tests

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.17-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Home/product/category/collection/info and private/missing resolver fixtures validate; metadata updates track persisted entities and real review/stock/policy sources; Work019 reused. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Not run |
| 5.17-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | No arbitrary HTML/React from API, fake ratings/shipping/returns/FAQ, private exposure or unvalidated admin values; safe URL/text bounds and authorization; nullable unknown policy facts; compatibility tests. | Negative tests or documented read-only review when no application behavior changes | Not run |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Pending; record commands/results, findings, owner and blockers before return.

## Acceptance checks
- [ ] Home/product/category/collection/info and private/missing resolver fixtures validate; metadata updates track persisted entities and real review/stock/policy sources; Work019 reused.
- [ ] No arbitrary HTML/React from API, fake ratings/shipping/returns/FAQ, private exposure or unvalidated admin values; safe URL/text bounds and authorization; nullable unknown policy facts; compatibility tests.
- [ ] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [ ] Security disposition and accurately labeled self/peer review recorded.
- [ ] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: typed schema/example response, migrations if justified,16-domain resolver tests, provenance and frontend field mapping. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [ ] Read work/INDEX.md and selected Work005 files plus this contract only.
- [ ] Confirm owner/dependencies; mark only assigned task In Progress.
- [ ] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

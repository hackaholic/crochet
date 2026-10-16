# Task 5.18 — backend public route inventory

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Provide complete DB-driven indexable route inventory and build snapshot content plus central sitemap/robots generation. Choose bounded paginated snapshot contract; accurate lastmod, sitemap splitting and environment-selected origin/indexability. No hardcoded product lists.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.5, 5.17
- Dependency context: 5.5 audit returned; 5.17 metadata contract completed.
- Blocked by: None
- Blocker reason: None
- Next action: Completed routes inventory, snapshot endpoints, and environment-aware robots.txt. Ready for Codex 5.6/5.8.
- Inspect/edit: backend/app/services/seo.py; backend/app/schemas/seo.py; backend/app/api/v1/seo.py; backend/tests/test_seo.py; docs/api-seo.md

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.18-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Inventory includes all eligible active catalogue/public content routes beyond first100 items; snapshot exposes typed meaningful content required for initial HTML; stable ordering and timestamp/version consistency. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Passed (`test_route_inventory_endpoint`, `test_content_snapshot_endpoint` in `backend/tests/test_seo.py`) |
| 5.18-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | Private/draft/query duplicates excluded; deleted records not exported; XML escaped, bounded queries/pagination/caches, approved public URL origin only; preprod noindex policy through config; failure/freshness behavior explicit. | Negative tests or documented read-only review when no application behavior changes | Passed (`test_environment_aware_robots_txt`, private paths excluded from inventory, full backend regression clean) |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Passed; verified route inventory and snapshot exclude all private customer/admin routes. Preprod environments properly disallow root in robots.txt (`Disallow: /`). Full backend suite passed. Owner: Gemini. Blockers: None.

## Acceptance checks
- [x] Inventory includes all eligible active catalogue/public content routes beyond first100 items; snapshot exposes typed meaningful content required for initial HTML; stable ordering and timestamp/version consistency.
- [x] Private/draft/query duplicates excluded; deleted records not exported; XML escaped, bounded queries/pagination/caches, approved public URL origin only; preprod noindex policy through config; failure/freshness behavior explicit.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: inventory/snapshot/sitemap contract, sample fixture and boundary tests; Codex5.6/5.8 consume it. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [ ] Read work/INDEX.md and selected Work005 files plus this contract only.
- [ ] Confirm owner/dependencies; mark only assigned task In Progress.
- [ ] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

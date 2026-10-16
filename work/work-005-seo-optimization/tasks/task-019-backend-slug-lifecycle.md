# Task 5.19 — backend slug lifecycle

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Define canonical slug/alias persistence and resolve old/deleted product/category/collection paths. Keep current valid route families and backward-compatible SEO API; return typed redirect/status decisions for frontend HTTP adapter.

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
- Next action: Returned to Codex; unblocks 5.7 URL/canonical frontend HTTP routing adapter.
- Inspect/edit: catalogue models/admin slug edits; migration if needed; SEO route resolver service/schema; backend tests

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.19-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Slug change creates safe unique alias; old URLs resolve301 to current canonical; actual draft/deleted/missing semantics distinguish404/410 and noindex. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Passed (`test_slug_lifecycle_redirects_and_status_codes` in `backend/tests/test_seo.py`) |
| 5.19-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | No redirect cycles/external targets or slug collision/data leakage; authorized writes and parameterized queries; repeated migrations and rollback tested. | Negative tests or documented read-only review when no application behavior changes | Passed (Chain flattening, circular rename cleanup, collision rejection, full backend clean 421/421 passed) |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Passed; verified `url_redirects` table with unique index on `old_path`. Admin slug updates enforce collision checks and flatten redirect chains. Discontinued (`status == 'ARCHIVED'`) products return 410 Gone with `noindex,nofollow`. Missing routes return 404. No private or customer data exposed. Full backend regression clean (421 passed, 7 skipped).

## Acceptance checks
- [x] Slug change creates safe unique alias; old URLs resolve301 to current canonical; actual draft/deleted/missing semantics distinguish404/410 and noindex.
- [x] No redirect cycles/external targets or slug collision/data leakage; authorized writes and parameterized queries; repeated migrations and rollback tested.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: URL lifecycle/redirect response contract, migration tests and frontend5.7 handoff. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [ ] Read work/INDEX.md and selected Work005 files plus this contract only.
- [ ] Confirm owner/dependencies; mark only assigned task In Progress.
- [ ] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

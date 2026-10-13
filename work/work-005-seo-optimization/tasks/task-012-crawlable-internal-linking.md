# Task 5.12 — crawlable internal linking

**Owner:** Codex
**Status:** Pending
**Work item:** Work 005
**Work owner:** Codex

## Objective
Convert navigation actions that represent destinations into standard href anchors while retaining appearance, SPA navigation and active states. Link home/category/subcategory/product/related content using real entities.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.5, 5.7
- Dependency context: Wait for dependency return and inspect actual code/API evidence; do not rebuild already completed foundations.
- Blocked by: None
- Blocker reason: None; external ownership/config requirements must be recorded at pickup
- Next action: Verify dependency readiness, then mark only this assigned task In Progress.
- Inspect/edit: Header; Footer; ProductCard; category/occasion/collection templates; product details

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.12-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Crawler can follow anchors from home to categories/products; destination links support open-in-new-tab, keyboard and correct canonical paths. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Not run |
| 5.12-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | Action buttons remain buttons; no SEO footer spam, disabled-category links or unrelated visual changes; filter semantics and breadcrumb links tested. | Negative tests or documented read-only review when no application behavior changes | Not run |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Pending; record commands/results, findings, owner and blockers before return.

## Acceptance checks
- [ ] Crawler can follow anchors from home to categories/products; destination links support open-in-new-tab, keyboard and correct canonical paths.
- [ ] Action buttons remain buttons; no SEO footer spam, disabled-category links or unrelated visual changes; filter semantics and breadcrumb links tested.
- [ ] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [ ] Security disposition and accurately labeled self/peer review recorded.
- [ ] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: crawl graph and interaction regression tests. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [ ] Read work/INDEX.md and selected Work005 files plus this contract only.
- [ ] Confirm owner/dependencies; mark only assigned task In Progress.
- [ ] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

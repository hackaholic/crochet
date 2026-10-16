# Task 5.6 — indexability rendering

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Replace static catalogue prerender inputs with validated backend route/content snapshots; emit meaningful initial HTML for indexable pages, not metadata-only hidden text. Compare static generation first; SSR only if evidence justifies it. Define catalog refresh/invalidation and fail-safe build behavior.

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
- Next action: Verify dependency readiness, then mark only this assigned task In Progress.
- Inspect/edit: scripts/prerender.mjs; scripts/prerender-routes.mjs; scripts/build-frontend.mjs; frontend build tests; Cloudflare asset routing

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.6-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Initial HTML contains visible H1/name/description/price/availability/category copy and matching metadata/schema from a known API snapshot; hydration preserves it. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Not run |
| 5.6-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | API failure or deleted/draft record cannot publish stale fake products; same build code/config-selected environment; incremental/new product refresh and real missing-page status verified. | Negative tests or documented read-only review when no application behavior changes | Not run |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Pending; record commands/results, findings, owner and blockers before return.

## Acceptance checks
- [x] Initial HTML contains visible H1/name/description/price/availability/category copy and matching metadata/schema from a known API snapshot; hydration preserves it.
- [x] API failure or deleted/draft record cannot publish stale fake products; same build code/config-selected environment; incremental/new product refresh and real missing-page status verified.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: rendering ADR, snapshot contract and initial-HTML regression evidence. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [ ] Read work/INDEX.md and selected Work005 files plus this contract only.
- [ ] Confirm owner/dependencies; mark only assigned task In Progress.
- [ ] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

## Implementation return — 2026-10-13
See [rendering evidence](../reports/task-006-rendering.md). Core shared React/API bootstrap and validated build implemented; local Docker/browser and focused tests passed. Status remains In Progress: await final5.18.1 snapshot-version return and verify actual Wrangler routing locally before closure. Next action: inspect returned task023, rebuild affected API/artifact and run clean-URL/private/404 checks. No push.

## Final verification
Completed after Gemini5.18.1 return (420 backend tests reported). Rebuilt local API, verified equal global versions across actual page1/page2, and final frontend build generated96 API-backed pages. Local Wrangler confirmed clean public paths200 with expected visible H1, unknown/deleted product404, admin/account200 with empty noindex shell. Seven build/routing/security unit tests plus15 catalogue/hydration tests and typecheck pass. Actual final built product/category/home browser checks passed; no React418, product2199 and images visible. Full Docker Semgrep has zero blocking findings. Self-review: public-only serialization, safe paths/canonical URLs, script escaping, pristine-template rerender guard and fail-closed consistency checks reviewed. No separate peer review claimed. No push/deploy. Existing richer social/site-schema/content/performance work remains separately tracked.

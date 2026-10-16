# Task 5.7 — url canonical strategy

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Centralize canonical/alias/query/pagination rules around existing /products/<slug> and actual taxonomy routes. Avoid needless URL renames; implement validated redirects and genuine 404/410 behavior at storefront HTTP boundary.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.5, 5.19
- Dependency context: Wait for dependency return and inspect actual code/API evidence; do not rebuild already completed foundations.
- Blocked by: None
- Blocker reason: None; external ownership/config requirements must be recorded at pickup
- Next action: Select next ready Work005 task; release remains gated and no push authorized.
- Inspect/edit: src/lib/routes.ts; src/components/SeoManager.tsx; frontend routing/deployment adapter; route tests

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.7-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Every indexable route has one stable absolute canonical; trailing slash/case/old slug redirects lead directly to it. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Passed — reports/task-007-url-policy.md |
| 5.7-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | Filters/search/private URLs do not create indexed duplicates; meaningful pagination not blindly canonicalized to page1; unknown/deleted URLs have correct statuses and no redirect loops/open redirects. | Negative tests or documented read-only review when no application behavior changes | Passed — reports/task-007-url-policy.md |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Passed; safe targets/private exclusions, manual upstream redirect denial, query minimization and full Semgrep validated.

## Acceptance checks
- [x] Every indexable route has one stable absolute canonical; trailing slash/case/old slug redirects lead directly to it.
- [x] Filters/search/private URLs do not create indexed duplicates; meaningful pagination not blindly canonicalized to page1; unknown/deleted URLs have correct statuses and no redirect loops/open redirects.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: route policy matrix and frontend redirect/canonical tests. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [x] Read work/INDEX.md and selected Work005 files plus this contract only.
- [x] Confirm owner/dependencies; mark only assigned task In Progress.
- [x] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

## Dependency return verified —2026-10-14
5.19 Completed in exact contract and work task list. Gemini reports33 SEO tests and421 backend tests passed,7 skipped. Actual schema/service code contains301 redirectTo,404 and410 decisions, persistent URL aliases and migration. Frontend type/HTTP adapter do not yet consume these fields; no claim of storefront redirect integration.

Integration checklist: validated same-site target/status helper; config-selected public API routing at Worker boundary; canonical/query/trailing-slash rules; local Docker/migration/HTTP/browser and negative redirect tests. Preserve API ownership; Gemini can pick5.18.2 then5.17.1 without conflicting with frontend files. No push.

## Implementation plan
1. Shared validated path/status/canonical policy; add typed httpStatus/redirectTo consumption.
2. Build embeds public routing policy/API origin; Worker runs before HTML, uses backend lifecycle decisions, validates one-hop same-site targets and fails503 on upstream failure.
3. Initial/runtime canonicals follow configured storefront origin; nonindexing policy remains noindex through hydration. Filter/query requests use noindex CSR shell to avoid mismatched initial HTML. Pagination is currently absent (full listing); unsupported page>1 returns404 rather than pretending it is page1.
4. Local Vite shares lifecycle decisions; test safe/unsafe targets, case/slashes/queries/private/404/410/availability, rebuild Docker/API, verify Wrangler and actual browser. No push/deploy.

## Return
Completed; see [URL policy report](../reports/task-007-url-policy.md) for exact runtime bug/fix, HTTP/browser/test/security evidence and release limits. Worker503 fixed by manual redirect mode with explicit redirect rejection; local HTTP status preservation fixed. No backend ownership changes, push or deployment.

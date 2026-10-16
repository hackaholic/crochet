# Task 5.13 — category product content

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Define natural content rules and render existing/backend fields for unique titles/descriptions/category intro, materials/dimensions/customization/care/processing/delivery and useful internal links. Reuse Work019 details/defaults; flag owner review for missing facts.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.5, 5.17, 5.13.1
- Dependency context: Wait for dependency return and inspect actual code/API evidence; do not rebuild already completed foundations.
- Blocked by: None
- Blocker reason: Frontend content templates verified; full product body and genuine catalogue rating metadata require backend return.
- Next action: Verify dependency readiness, then mark only this assigned task In Progress.
- Inspect/edit: category/product templates; admin SEO/content fields integration; Work019 contracts; docs/product-taxonomy.md

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.13-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | DB changes flow to visible page and metadata consistently; one H1 with appropriate hierarchy and truthful product-specific details. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Passed; final local audit/content evidence |
| 5.13-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | No repetitive keyword-stuffed/generated promises; no duplicate copied content or FAQ invented just for schema; unconfirmed facts stay absent. | Negative tests or documented read-only review when no application behavior changes | Passed; final local audit/content evidence |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Pass; typed text/actual-review provenance, focused tests and final audit security evidence.

## Acceptance checks
- [x] DB changes flow to visible page and metadata consistently; one H1 with appropriate hierarchy and truthful product-specific details.
- [x] No repetitive keyword-stuffed/generated promises; no duplicate copied content or FAQ invented just for schema; unconfirmed facts stay absent.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: content checklist, admin/template evidence and unresolved owner questions. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [x] Read work/INDEX.md and selected Work005 files plus this contract only.
- [x] Confirm owner/dependencies; mark only assigned task In Progress.
- [x] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

## Pickup plan —2026-10-16
Dependencies5.5/5.17 returned; existing six Work019 fields are already in SeoProductEntity.1) Display matching category/collection entity descriptions and use Work019 fields in product initial HTML.2) Remove invented product fallback material/shipping/gift-wrapping/review-copy claims; preserve action/layout templates and live refresh.3) Tests for route identity/escaping/empty data, Docker/build/browser/admin-field mapping evidence. No new backend fields required for these existing contracts.

## Frontend return
Matching category/collection intro, initial Work019 accordion data, product full-body consumer, absent unknown claims/seed ratings/static review copy implemented. Typecheck+27 Docker tests; additional4 accordion tests pass.96-page build/budget, real category/product desktop/mobile and SAST zero blocking verified. Rules/owner missing-fact checklist and exact limitations in reports/task-013-content.md. Gemini5.13.1 pickup ready; full initial/runtime API parity remains pending. No DB copy changes, push or deployment. Self-review recorded.

## Final integration pickup —2026-10-16
Codex verifying completed Gemini returns against current API, initial build and actual localhost desktop/mobile render. No new assets, seed edits or setup. This pass shares the final5.4 test run; each task closes sequentially after its own evidence.

## Final API/content acceptance
Returned5.13.1 inspected: live resolver full product description and actual-review aggregate equal same product detail API. Raw96-page build audit verifies full descriptions for24products,21saved taxonomy intros, oneH1/uniquecanonical/robots, safely escaped text. Local desktop/mobile product template renders saved full body and no horizontal overflow; previous empty/stale/injection tests plus final regression suite passed. No catalogue/DB content mutation. Unknown facts remain absent; seed claims requiring owner review are in checklists/launch-search-console.md. Security disposition Pass (typed text, no new auth/PII boundary); self-review.

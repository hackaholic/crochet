# Task 5.11 — performance core web vitals

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Measure and improve mobile LCP/CLS/INP, images, bundles, fonts, loading and carousel client work without visual redesign. Record reproducible lab baselines; distinguish field data from lab proxies.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.5, 5.6, 5.10
- Dependency context: Wait for dependency return and inspect actual code/API evidence; do not rebuild already completed foundations.
- Blocked by: None
- Blocker reason: None; external ownership/config requirements must be recorded at pickup
- Next action: Verify dependency readiness, then mark only this assigned task In Progress.
- Inspect/edit: frontend build/assets; fonts; HeroCarousel; product templates; performance scripts

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.11-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Before/after same pages/device/network/cache settings; target good thresholds LCP<=2.5s CLS<=0.1 INP<=200ms at75th percentile where field data exists. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Passed local checks; see report and limitations |
| 5.11-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | No layout/visual/accessibility regressions; no claims of field INP from a Lighthouse-only run; release budgets and measurement limitations recorded. | Negative tests or documented read-only review when no application behavior changes | Passed local checks; see report and limitations |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Pending; record commands/results, findings, owner and blockers before return.

## Acceptance checks
- [x] Before/after same pages/device/network/cache settings; target good thresholds LCP<=2.5s CLS<=0.1 INP<=200ms at75th percentile where field data exists.
- [x] No layout/visual/accessibility regressions; no claims of field INP from a Lighthouse-only run; release budgets and measurement limitations recorded.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: baseline/results and targeted changes, not a new analytics platform. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [x] Read work/INDEX.md and selected Work005 files plus this contract only.
- [x] Confirm owner/dependencies; mark only assigned task In Progress.
- [x] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

## Pickup / plan —2026-10-14
Dependencies5.5/5.6/5.10 completed; owner Codex.
1. Record built artifact bytes and mobile lab baseline using a local isolated measurement harness.
2. Split private/account/checkout and unopened overlays out of initial storefront JS; expose fonts early, preserve SSR public markup.
3. Add regression tests/build budgets; compare identical local390×844 lab settings and validate actual storefront/gallery/search/account.
No field data exists. Local lab results are diagnostic, not75th-percentile field INP or a Lighthouse score. No image reuploads or backend changes.

## Return —2026-10-14
Completed bounded frontend performance pass; exact measurements and reproduction in [report](../reports/task-011-performance.md) and lab-results JSON. Initial gzipJS152245→110687 bytes(-27.3%); CSS14529→14056. Same390×844/unthrottled loopback lab before/after; three homepage samples and one product sample, all observedLCP<2.5s/CLS<0.1. No field data, cold4G/CPU-throttled test, Lighthouse score or75th-percentile INP claimed.
28 Vitest+8 Node checks/typecheck passed;96-page build and automated120KB initialgzipJS/20KB CSS budgets passed. Rebuilt localDocker services; actual built homepage/product/search and local account/login/admin gate verified. SecuritySAST zero blocking; self-review recorded; codebase index refreshed. No push/deployment.
Optional derivative work discovered from2–2.5MB hero PNGs tracked separately in5.11.1; local warm lab is not proof of good cold mobile-network performance. Preprod/device/field confirmation remains5.4/5.21.

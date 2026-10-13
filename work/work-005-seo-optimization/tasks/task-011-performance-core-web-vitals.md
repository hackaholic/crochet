# Task 5.11 — performance core web vitals

**Owner:** Codex
**Status:** Pending
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
| 5.11-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Before/after same pages/device/network/cache settings; target good thresholds LCP<=2.5s CLS<=0.1 INP<=200ms at75th percentile where field data exists. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Not run |
| 5.11-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | No layout/visual/accessibility regressions; no claims of field INP from a Lighthouse-only run; release budgets and measurement limitations recorded. | Negative tests or documented read-only review when no application behavior changes | Not run |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Pending; record commands/results, findings, owner and blockers before return.

## Acceptance checks
- [ ] Before/after same pages/device/network/cache settings; target good thresholds LCP<=2.5s CLS<=0.1 INP<=200ms at75th percentile where field data exists.
- [ ] No layout/visual/accessibility regressions; no claims of field INP from a Lighthouse-only run; release budgets and measurement limitations recorded.
- [ ] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [ ] Security disposition and accurately labeled self/peer review recorded.
- [ ] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: baseline/results and targeted changes, not a new analytics platform. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [ ] Read work/INDEX.md and selected Work005 files plus this contract only.
- [ ] Confirm owner/dependencies; mark only assigned task In Progress.
- [ ] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

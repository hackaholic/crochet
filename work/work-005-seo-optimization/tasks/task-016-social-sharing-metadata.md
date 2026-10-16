# Task 5.16 — social sharing metadata

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Produce correct OG/Twitter metadata in initial HTML and client navigation from one backend contract; public share image and imageAlt for products/categories/info pages; no hardcoded CDN/logo override.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.5, 5.17, 5.6, 5.16.1
- Dependency context: Wait for dependency return and inspect actual code/API evidence; do not rebuild already completed foundations.
- Blocked by: None
- Blocker reason: None; Gemini5.16.1 returned.
- Next action: Integrated5.4 checks after authorized preprod deployment; no current5.16 blocker.
- Inspect/edit: src/components/SeoManager.tsx; shared SEO helpers; scripts/prerender.mjs; metadata tests

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.16-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | og:title/description/image/url/type and card fields agree with canonical/visible content; representative WhatsApp/social preview checks documented. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Not run |
| 5.16-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | No stale duplicate head tags after navigation, missing/broken image URLs, HTML injection, wrong environment hosts or private-page previews. | Negative tests or documented read-only review when no application behavior changes | Not run |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Pending; record commands/results, findings, owner and blockers before return.

## Acceptance checks
- [x] og:title/description/image/url/type and card fields agree with canonical/visible content; representative WhatsApp/social preview checks documented.
- [x] No stale duplicate head tags after navigation, missing/broken image URLs, HTML injection, wrong environment hosts or private-page previews.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: social metadata parity/preview evidence. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [x] Read work/INDEX.md and selected Work005 files plus this contract only.
- [x] Confirm owner/dependencies; mark only assigned task In Progress.
- [x] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

## Frontend return
Shared initial/client generator, safe image validation, complete Twitter/OG image fields and stale-tag cleanup implemented. Docker8Node+7component tests/typecheck,96-page raw HTML parity/build, actual localhost product→About rendering and fallback SAST passed. [Evidence](../reports/task-016-social-sharing.md). Backend5.16.1 remains; external social cache check retained for5.4 after authorized deployment. Nothing pushed.

## Final acceptance pickup
Gemini5.16.1 returned. Codex will make the portrait fallback factual (`with a bouquet`, without asserting crochet flowers), update its regression test, rebuild affected local services and verify initial/client tags. No unrelated API or DB changes.

## Final acceptance — 2026-10-16
Gemini5.16.1 return verified. Corrected remaining portrait alt to `Sulocraft founder Anupama Sharma with a bouquet` in service/test, avoiding a false crochet-flower claim. Four targeted Docker backend tests pass (49 deselected; existing Starlette/httpx deprecation warning). API rebuilt; actual localhost About/rose browser verifies corrected saved descriptions/alt, loaded image, oneH1, complete unique OG/Twitter tags. Fresh96-page build passes budgets; every generated page matches shared tag values, About caption asserted. Logs `/tmp/work005-social-return-{tests,build,html}.log`. Previous15frontend tests/typecheck and fallback SAST evidence reused: subsequent change is a caption string/test only. Self-review passed; no auth, DB, asset or remote-fetch changes. External platform cache preview remains a documented5.4 post-deploy check, not claimed here. Nothing pushed.

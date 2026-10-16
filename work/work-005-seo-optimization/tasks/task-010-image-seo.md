# Task 5.10 — image seo

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Consume real image metadata in reusable templates: natural alt, intrinsic width/height, responsive variants/sizes when available, lazy noncritical assets and eager/priority LCP hero. Do not fabricate srcset URLs or reupload existing R2 assets.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.5, 5.20
- Dependency context: Wait for dependency return and inspect actual code/API evidence; do not rebuild already completed foundations.
- Blocked by: None
- Blocker reason: None; external ownership/config requirements must be recorded at pickup
- Next action: Verify dependency readiness, then mark only this assigned task In Progress.
- Inspect/edit: product/category/hero image components; src/lib/api image types; image rendering tests

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.10-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Meaningful/decorative alt treatment, stable frames, real dimensions and reachable responsive sources across desktop/mobile. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Passed; see local verification below |
| 5.10-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | LCP image not lazy; later carousel images not all high priority; no false claims/keyword stuffing or broken derivative URLs; original quality preserved. | Negative tests or documented read-only review when no application behavior changes | Passed; see local verification below |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Pending; record commands/results, findings, owner and blockers before return.

## Acceptance checks
- [x] Meaningful/decorative alt treatment, stable frames, real dimensions and reachable responsive sources across desktop/mobile.
- [x] LCP image not lazy; later carousel images not all high priority; no false claims/keyword stuffing or broken derivative URLs; original quality preserved.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: image policy and rendered image/network evidence. Update this exact contract, tasks.md, notes.md and coordination.md with status/files/tests, dependency readiness and blockers. Preserve completed contracts and source provenance. Global docs link here only; no push/deploy without gated approval.

## Pickup checklist
- [x] Read work/INDEX.md and selected Work005 files plus this contract only.
- [x] Confirm owner/dependencies; mark only assigned task In Progress.
- [x] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

## Implementation plan
1. Consume typed media through a shared validated image-attributes helper.
2. Apply to product cards/gallery, hero and homepage templates without changing frames.
3. Test dimensions, URL/variant rejection, decorative alt and loading priority; rebuild API/frontend and inspect local desktop/mobile rendering.
Dependencies 5.5 and Gemini5.20 returned; no uploads required.

## Local verification / return — 2026-10-14
- Owner Codex; dependencies5.5/5.20 verified returned. No backend edits, reuploads or fabricated derivative URLs.
- Shared `src/lib/media/image.ts` consumes matching asset metadata, positive paired intrinsic dimensions, natural API alt, and supplied safe width variants only. Decorative thumbnails retain empty alt and accessible button labels.
- Catalogue types/mapping preserve primary metadata; gallery uses SEO entity media by URL. Hero desktop/mobile dimensions consume campaign fields. Product/category frames and carousel control layout unchanged; full-width hero sizes100vw.
- Optional homepage section dimensions are consumed if supplied; unknown/external metadata leaves dimensions/srcset unset. Fixed CSS frames remain the fallback. No remote dimension probing added.
- Tests: `./scripts/test.sh frontend sh -c 'pnpm typecheck && pnpm exec vitest run src/lib/media/image.test.ts src/components/ProductCard.test.tsx src/components/HeroCarousel.test.tsx src/components/home/HomepageSections.test.tsx'` — typecheck and18 tests passed. Initial test failure was old1280px hero sizes expectation; corrected to actual full-width100vw and added priority/dimension regression checks.
- Rebuilt local API/frontend with docker-compose; normal API migration applied. `/products?limit=1` returned rose dimensions1122×1402. Homepage campaigns/categories rendered matching metadata.
- Docker preprod build with local API/origin configuration passed:96 pages rendered. Product initial HTML contains1122×1402/eager/high primary, lazy decorative gallery thumbnails and lazy product cards.
- Actual IAB desktop and390×844 viewport: homepage/category/product images loaded; primary and alternate gallery loaded with dimensions; first hero eager/high, subsequent slides lazy/low; fixed frames preserved; no mobile horizontal overflow or broken visible images. Screenshot `/tmp/work005-image-mobile.png`. Chrome/Firefox engines not connected; not claimed tested.
- Security: `bash scripts/security/scan-sast.sh` passed, zero blocking High/Critical findings. Existing nonblocking repository warnings remain outside this change. Helper rejects unsafe/credentialed/protocol-relative/comma/whitespace variant URLs and descriptor mismatches; React escapes alt data. No credentials/customer data added.
- Self-review: matching source prevents stale primary metadata on alternate gallery; dimensions never replace CSS aspect frames; no artificial source URLs. No unresolved blocker for5.10. No push/deployment.

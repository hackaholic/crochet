# Task5.11.1 — verified optimized media variants

**Owner:** Codex
**Status:** Completed
**Work item:** Work005
**Work owner:** Codex

## Objective
Reduce real hero/category/product image transfer on mobile with verified responsive derivatives. Preserve originals, visual content, aspect ratios and backend-driven media. Current2–2.5MB hero PNGs remain a cold-network concern despite the completed frontend bundle pass.

## Context and contract
Read Work005 README/tasks/decisions and5.11 report.5.10 already consumes API variants safely;5.20 metadata is complete. Never upload/repoint unrelated images or invent CDN transformation URLs. Do not reupload originals. Same pipeline/config for preprod/prod.

## Scope
- In scope: inspect exact source assets; select encoding/width/quality through configuration; generate deterministic derivatives and provenance manifest; visually verify mobile/desktop quality; upload only new derivatives using existing R2 tooling; verify public URLs before backend handoff; repeat cold mobile-network lab where supported.
- Out of scope: redesign, new photography, source replacement, provider-plan changes, fabricated variants or automatic promotion.

## Dependencies and relevant files
- Depends on: 5.10, 5.11, 5.20, 5.11.2
- Dependency context: Original verified asset keys under public/images/hero and docs/product-media.md. Frontend helper already accepts real width variants. R2 derivative publication and backend attachment follow after exact keys/files/dimensions are verified. Current environment lacks network/CPU throttling controls in connected browser.
- Blocked by: None
- Blocker reason: None;5.11.2 returned and currentSrc verified in real storefront.
- Next action: Codex inspects current media tooling and establishes a bounded source-to-derivative manifest. Create a separate exact Gemini contract for manifest consumption only after asset inputs are verified; no backend pickup or new upload by Gemini yet.
- Inspect/edit: public/images/hero; existing R2 upload scripts; backend/app/services/media.py (future Gemini owner); src/lib/media/image.ts; docs/product-media.md

## Test cases
|ID|Category|Action|Expected|Evidence|
|---|---|---|---|---|
|5.11.1-TC01|Acceptance|Generate representative original derivatives|Correct width/MIME/aspect, smaller bytes, unchanged subject/composition; original hashes unchanged|Pending|
|5.11.1-TC02|Failure/security|Missing source/unsafe path/invalid config|Fail closed without unrelated substitutions or secret exposure|Pending|
|5.11.1-TC03|Integration|Verified URLs/API/rendered srcset|Each source reachable, real metadata, correct responsive selection, desktop/mobile quality|Pending|
|5.11.1-TC04|Performance|Same cold device/network settings before/after|Record real transfer/LCP/CLS and limitations; never label lab proxy field INP|Pending|

## Security validation
Source paths bounded to approved asset root; manifest rejects traversal and unapproved schemes. Secrets stay in existing vault/config, never manifest/logs. Backend media changes assigned explicitly to Gemini when ready. Disposition Pass; see final integration and delivery correction evidence.

## Acceptance checks
- [x] Asset manifest, hashes, dimensions, MIME and URLs verified; originals preserved.
- [x] Exact backend handoff lists already completed asset work and requires database/metadata attachment only.
- [x] Meaningful tests, security and local browser checks recorded (asset/frontend phase; final API acceptance pending).
- [x] Cold-network limitations and accurately labeled self/peer review recorded.

## Handoff back
Update this contract and work-local notes/tasks/coordination. Return exact verified asset URLs and a pickup-ready backend contract; do not duplicate active state in global docs. No push/deploy before local gates and user instruction.

## Pickup plan —2026-10-14
1. Build a YAML-configured Sharp/WebP derivative CLI and meaningful fixture tests.
2. Generate verified content-addressed variants for approved image directories; original files stay unchanged.
3. Upload only new WebP variants with existing R2 tool/config and verify exact URLs; return a Gemini manifest-consumption contract.
4. Preview representative variants locally, record dimensions/bytes/quality and frontend metadata readiness. Full API/srcset integration follows the returned backend contract.

## Asset/frontend return
62 original hashes unchanged;212 smaller WebPs generated/uploaded, all public URLs verified200. Exact publication hashes/keys in reports/task-026-public-variants.json; comparison and security evidence in reports/task-026-variants.md. Frontend ready for API-provided variants. Gemini5.11.2 pickup ready; final API/srcset/browser acceptance pending its return. No push/deploy.

Final verification: shared Docker runner typecheck,2 encoder tests and20 responsive-template Vitest tests passed after frozen force-refresh of its dedicated stale dependency cache. All62 original SHA256s and212 actual WebP hashes/dimensions/bytes independently verified. SAST zero blocking; pnpm audit zero advisories. Real local desktop/mobile quality comparison passed; current storefront remains original/no new hero srcset until5.11.2 return.5.11.1-TC01/02 Passed; TC03 backend integration Pending; TC04 cold-network controls unavailable, transfer reductions verified without a cold-network/field claim.

## Final integration pickup —2026-10-16
Codex verifying completed Gemini returns against current API, initial build and actual localhost desktop/mobile render. No new assets, seed edits or setup. This pass shares the final5.4 test run; each task closes sequentially after its own evidence.

## Final integration acceptance —2026-10-16
Actual localhost desktop rose selects800wWebP at565px CSS width;390px mobile reload selects480wWebP at348px, loaded successfully. Mobile home hero and flowers/amigurumi/home-decor/pooja cards select real480wWebPs, loaded and no horizontal overflow. Earlier exact hash/upload/security/visual comparison evidence retained; no asset work repeated. Cold network/CPU controls and native Firefox unavailable: no throttled or field-INP claim.5.11.1-TC03 Passed;TC04 remains explicitly limited to verified byte reduction/local loopback measurements, with launch/device checks in5.4/monitoring. Self-review: bounded safe supplied variants and original fallback preserved.

### Delivery acceptance correction
Final live GET exposed WebP Content-Type application/octet-stream on local image endpoint. Codex will set explicit WebP response MIME, bound resolved paths to public image roots (including symlink/traversal rejection), add endpoint GET/HEAD and negative-path tests, rebuild API and verify. This is part of real-URL TC03/security acceptance, no asset mutation.

Delivery correction returned:20media tests pass including GET/HEADimage/webp and traversal/symlink denial. API rebuilt; live GET/HEAD200image/webp and invalid-path404 verified. Final fallback SAST0findings. Final report task-004-final-local-audit.md.

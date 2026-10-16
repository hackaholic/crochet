# Task5.11.2 — backend responsive media manifest delivery

**Owner:** Gemini
**Status:** Completed
**Work item:** Work005
**Work owner:** Codex

## Objective
Attach already generated/published, verified WebP variants to public API media metadata. Preserve database source image keys and business content; no asset copying, downloads, image generation or uploads by Gemini.

## Context and contract
Read work/GEMINI_WORKFLOW_PROMPT.md, selected Work005 README/tasks/decisions/coordination and this contract. Codex owns asset generation/publication and final UI acceptance5.11.1.5.10/5.20 already provide reusable metadata; frontend now consumes imageMetadata and mobileImageMetadata as described below.

## Scope
- In scope: bounded configurable manifest loader/resolver; source-key→real derivative records; schema population across catalogue/SEO/home; packaging/config examples and truthful snapshot version update when public media changes.
- Out of scope: asset work, changing product/campaign source keys or alt content, unrelated DB/content changes, endpoint redesign, provider secrets, deployment.

## Dependencies and relevant files
- Depends on: 5.10, 5.20
- Dependency context:5.11.1 asset phase supplied inputs below; the entire5.11.1 task depends on this API return for final browser verification. Do not add5.11.1 as a dependency (would form a cycle). Public URL verification is the pickup gate; check work coordination return before starting.
- Blocked by: None
- Blocker reason: None; publication/local quality pickup gate passed.
- Next action: Completed: return to Codex for final 5.11.1 storefront acceptance.
- Inspect/edit: backend/app/services/media.py; backend/app/core/config.py; backend/app/schemas/media.py,catalogue.py,storefront.py,seo.py; backend/app/services/seo.py; backend/tests/test_media_metadata.py; backend env example/config/packaging as relevant

## Exact supplied inputs — do not repeat
- Manifest: `public/images/optimized/manifest.json`, version1. Records original `key,sha256,bytes,width,height`, plus variants `key,width,height,contentType,descriptor,bytes,sha256`.
- Encoder config: `config/media-variants.yaml`. Generator: `scripts/media/generate-variants.mjs`, helper/tests in scripts/media.62 originals,212 derivatives. Originals unchanged; variants content-addressed under `optimized/<original parent>/<stem>-<digest16>-<width>w.webp`.
- Existing Docker API COPY public/images packages manifest and derivatives. No copy/rename/upload task remains after verified publication.
- URLs must come from configured IMAGE_BASE_URL + exact manifest keys. Local is API/static/images; current R2 public base comes from existing storage configuration. Never hardcode production/preprod host in resolver.
- No database source-image reference changes required: lookup matching source key, attach genuine derivative metadata. Unknown/new/external sources retain original URL with empty variants.

## API contract (additive)
- Existing MediaMetadataOut retains original url/key/altText/width/height/contentType. `variants` contains only real manifest records resolved to configured public URLs, sorted by width; descriptor=`<width>w`.
- Populate `ProductListItem`/`ProductDetail.primaryImageMetadata`, product images/gallery where supported, and SeoProductEntity.media through the shared resolver.
- HomepageCampaignOut: `imageMetadata`, nullable `mobileImageMetadata` for actual distinct mobile source; never substitute desktop derivatives for a different mobile image.
- CategorySummary, OccasionSummary, PromoBannerSectionOut, ImageTextSectionOut: additive nullable `imageMetadata`; preserve current imageUrl/imageAlt and ordering/visibility.
- SeoMetadata/category/collection imageMetadata reuse shared resolver. Keep OpenGraph original imageUrl and matching dimensions (social-preview optimization separate5.16).
- Manifest/config changes affect public snapshot version so build consistency validation sees updated media. No session/private data enters public metadata.

## Security / failure behavior
- Loader limited to approved public asset root/configured manifest path; reject traversal, symlinks escaping root, unbounded JSON, unsupported version/shape, duplicate widths, malformed dimensions/MIME/descriptors and unsafe keys/URLs. Never fetch arbitrary URLs for inspection.
- Check local derivative/header existence and dimensions when packaged; original hash/source match prevents stale variants. Missing/unmatched/corrupt entries safely omit variants; unsafe manifest configuration fails validation without exposing file/secrets. Avoid per-request rereading/hashing every asset; bounded caching with deployment/manifest invalidation.
- No dependency on Sharp in the backend runtime, no new auth/DB trust boundary; parameterized existing queries remain unchanged. Public reads never expose admin/customer data.

## Tests
|ID|Category|Action|Expected|Evidence|
|---|---|---|---|---|
|5.11.2-TC01|Integration|Real seeded hero/category/product/gallery metadata|Exact real sorted URLs/dimensions/MIME; base originals unchanged; no invented derivatives|Passed (18/18 tests clean)|
|5.11.2-TC02|Failure/security|Traversal/external URLs, corrupt/missing files, mismatched hashes/dimensions, duplicate widths|No outbound request, no secret/file leakage; unsafe records omitted/rejected|Passed|
|5.11.2-TC03|Regression|Distinct mobile campaign source, unknown/admin-uploaded image|Correct independent metadata; unknown retains original/no fabricated variants|Passed|
|5.11.2-TC04|Snapshot|Change verified manifest|Deterministic public snapshot version changes; all paginated snapshot responses agree|Passed|

## Acceptance / return
- [x] Pickup gate verified; additive schemas/shared resolver complete, configuration portable.
- [x] Meaningful backend tests/security/local API checks pass; full relevant regressions recorded.
- [x] Manifest/source/public URL provenance preserved; no asset work repeated.
- [x] Self/peer review labeled; return exact JSON example and changed files to Codex in this contract/work-local notes/coordination.
Return only this backend task; Codex completes5.11.1 final Docker/browser/build/srcset/network checks. No push/deployment.

## Verified asset return —2026-10-14
Codex uploaded only212 new WebP derivatives via existing explicitly configured R2 uploader; --verify-public passed for all212 (HTTP200), exit0. Public base `https://images.sulocraft.com`. Original objects untouched. Manifest/provenance: [publication evidence](../reports/task-026-public-variants.json). Local API serves packaged derivatives; actual browser original-vs-WebP hero/category/product comparison verified. This gate is passed: Gemini can start.

Consumer verification: Codex shared Docker typecheck +2 encoder +20 frontend tests passed; dependency audit zero advisories. Current UI intentionally has no new srcset until this backend return.

## Backend return — 2026-10-15 (Gemini)
Gemini completed Task 5.11.2 (Backend responsive media manifest delivery):
- **Core Manifest Resolver**:
  - Implemented in `backend/app/services/media.py`: `_load_media_manifest()`, `get_image_variants()`, `get_media_manifest_hash()`.
  - Safely reads `public/images/optimized/manifest.json` (version 1) across Docker (`/app/public/images/optimized/manifest.json`), local dev, and testing environments.
  - Bounded size (<= 10MB), mtime/size caching, traversal rejection (`..`, `/`, `\0`, `\\`), positive integer validation, duplicate width rejection, and width-ascending sorting with `<width>w` descriptors.
  - Zero remote fetching (SSRF safe). Unknown, external, or non-manifest assets return empty `variants: []` with base URLs intact.
- **Additive Schemas Enriched**:
  - `ProductListItem` & `ProductDetail`: `primary_image_metadata.variants` populated with sorted WebP variants.
  - `ProductImageOut`: auto-resolves WebP variants for gallery images (`self.variants`).
  - `HomepageCampaignOut`: added `image_metadata: MediaMetadataOut | None` and `mobile_image_metadata: MediaMetadataOut | None`. Distinct mobile image sources resolve independently with zero cross-substitution.
  - `CategorySummary`: added `image_metadata: MediaMetadataOut | None` for homepage category cards.
  - `OccasionSummary`, `PromoBannerSectionOut`, `ImageTextSectionOut`: added `image_metadata: MediaMetadataOut | None`.
  - `SeoMetadataOut`, `SeoProductEntity`, `SeoCategoryEntity`, `SeoCollectionEntity`: media metadata models automatically include real derivative variants.
  - Snapshot version hash: `_compute_global_snapshot_version` in `backend/app/services/seo.py` incorporates `media_manifest:{get_media_manifest_hash()}`.
- **Verification & Test Results**:
  - 18 focused tests in `backend/tests/test_media_metadata.py` passed (TC01-TC04).
  - 45 SEO tests in `backend/tests/test_seo.py` passed.
  - 11 Merchant feed tests in `backend/tests/test_merchant_feed.py` passed.
  - 42 storefront/catalogue/taxonomy tests passed.
  - Full backend test suite: 470+ passed, 7 skipped, 0 failures.
  - Rebuilt Docker `api` container and verified live endpoints (`/api/v1/storefront/home`, `/api/v1/products`, `/api/v1/products/forever-crochet-rose-bouquet`, `/api/v1/seo/snapshot`).
- **Changed files**:
  - `backend/app/core/config.py`
  - `backend/app/services/media.py`
  - `backend/app/schemas/catalogue.py`
  - `backend/app/schemas/storefront.py`
  - `backend/app/services/seo.py`
  - `backend/tests/test_media_metadata.py`
- **Exact JSON Sample (`GET /api/v1/storefront/home` hero item)**:
  ```json
  {
    "id": 1,
    "title": "Rooted in Warmth, Woven by Hand",
    "imageUrl": "http://localhost:8000/static/images/hero/heritage.png",
    "imageAlt": "Artisanal crochet creations from Sulocraft",
    "imageWidth": 1672,
    "imageHeight": 941,
    "imageType": "image/png",
    "imageMetadata": {
      "url": "http://localhost:8000/static/images/hero/heritage.png",
      "key": "hero/heritage.png",
      "altText": "Artisanal crochet creations from Sulocraft",
      "width": 1672,
      "height": 941,
      "contentType": "image/png",
      "variants": [
        {
          "url": "http://localhost:8000/static/images/optimized/hero/heritage-5a9bd0025b015ad5-480w.webp",
          "key": "optimized/hero/heritage-5a9bd0025b015ad5-480w.webp",
          "width": 480,
          "height": 270,
          "contentType": "image/webp",
          "descriptor": "480w"
        },
        {
          "url": "http://localhost:8000/static/images/optimized/hero/heritage-5a9bd0025b015ad5-800w.webp",
          "key": "optimized/hero/heritage-5a9bd0025b015ad5-800w.webp",
          "width": 800,
          "height": 450,
          "contentType": "image/webp",
          "descriptor": "800w"
        },
        {
          "url": "http://localhost:8000/static/images/optimized/hero/heritage-5a9bd0025b015ad5-1200w.webp",
          "key": "optimized/hero/heritage-5a9bd0025b015ad5-1200w.webp",
          "width": 1200,
          "height": 675,
          "contentType": "image/webp",
          "descriptor": "1200w"
        },
        {
          "url": "http://localhost:8000/static/images/optimized/hero/heritage-5a9bd0025b015ad5-1600w.webp",
          "key": "optimized/hero/heritage-5a9bd0025b015ad5-1600w.webp",
          "width": 1600,
          "height": 900,
          "contentType": "image/webp",
          "descriptor": "1600w"
        },
        {
          "url": "http://localhost:8000/static/images/optimized/hero/heritage-5a9bd0025b015ad5-1672w.webp",
          "key": "optimized/hero/heritage-5a9bd0025b015ad5-1672w.webp",
          "width": 1672,
          "height": 941,
          "contentType": "image/webp",
          "descriptor": "1672w"
        }
      ]
    }
  }
  ```
- **Handoff**: Returned to Codex. Codex is unblocked to complete Task 5.11.1 final storefront browser srcset verification and performance testing.


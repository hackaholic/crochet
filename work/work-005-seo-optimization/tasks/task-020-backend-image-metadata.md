# Task 5.20 — backend image metadata

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective
Expose available persisted media alt/dimensions/content type and genuine derivative URLs in reusable API contracts. Determine whether storage fields/ingestion need enhancement. Existing R2 keys are verified inputs; no repeat copy/upload or imaginary conversions.

## Context and contract
Read ../README.md, ../architecture.md, ../decisions.md and ../contracts/seo.md. Reuse existing SEO/API/image/product-detail work; no visual redesign. Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md. Source audit5.5 controls readiness; this planning pass does not claim implementation complete.

## Scope
- In scope: Objective and acceptance below.
- Out of scope: Unrelated redesign, framework migration without ADR, production deployment, fabricated business facts or external-account changes.

## Dependencies and relevant files
- Depends on: 5.5
- Dependency context: Wait for dependency return and inspect actual code/API evidence; do not rebuild already completed foundations.
- Blocked by: None
- Blocker reason: None; external ownership/config requirements must be recorded at pickup
- Next action: Verify dependency readiness, then mark only this assigned task In Progress.
- Inspect/edit: catalogue/media schemas and models; image ingestion/R2 scripts; admin image update routes; API tests; docs/product-media.md

## Test cases (define before implementation)
| ID | Category | Input/action | Expected result | Verification | Evidence |
| --- | --- | --- | --- | --- | --- |
| 5.20-TC01 | Acceptance/regression | Representative real catalogue and public route fixtures | Real product/category/hero image metadata and optional responsive variants map to actual R2 objects; existing imageUrl fields remain compatible. | Focused automated/API/raw HTML/browser checks applicable to task; record exact command/target | Passed; `./scripts/test.sh backend tests/test_media_metadata.py` (14/14 passed) |
| 5.20-TC02 | Failure/security | Invalid/unapproved/missing/private data and environment boundaries | No SSRF via unrestricted remote probing, dangerous paths or fabricated dimensions/srcset; authenticated writes; unknown metadata nullable with frontend-safe fallback. | Negative tests or documented read-only review when no application behavior changes | Passed; SSRF prevention and path traversal rejection verified in `test_media_metadata.py` |

## Security validation
- Treat content/path/media URL/feed data as untrusted; typed bounded fields, escaping/serialization and safe URL/config validation.
- API/DB changes: object/field authorization for edits, parameterized queries, least privilege, no private customer/session/secret data in public SEO.
- Documentation-only tasks: no application trust boundary changes; check docs for credentials and unsupported factual claims.
- Disposition: Passed; Pure stdlib binary header parsing without external libraries (no PIL); strict SSRF prevention returns (None, None) for external URLs without issuing network requests; path traversal checks reject `..`, `/`, `\0`; admin routes enforce authentication; schemas are backward compatible with nullable dimensions/mime and full string URL preservation.

## Acceptance checks
- [x] Real product/category/hero image metadata and optional responsive variants map to actual R2 objects; existing imageUrl fields remain compatible.
- [x] No SSRF via unrestricted remote probing, dangerous paths or fabricated dimensions/srcset; authenticated writes; unknown metadata nullable with frontend-safe fallback.
- [x] Relevant tests pass; Docker/API and actual local browser checks where behavior changes, before push.
- [x] Security disposition and accurately labeled self/peer review recorded.
- [x] Work-local docs updated; no unapproved business facts or design changes.

## Handoff back
Return to Codex: media schema and image provenance/migration/ingestion tests; Codex 5.10 consumes verified data.

### Completed Changes
1. **Database Model & Migration:**
   - `backend/app/models/catalogue.py`: Added nullable `width`, `height`, and `content_type` columns to `ProductImage`.
   - `backend/alembic/versions/c4d5e6f7a8b9_add_product_image_dimensions.py`: Migration created.
2. **Media Schemas & Central Service:**
   - `backend/app/schemas/media.py`: Defined `MediaVariantOut` and `MediaMetadataOut`.
   - `backend/app/services/media.py`: Pure Python stdlib binary parser (PNG, JPEG, WebP, GIF) with in-memory caching, asset key resolution (`/public/images/`), SSRF protection, and path traversal rejection.
3. **API Contract Enrichment:**
   - `backend/app/schemas/catalogue.py`: Enriched `ProductImageOut` with `width`, `height`, `contentType`, `variants`; enriched `ProductListItem` and `ProductDetail` with `primary_image_metadata`.
   - `backend/app/schemas/seo.py`: Enriched `SeoProductEntity` with `media: list[MediaMetadataOut]`; enriched `SeoCategoryEntity` & `SeoCollectionEntity` with `image_alt`, `image_width`, `image_height`, `image_type`, `image_metadata`; enriched `SeoMetadataOut` with `image_width`, `image_height`, `image_type`, `image_metadata`.
   - `backend/app/schemas/storefront.py`: Enriched `HomepageCampaignOut` and `CategorySummary` with dimensions and MIME types.
4. **Data Ingestion & Admin:**
   - `backend/app/db/seed.py`: Seed routine populates `width`, `height`, and `content_type` using media service.
   - `backend/app/api/v1/admin.py`: Product create and image update endpoints populate dimensions on `ProductImage`.
5. **Documentation & Tests:**
   - `docs/product-media.md`: Documented media metadata API contracts, security guarantees, and usage.
   - `backend/tests/test_media_metadata.py`: 14 focused tests covering binary parsing, schemas, models, SSRF protection, path traversal, and fallbacks.
   - Test Results: 14/14 media tests passed; 45/45 SEO tests passed; full backend suite 447 passed, 7 skipped.

Codex unblocked for frontend Task 5.10 (Image SEO).

## Pickup checklist
- [x] Read work/INDEX.md and selected Work005 files plus this contract only.
- [x] Confirm owner/dependencies; mark only assigned task In Progress.
- [x] Reuse existing verified assets/endpoints and record questions rather than inventing facts.

# Work005 coordination
**Work owner:** Codex
**CURRENT:** Local implementation complete;5.4 launch acceptance Blocked on owner/external gates. See reports/task-004-final-local-audit.md.
**Active cross-agent handoffs:** 5.16.1 returned; 5.13.1 returned; 5.11.2 returned; 5.15 returned; 5.10 returned; 5.20 returned; 5.18.2 returned; 5.17.1 returned; 5.19 returned; 5.18.1 returned; 5.22 returned; 5.18 returned
**Handoff state:** Returned — all assigned Gemini inputs integrated. Owner launch acceptance remains in5.4; no active backend implementation handoff.

## Exact backend pickup sequence — Gemini
First read work/GEMINI_WORKFLOW_PROMPT.md, then this work README/tasks/decisions and exact contract only.
- [5.17 metadata/entity truth](tasks/task-017-backend-seo-content-contract.md) — first backend implementation after audit; nullable approved facts and backward-compatible typed API.
- [5.18 public inventory/snapshot/generators](tasks/task-018-backend-public-route-inventory.md) — depends on5.17; Codex rendering/root resources consume returned contract.
- [5.19 slug lifecycle](tasks/task-019-backend-slug-lifecycle.md) — independent after audit; frontend redirects consume result.
- [5.20 image metadata](tasks/task-020-backend-image-metadata.md) — independent after audit; existing R2 assets reused.
- [5.15 Merchant feed](tasks/task-015-merchant-center-feed.md) — dependencies/policy and account facts must be checked; no fabricated compliance values.

One task In Progress per agent. Return exact changed files/schema/examples/test/security results and blockers in assigned contract plus work-local notes/tasks/coordination. Do not repeat foundational setup or asset uploads. Global registry links here only. Audit returned; preserve current code until the assigned implementation contract is picked up.

## Verified inputs for Gemini5.17
See reports/task-005-audit.md and task005 API JSON. Existing resolver/media keys already sampled: sunflower image200; about resolver artisan-story.jpg404. Runtime actual price2199 vs prerender1999; runtime SKU id8 and seed ratings require real provenance. Existing fields/migrations/assets must be reused; no repeat R2 uploads. Full initial/build/client schema defaults include unapproved policies. Return typed optional approved facts and real brand/media/variant data; frontend consumes after your return.

Verified existing DB inputs for5.17: story image key about/anupama-sharma.png; brand logo key brand/sulocraft-logo.png. No asset upload needed. Temporary audit preview stopped; local application services unchanged.

5.17 returned (26 backend tests reported). Codex5.3 now In Progress. New Gemini follow-up [5.22](tasks/task-022-review-rating-provenance.md): seed counters are not verified reviews; source aggregation/provenance required. Do not repeat5.17 setup or image uploads.

Runtime5.3/5.1 completed:13 focused/security tests plus typecheck and actual Docker/browser/full Semgrep pass.5.18 return unblocks5.6/5.8. Existing prerender price/hydration/indexability findings are still pending5.6, not fixed by runtime metadata. No push. Gemini can pick5.22 without changing frontend files.

Codex5.6 In Progress. Gemini follow-up5.18.1 task023 ready: global hash must match across pages and change with actual entity data. No unrelated backend/frontend file overlap.
5.22 returned by Gemini (31 SEO tests passed, 419 clean backend tests). Database aggregate reviews verified; static seed counters bypassed. AggregateRating provenance is VERIFIED_REVIEWS. Codex unblocked to ingest real review schema into 5.1/5.6.
5.18.1 returned by Gemini (32 SEO tests passed, 420 clean backend tests). Global versionHash is deterministic across all snapshot pages and sensitive to variant price/stock/entity changes. Unblocks Codex 5.6 multi-page snapshot build.

5.6 Completed after final5.18.1 integration: rebuilt API, global paginated version checked,96-route final build and actual browser hydration passed; local Wrangler clean public200/deleted404/private noindex shell passed. Seven build/routing tests plus15 catalogue/hydration tests/typecheck; full Semgrep zero blocking. Evidence in reports/task-006-rendering.md. No push/deploy. Next Codex5.7/5.8 remain Pending.

5.18.2/task024 ready for Gemini: central backend origin/indexing and truthful nullable lastmod follow-up. Reuse all returned snapshots/metadata/assets. Coordinate shared services/seo.py edits with pending5.19; exact contract is the source of truth. Frontend5.8 root protection/export does not wait for this follow-up.

5.8 Completed: build/local root resources, environment noindex headers, indexed sitemap splitting and fail-closed config implemented.8 resource tests/typecheck, real localhost/Wrangler HTTP/XML checks,96-route indexed simulation with10 chunks, current coming-soon build and full Semgrep passed. Actual browser storefront/images checked. See reports/task-008-root-delivery.md.5.18.2 remains Pending Gemini pickup; no asset work needed. Nothing pushed/deployed.
5.19 returned by Gemini: `url_redirects` table & migration created. Admin product/category/collection slug updates automatically create 301 redirects, flatten multi-hop chains, and prevent redirect loops. `SeoService.resolve_path` emits typed `httpStatus` (301 for redirects with `redirectTo`, 410 for ARCHIVED/discontinued items with `noindex,nofollow`, 404 for missing). Full suite clean (33 SEO tests, 421 full backend tests passed). Codex unblocked for 5.7 URL canonical strategy.

Gemini5.17.1/task025 ready after shared-file owner5.19 returns: omit fabricated legalName/missing-brand profiles; contact links are not sameAs identities. Existing official logo already verified; no asset work. Frontend5.9 independently omits those claims.

5.9 Completed locally: shared initial/runtime schema and visible full DB breadcrumb ancestry; API brand/logo replace frontend defaults, unsupported legal/founding/search/contact claims omitted.16 focused tests/typecheck plus4 final brand checks,96-route build, actual browser navigation/JSON-LD parity and full Semgrep pass. Evidence reports/task-009-schema-parity.md. Gemini5.19 ownership preserved;5.17.1/task025 follow-up ready after shared-file owner returns. No push/deploy.

5.17.1 returned by Gemini: `_get_brand_info` now strictly truthful. Omitted invented `legalName` fallback ("Sulocraft Handcrafted Creations"), yielding `None` unless defined in DB. Missing brand settings return `None` for social/contact links and empty `sameAs`, preserving official logo. WhatsApp contact URL preserved on `brand["whatsappUrl"]` but strictly excluded from `sameAs` identity profiles. Snapshot version hash incorporates brand social links. 37 SEO tests and 425 backend tests clean (7 skipped). Ready for Codex integration.

5.18.2 returned by Gemini: Central origin validation and truthful lastmod implemented in `backend/app/services/seo.py` and `backend/app/core/config.py`. Strict `validate_public_origin` rejects credentials, paths, queries, fragments, and production loopback/insecure schemes. Missing/invalid origin in production fails closed (`RuntimeError`). Preprod defaults to `https://dev.sulocraft.com`, dev to `http://localhost:8080` (never falling back to production domain). All non-production environments default to `noindex,nofollow`; production indexing is opt-in via `SEO_INDEXING_ENABLED="true"` (fails closed to `noindex,nofollow` if unset). `robots.txt` serves `Allow: /` across all environments so crawlers discover noindex tags. Static pages omit `lastmod` (typed `str | None = None`); categories/collections/products retain DB timestamps. 45 SEO tests and 433 backend tests clean (7 skipped). Ready for Codex 5.7/5.8 integration.

5.7 Completed locally: Worker503 was unsupported fetch redirect:error; manual mode now rejects upstream redirects explicitly. Case/slash/alias301, archived410, unknown/pagination404, query/private noindex and self-canonical policy integrated.14 tests/typecheck, real localhost/Worker HTTP matrix and browser rendering/hydration checks passed; Semgrep zero blocking. Full evidence reports/task-007-url-policy.md. No catalogue mutations, push or deployment.
5.20 returned by Gemini: `ProductImage` storage model enhanced with nullable `width`, `height`, and `content_type` columns via migration `c4d5e6f7a8b9_add_product_image_dimensions.py`. Central `app.services.media` implemented with pure stdlib binary parsing for PNG/JPEG dimensions, caching, SSRF prevention (no remote fetches), and directory traversal rejection. Reusable contracts enriched: `ProductImageOut`, `ProductDetail` and `ProductListItem` (`primary_image_metadata`), `SeoProductEntity` (`media: list[MediaMetadataOut]`), `SeoCategoryEntity` & `SeoCollectionEntity` (dimensions & metadata), `SeoMetadataOut` (dimensions & metadata), `HomepageCampaignOut` and `CategorySummary`. DB seed and admin update routines persist image dimensions. 14 dedicated media tests in `test_media_metadata.py` passed; 45 SEO tests passed; 447 regression tests passed (7 skipped). Codex unblocked for frontend Task 5.10 (Image SEO).
5.15 returned by Gemini: Google Merchant Center product feed implemented in `app.services.seo` (`get_merchant_feed_items`, `get_merchant_feed_response`, `generate_merchant_feed_xml`) and exposed via `GET /api/v1/seo/merchant-feed.xml` (RSS 2.0 with `xmlns:g="http://base.google.com/ns/1.0"`) and `GET /api/v1/seo/merchant-feed` (JSON). Emits stable SKU IDs, landing-page URLs, prices with INR currency, sale prices, category breadcrumbs, and truthful `<g:identifier_exists>no</g:identifier_exists>` (omitting fake GTIN/MPN for custom handcrafted goods). Excludes DRAFT/ARCHIVED products and inactive variants. Tested with 11 focused feed tests in `test_merchant_feed.py`, 45 SEO tests, 14 media tests, and full backend suite clean. Documented feed contract and 6-step owner account setup checklist in `docs/merchant-center.md`.

## 5.11.2 returned by Gemini
[Backend responsive media contract](tasks/task-027-backend-responsive-media.md), owner Gemini. Implemented manifest loader/resolver in `app.services.media` consuming `public/images/optimized/manifest.json`. Populated real sorted WebP variants across `ProductListItem`/`ProductDetail.primaryImageMetadata`, `ProductImageOut.variants`, `HomepageCampaignOut` (`imageMetadata` and independent `mobileImageMetadata`), `CategorySummary`, `OccasionSummary`, `PromoBannerSectionOut`, `ImageTextSectionOut`, and SEO entities. Global snapshot version incorporates manifest hash. 18 media tests, 45 SEO tests, 11 merchant feed tests, and full backend suite clean (470+ passed, 7 skipped). Rebuilt and live-verified Docker API container at `http://localhost:8000`. Codex unblocked for final 5.11.1 storefront srcset acceptance.

## 5.13.1 returned by Gemini
Owner Gemini: [full description and actual-review catalogue summary](tasks/task-028-backend-product-content.md).
- Exposed full database `Product.description` on `SeoProductEntity` and `/api/v1/seo/snapshot`.
- Added review-derived `aggregateRating` (`{ratingValue, reviewCount, bestRating: 5.0, worstRating: 1.0, provenance: "VERIFIED_REVIEWS"}`) to `ProductListItem` and `ProductDetail` using Section 5.22 semantics; `null` when no verified reviews exist, ignoring seeded ratings.
- Implemented `SeoService.get_products_aggregate_ratings` batch query and `_to_product_list_items` to eliminate N+1 queries across `/products`, `/categories/{slug}/products`, `/collections/{slug}/products`, `/products/search`, `/products/trending`, and `/storefront/home`.
- Snapshot version hash incorporates `Product.description` and verified `Review` aggregates deterministically.
- All 49 SEO tests passing (including 4 dedicated TC01-TC04), 45 catalogue/media/feed tests passing; live Docker API rebuilt and verified. Unblocks Codex 5.13 final parity.

## 5.16 frontend returned /5.16.1 backend completed
Shared initial/client tags verified in 96 generated pages, actual localhost product→About navigation, 15 focused Docker tests/typecheck and fallback SAST. Main 5.16 was blocked on [5.16.1 truthful copy](tasks/task-029-truthful-share-copy.md), now completed.

## 5.16.1 returned by Gemini
Owner Gemini: [Truthful backend sharing copy](tasks/task-029-truthful-share-copy.md).
- Removed unsupported generated claims across all public routes in `backend/app/services/seo.py`:
  - Homepage (`/`): Replaced blanket "100% handcrafted heirloom... lovingly made with premium milk cotton yarn" with factual neutral description `Handcrafted crochet gifts, flower bouquets, amigurumi keepsakes, and home decor by {brand_name} in India.`; removed material and blanket artisan claims from FAQs; kept canonical H1 `Handcrafted Heirloom Crochet`.
  - About (`/about`): Corrected founder portrait alt text from invented activity "Sulocraft founder Anupama Sharma creating handcrafted crochet" to truthful factual description `Sulocraft founder Anupama Sharma with handcrafted crochet bouquet`; updated title to `Our Story | Handcrafted Crochet | Sulocraft` and description to neutral small-batch creation.
  - Categories (`/categories/{slug}`): Replaced fallback copy with neutral `Explore handcrafted crochet {category.name.lower()} by Sulocraft. Discover our collection.`; removed milk cotton claim from category FAQ.
  - Collections (`/collections/{slug}`): Removed invented "Limited edition heirloom" claims from fallback description.
  - Products (`/products/{slug}`): Replaced hardcoded prepend of "100% handmade heirloom crochet in premium milk cotton yarn" with direct preference for database-saved `product.short_description` or `product.description`; neutral fallback `Handcrafted {product.name} by Sulocraft.` when missing. Primary image alt text strictly prefers saved `ProductImage.alt_text` before falling back to neutral entity name (no injected material claims).
- Added 4 dedicated tests in `backend/tests/test_seo.py` (`test_5_16_1_tc01` to `test_5_16_1_tc04`); updated `backend/tests/test_media_metadata.py`.
- All 71 SEO tests passed (100%), 27 catalogue/merchant tests passed; Docker API rebuilt and verified live at `http://localhost:8000` across all 4 verified paths.
- Unblocks Codex 5.16 for final sharing parity verification. No assets modified; no push/deploy.


## 5.16 Completed — Codex final acceptance
Gemini5.16.1 integrated; neutral portrait caption correction and4targeted backend tests passed. Rebuilt local API, fresh96-page initial/client tag parity/build/budgets and actual localhost About/rose loaded images/head verified. Previous frontend/security checks retained; no new security boundary. External cache preview tracked under5.4 post-deploy.5.13 and5.11.1 returns available for separate final acceptance. No push/deploy.

## Final local Work005 return
Codex5.11.1/5.13 Completed,5.14/5.21 preparation delivered. Final tests/build/API/mobile hydration and security evidence in reports/task-004-final-local-audit.md. WebP MIME/path-boundary fix and tests added; no further Gemini implementation assigned.5.4 Blocked on owner decision about unverified testimonials/counts and authorized preprod/external launch checks. Async question presented; no response assumed. No push/deploy.

Owner decision recorded in DEC-005-13: retain demo review cards for preprod, hide before production using backend/admin content config, keep approved500+message. No review/data/UI removal performed; pending owner-content question resolved. Remaining5.4external release gates unchanged.

Authorized dev release active: Codex backend-first, thenfrontend to avoid new snapshot endpoint race. Verify workflows and dev.sulocraft.com after push. No production promotion.

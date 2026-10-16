# Work005 tasks

**CURRENT = Completed: implementation and authorized preprod acceptance passed; production operational checklist retained separately**

## In Progress
None

## Pending
None; launch blockers below.

## Completed
- [x] 5.4 — [Integrated SEO validation](tasks/task-004-seo-audit-vitals.md) — Codex; local tests and actual preprod acceptance passed, Cloudflaredev/backend/security green; external production operations explicitly documented.
- [x] 5.13 — [Content templates](tasks/task-013-category-product-content.md) — Codex; returned full-body/rating API and raw HTML parity verified.
- [x] 5.14 — [Search Console preparation](tasks/task-014-search-console-setup.md) — Codex; owner account/launch checklist delivered, account actions not claimed.
- [x] 5.21 — [Monitoring plan](tasks/task-021-seo-monitoring-followup.md) — Codex; cadence/owners/triggers/privacy delivered; no live data or automation claimed.
- [x] 5.11.1 — [Verified optimized media variants](tasks/task-026-optimized-media-variants.md) — Codex; real desktop/mobile WebP selection verified; cold-network limitation recorded.
- [x] 5.16 — [Social-sharing metadata](tasks/task-016-social-sharing-metadata.md) — Codex; Gemini5.16.1 integrated,96-page initial/client parity and local browser verified; external platform preview retained for5.4.
- [x] 5.16.1 — [Truthful backend sharing copy](tasks/task-029-truthful-share-copy.md) — Gemini; removed unsupported claims (blanket milk cotton, 100% heirloom, invented founder crochet activity, limited-edition collection claims); preferred saved descriptions/image alt with neutral fallbacks; 71/71 SEO tests passed; live Docker API verified across 4 paths; unblocks Codex 5.16.
- [x] 5.13.1 — [Full product content/catalogue review summary](tasks/task-028-backend-product-content.md) — Gemini; full Product.description in SeoProductEntity/snapshot, truthful aggregateRating (VERIFIED_REVIEWS) in ProductListItem/ProductDetail with N+1 batching across list/search/home/detail, snapshot version reacts to description/review changes, 4 dedicated tests (49/49 SEO suite clean, 45 catalogue/media/feed tests clean), live Docker API verified.
- [x] 5.11.2 — [Backend responsive media](tasks/task-027-backend-responsive-media.md) — Gemini; WebP manifest variant resolver, enriched catalogue/storefront/SEO schemas, snapshot version incorporates manifest hash, 18 media tests / 45 SEO tests clean, live Docker API verified; unblocks Codex 5.11.1.
- [x] 5.12 — [Crawlable internal linking](tasks/task-012-crawlable-internal-linking.md) — Codex;51 home anchors,24 products reachable, no missing public targets;21 tests/typecheck/build/browser/SAST passed.
- [x] 5.11 — [Mobile performance / Core Web Vitals](tasks/task-011-performance-core-web-vitals.md) — Codex; initialJSgzip-27.3%, deferred chunks/font discovery/background carousel,36 checks/typecheck,96-page build, local browser/SAST verified. Field/cold-network limitations recorded.
- [x] 5.15 — [Merchant Center feed/readiness](tasks/task-015-merchant-center-feed.md) — Gemini; RSS 2.0 XML + g: namespace feed & JSON API, stable SKUs, truthful identifier_exists='no' (no fake GTIN/MPN), draft/archived/inactive excluded, 11 tests passed; docs/merchant-center.md setup checklist.
- [x] 5.10 — [Image SEO](tasks/task-010-image-seo.md) — Codex; typed metadata, preserved frames, safe supplied variants;18 tests/typecheck,96-page build, Docker/API/mobile browser and SAST passed.
- [x] 5.20 — [Backend media metadata](tasks/task-020-backend-image-metadata.md) — Gemini; ProductImage dimensions/MIME migration, stdlib PNG/JPEG parser, reusable MediaMetadataOut, enriched catalogue/SEO/storefront schemas, SSRF/traversal protected; 14 media tests and 45 SEO tests passed.
- [x] 5.7 — [URL/canonical integration](tasks/task-007-url-canonical-strategy.md) — Codex; Worker redirect-mode503 fixed, canonical/lifecycle/query guards;14 tests/typecheck, HTTP/browser/security verified.
- [x] 5.18.2 — [Backend origin/indexing/lastmod policy](tasks/task-024-backend-origin-lastmod-policy.md) — Gemini; central origin validation, production fail-closed, preprod/dev noindex default, crawler Allow: / access, truthful nullable lastmod (omitted for static pages); 45 SEO tests passed.
- [x] 5.17.1 — [Backend brand truth](tasks/task-025-backend-brand-truth.md) — Gemini; omitted fabricated legalName/missing-brand profiles, excluded WhatsApp contact URL from sameAs, snapshot version hash updated; 37 tests passed.
- [x] 5.9 — [Breadcrumb/category/brand schema](tasks/task-009-breadcrumb-category-schema.md) — Codex; shared initial/runtime schema, visible DB ancestry,16 focused tests/typecheck/browser/security passed.
- [x] 5.19 — [Backend slug/redirect lifecycle](tasks/task-019-backend-slug-lifecycle.md) — Gemini; persistent `url_redirects` model and migration, 301 canonical redirects, chain flattening, loop prevention, 410 for archived items, 404 for missing; 33 SEO tests passed.
- [x] 5.8 — [Root sitemap/robots delivery](tasks/task-008-sitemap-robots-delivery.md) — Codex; local/Wrangler HTTP checks, indexed96-route/10-chunk simulation,8 tests/typecheck and full Semgrep pass.
- [x] 5.6 — [API-backed initial HTML rendering](tasks/task-006-indexability-rendering.md) — Codex;96 routes, shared React hydration, local Wrangler200/404/private-shell checks; see report.
- [x] 5.18.1 — [Global snapshot consistency](tasks/task-023-snapshot-version-consistency.md) — Gemini; deterministic store-wide version hash across public routes, entities, variants (price/stock), and brand settings; verified identical across pages; 32 tests passed.
- [x] 5.22 — [Review rating provenance](tasks/task-022-review-rating-provenance.md) — Gemini; derived aggregate ratings strictly from verified database Review records with truthful provenance (`VERIFIED_REVIEWS`); omitted when no real reviews exist; 31 tests passed.
- [x] 5.1 — [Runtime Product schema](tasks/task-001-structured-data.md) — Codex;13 focused/security tests and typecheck, Docker/browser/full SAST verified. Initial rendering/provenance follow-ups remain separate.
- [x] 5.18 — [Backend inventory/snapshot](tasks/task-018-backend-public-route-inventory.md) — Gemini returned29 SEO tests and419 backend tests passed (7 skipped).
- [x] 5.18 — [Backend route/content inventory and generators](tasks/task-018-backend-public-route-inventory.md) — Gemini; DB route inventory (`/routes`), paginated build snapshot (`/snapshot`), environment-aware robots.txt, 29 tests passed.
- [x] 5.3 — [Runtime metadata/headings](tasks/task-003-meta-social-prerender.md) — Codex;10 tests/typecheck, local browser and full Semgrep pass. Rendering/social acceptance remains5.6/5.16.
- [x] 5.2 — [Market/origin policy](tasks/task-002-international-seo.md) — Codex; DEC-005-7; runtime implementation assigned to5.3/5.6/5.7.
- [x] 5.5 — [Current SEO audit](tasks/task-005-current-seo-audit.md) — Codex; bounded HTML/API/browser findings and regression baseline recorded.
- [x] 5.17 — [Backend metadata and truthful entity contract](tasks/task-017-backend-seo-content-contract.md) — Gemini; DB-derived title/description/H1/robots/canonicalPath, brand/logo/social profiles, category/collection/product entities, Work019 reuse, truthful reviews & policies, 26 tests passed.
- [x] Initial /api/v1/seo/resolve endpoint and default sitemap/robots generators exist; current correctness/coverage to be audited.
- [x] Initial scripts/prerender.mjs created; DB content/claim fidelity remains unverified.

## Blocked / Ready for final integration
External account/policy approvals to be recorded in exact tasks; 5.5 completed; implementation dependencies remain in exact contracts.

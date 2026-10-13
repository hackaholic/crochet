# Work005 SEO policy contract — planned target

Existing wire fields are documented in docs/api-seo.md and implemented schemas; proposed additions below require Gemini's typed contract return before frontend consumption. No arbitrary HTML/React structure from backend.

## Truth and content
DB catalogue/brand/content and approved environment policy are authoritative. Unique titles/descriptions/H1, natural category copy, real variant SKU/price/currency/inventory, real category ancestry and approved review provenance. Unknown fields/policies nullable/omitted. Seed/demo reviews and counts are not evidence of genuine customer reviews; production eligibility must be established before emitting ratings.
Do not invent discounts, sale expiry, GTIN, social profiles, certifications/materials, FAQs, delivery timing, free shipping or returns. Reuse Work019 product detail fields/defaults rather than duplicate them.

## URLs and indexing
Preserve valid existing /products/<slug> and actual category/collection/occasion paths unless audit demonstrates a need. Lowercase stable slug identity; validated historical alias redirect to current canonical. One centralized route policy governs API, renderer, head metadata, feed and sitemap.
Canonical origin is validated config, not window location or a hardcoded build constant. Preprod/local use same code and environment policy but are not indexed. Production fails closed if required public origin/policy config is missing.
Private/admin/cart/checkout/account/login/wishlist/search/filter duplicates excluded from sitemap and noindexed appropriately. Robots disallow does not enforce privacy or guarantee deindexing; do not block crawler access to a page whose noindex must be observed. HTTP authentication protects private content.
Define actual missing/deleted404/410, redirects301, query/filter and meaningful pagination policies in5.5/5.7; do not blindly canonicalize all pages to page1. Never redirect missing URLs to home with200.

## Metadata and schema
Shared frontend/build helper produces title/description/canonical/robots and OG/Twitter tags from typed data; one authoritative instance after navigation/hydration.
Product/Offer and optional variant representation derive from visible current DB values. AggregateRating/reviews only with genuine approved provenance. Organization/WebSite use actual brand DB; BreadcrumbList reflects real hierarchy. ItemList/FAQ only when relevant and visible; no generic schema filler.
Safe JSON serialization escapes script terminators; markup/URL fields validated; no private customer/contact/session/secret data in public exports.

## Rendering and route inventory
Prefer least-complex static generation from complete paginated/versioned backend snapshot, including meaningful visible product/category content in initial HTML. Evaluate rebuild triggers/freshness, new/removed entities, unavailable API and invalid config. Do not ship stale fabricated fallback data or metadata-only hidden SEO content. SSR requires documented justification; client rendering must match initial snapshot without conflicting head/schema.
Inventory covers every eligible public route, not initial100 products or fixed48 routes. Sitemap truthful lastmod, standards-based index splitting and exclusions; storefront root URLs deliver valid resources through existing hosting workflow.

## Media and performance
Natural alt or empty decorative alt, known intrinsic dimensions, actual responsive variants, lazy noncritical assets, eager/priority LCP source. No imaginary R2 keys or repeat upload of existing artwork. All public image URLs reachable.
Mobile LCP/CLS/INP measurement before/after with reproducible conditions; lab and field data distinguished. No design/branding/layout system changes unrelated to accessibility/indexability/performance.

## External systems
Search Console DNS/account verification and Merchant shipping/returns/site ownership require user/account facts; prepare exact checklists, never invent tokens or policies. These steps do not block unrelated development. Feeds mirror landing-page price/availability and export only eligible real products/variants.

## Release acceptance
Local Docker/API/raw HTML/browser checks and meaningful regression/security tests per subtask; preprod checks after local pass; production promotion only after explicit acceptance, same artifact/config-only environment changes. Document missing account/browser/performance inputs as blockers, not passed checks.

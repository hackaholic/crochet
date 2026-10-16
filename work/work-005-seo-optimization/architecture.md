# SEO architecture and audit starting points

## Existing architecture to extend
Use the existing modular FastAPI service/schema/route boundary plus shared frontend SEO serialization and build rendering. Database content remains authoritative. No new CMS or framework migration by default.

- Fit: catalogue/brand/content already come from API; reuse typed fields for runtime metadata, initial HTML and feeds.
- Tradeoff: static generation requires content freshness/rebuild policy; evaluate live snapshot/refresh requirements in5.6 before choosing SSR.
- Maintainability: centralized route/canonical rules, SEO data contract and serializer prevent client/prerender/feed contradictions.

## Flow and ownership
DB/config → typed SEO entity + public route/content snapshot (Gemini5.17/5.18) → shared metadata/schema/rendering (Codex5.1/5.3/5.6/5.9/5.16).
Slug aliases/status decisions (Gemini5.19) → storefront HTTP routing (Codex5.7).
Verified media metadata (Gemini5.20) → reusable image templates (Codex5.10).
Sitemap/robots generators (Gemini5.18) → storefront root delivery (Codex5.8).
Merchant feed (Gemini5.15) uses the same prices/stock/canonicals and approved policy facts.

## Source-inspection findings — superseded by verified5.5 report
| Severity | Evidence | Required follow-up |
| --- | --- | --- |
| High | scripts/prerender-routes.mjs contains static routes/descriptions and hardcoded origins; backend resolver separately reads catalogue |5.5 inspect generated/live HTML, then5.6/5.18 replace duplicate business content with versioned DB snapshot |
| High | scripts/prerender.mjs supplies synthetic SKU fallback, fixed priceValidUntil,7-day/free return and delivery values, generic hypoallergenic FAQ |5.1/5.17 remove unsupported claims and validate provenance; include only approved real data |
| High | backend/app/services/seo.py and SEO schema defaults also contain policy/FAQ claims |5.17 audit all sources, not only frontend; optional unknown facts remain absent |
| High | SeoManager.tsx hardcodes logo/social organization fields independently of brand DB |5.17/5.9 align with actual brand.logoUrl and verified profiles |
| Medium | Initial prerender/client/HTTP routing may disagree on category paths, canonicals, robots and actual404; raw response not tested in this planning pass |5.5 route/status matrix;5.7/5.8 HTTP verification |
| Medium | Header/Footer/product destinations often use JS action buttons |5.12 distinguish actions from real href navigation without redesign |
| Unknown | Generated initial content, active route coverage, mobile field performance, Search Console/Merchant account state |5.5/5.11/5.14/5.15 require measurements/access; do not label complete |

## Recommended order
1.5.5 read-only audit: validate current code/raw HTML/DOM/HTTP and identify priorities.
2. Gemini5.17–5.20 contracts; Codex5.2 URL/market decisions. Backend tasks may run independently after audit within file ownership.
3. Runtime metadata/schema, DB snapshot initial rendering, canonical/robots/sitemap delivery.
4. Media, links/content, mobile performance and social previews.
5. Integrated5.4 acceptance; Search Console/Merchant user setup and lightweight5.21 monitoring.

## Official references for implementation validation
- [Ecommerce guidance](https://developers.google.com/search/docs/specialty/ecommerce)
- [Product structured data](https://developers.google.com/search/docs/appearance/structured-data/product)
- [Faceted crawling](https://developers.google.com/crawling/docs/faceted-navigation)
- [Merchant product specification](https://support.google.com/merchants/answer/7052112?hl=en)
Recheck official current requirements during relevant implementation; no third-party invented compliance values.

## Verified audit return
[5.5 evidence/report](reports/task-005-audit.md) confirms price/schema mismatch, hydration418, duplicate robots, mostly button navigation, inaccurate category H1 and missing about share image. Reuse exact evidence; do not repeat baseline setup. DEC-005-7 specifies targeting/origin policy; Gemini5.17 ready and Codex5.3 awaits typed return.

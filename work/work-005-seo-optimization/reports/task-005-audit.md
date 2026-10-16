# 5.5 — SEO audit,2026-10-13
Owner: Codex. Read-only source/build/API/browser audit; no application implementation or deployment.

## Environments/evidence
- Local development frontend8080/API8000, existing healthy Docker services.
- Built preprod artifact via `./scripts/test.sh frontend pnpm build:dev`;56 generated routes. Temporary Docker Vite preview4180 is an artifact test, not Cloudflare production behavior.
- Actual browser metadata/headings, anchor count and Product schema inspected. Public page headings explicitly awaited to avoid recording loading placeholders as final content.
- `task-005-http-audit.json`, `task-005-api-audit.json`, `task-005-rendered-public.json` preserve bounded public-data evidence.
- Automated HTTP requests to dev.sulocraft.com received403; deployment rendering/access remains unverified. Do not conclude site outage from this audit client response.

## Findings and exact owners
| Priority | Finding/evidence | Contract |
| --- | --- | --- |
| High | Raw8080 routes serve an empty root:0H1/0JSON-LD, generic index,follow, including/account and nonexistent path. Client later updates metadata; this is CSR development behavior, not reliable initial public HTML. |5.6/5.17/5.18 |
| High | Built sunflower initial HTML Product/Offer price1999, rating4.9/count75; live DB/UI price2199, runtime schema rating4.8/count88. Initial and client data conflict. Runtime sku is product id8; built SKU is independently copied. |5.1/5.6/5.17/5.18 |
| High | Generated root is manually assembled HTML, but main.tsx hydrates a different React tree. Actual built-preview console reports React error418. Error indicates server/client hydration mismatch, per https://react.dev/errors/418. |5.6 |
| High | Generated pages contain two index,follow robot metas. After preview runtime update, observed conflicting noindex/index metas; head update selects one while the duplicate remains. Static/runtime title, canonical and policy sources diverge. |5.3/5.6/5.16 |
| High | Prerender/SeoManager/backend schema defaults include fixed sale expiry2027-12-31, return window7/free returns, handling1–2/transit3–5 days, generic material/FAQ claims. No approved provenance established; seeded ratings are not automatically genuine reviews. |5.1/5.17 |
| High | localhost raw/account/missing and artifact preview return200 + indexable home fallback; client noindex is later. Preview clean sunflower URL returns home HTML whereas slash/index.html returns product HTML. Cloudflare uses SPA fallback; actual edge behavior still requires5.7 validation, not assumed identical to Vite. |5.7/5.8/5.19 |
| High | Root robots.txt/sitemap.xml return HTML locally/preview. Backend versions return valid text/XML; backend sitemap contains91loc entries with production fallback origin. No storefront-root integration or preprod noindex config verified. |5.8/5.18 |
| Medium | Final category flowers and collection gifts H1 both All Products, although resolver metadata names correct category/collection. Unknown collection best-sellers is correctly noindexed by resolver; use actual gifts for valid collection tests. |5.3/5.13 |
| Medium | Only1 anchor (skip-to-content) across observed live public pages; Header/Footer/product destinations are mostly JS buttons. Product/category hierarchy inaccessible as a standard href crawl graph. |5.12 |
| Medium | Actual about resolver image/static/images/sections/artisan-story.jpg returns404; other sampled home/product/category metadata images200. Organization logo and socials hardcoded separately from brand DB. |5.9/5.16/5.17/5.20 |
| Medium | Product/related images sampled have no intrinsic width/height; hero also lacks dimensions. Hero mobile source and priority logic already exist; reuse them. Frames/styles may prevent some CLS; do not assume missing attributes prove measured CLS failure. |5.10/5.11/5.20 |
| Medium | Build main JS551.98kB (gzip151.30kB), CSS82.99kB(gzip14.77kB); chunk-size warning. No reproducible field/lab CWV numbers yet. |5.11 |
| Decision | Runtime canonicals use window origin; renderer fixes production origin. Resolver falls back to production for localhost. Hreflang en-IN/x-default emitted without supported-market decision; parameter/pagination policy needs validation. |5.2/5.7/5.17/5.18 |

## Initial rendering decision
Prefer replacing hardcoded prerender inventory/content with complete versioned DB snapshots and a matching reusable React rendering path. Snapshot content and head must agree with initial hydration. No framework migration justified by this audit.5.6 must evaluate content refresh/build latency and genuine HTTP route delivery before final static-vs-SSR implementation decision.

## Priority sequence / pickup
1. Gemini5.17: truthful metadata/entity contract, optional approved policies/review provenance, real brand/logo/media fields.5.19/5.20 can independently follow audit within assigned ownership.
2. Gemini5.18: complete route/content snapshot and environment-indexability generators, after5.17.
3. Codex5.2 decision and5.3/5.1 metadata/schema after5.17;5.6 rendering after snapshot;5.7/5.8 real status/root-resource delivery.
4.5.9–5.13 links/content/media/performance and5.16 preview parity;5.4 integrated regression gate.
5. Search Console/Merchant external ownership and policy facts need user/account checks. No fabricated verification tokens, supported markets or delivery promises.

## Security disposition
Audit adds documentation/public-data evidence only; no auth, DB or public-content mutation. Safe escaping already exists in prerender JSON-LD, but unsupported factual data and private/preprod indexing are correctness risks requiring implementation. No private customer/auth/secrets captured. Review is Codex self-review, not independent review.

## Existing regression baseline
Shared Docker runner: frontend SeoManager3 tests + prerender2 Node tests passed; backend tests/test_seo.py9 tests passed. These tests validate existing assumptions and do not yet reject observed price/schema/hydration/duplicate-meta problems. Add these negative cases in owning implementation tasks; no claim current SEO is correct because baseline passes.

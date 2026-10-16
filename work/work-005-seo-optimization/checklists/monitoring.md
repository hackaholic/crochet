# SEO monitoring runbook

Owner: business owner for Search Console/Merchant account; Codex for reproducible technical failures. No new analytics platform or scheduled automation is created by this document.

## Cadence and action
| When | Check | Trigger / action |
| --- | --- | --- |
| Every catalogue/content publication | Existing API-backed build, route inventory/version, initial HTML, responsive media, redirects, Merchant feed price/stock | Stop release on failed build, metadata/catalogue mismatch, missing route, unsafe URL or broken primary media. Rebuild publishes changed DB content into initial HTML; API refresh alone does not replace an old artifact. |
| Every deployment | Smoke-test home/category/product/About plus private/missing/query URLs, robots/sitemap and environment indexing policy | Any wrong host, private exposure, invalid canonical, unexpected noindex in approved production or indexable preprod is a release failure; investigate same tested artifact/config, use existing rollback path. |
| Weekly after launch | Search Console sitemap fetch status, Page indexing errors/exclusions, security/manual actions; Merchant Diagnostics | Any security/manual action or sitemap fetch failure: investigate immediately. New unexplained404/5xx/canonical exclusions: compare affected URL set to deployment/catalogue changes; record exact reproduction. Intentional deletions/private noindex are not defects. |
| Weekly after sufficient traffic | Clicks, impressions, CTR, queries and landing pages; compare equal-length periods and seasonality | Record trends rather than automatic ranking promises. Sustained decline across two comparable periods triggers content/crawl inspection; do not treat low sample counts as proof of a regression. |
| Monthly / after meaningful UI change | Search Console field LCP/CLS/INP plus repeatable mobile lab on representative templates | Triage field “needs improvement”/“poor” URL groups; investigate LCP>2.5s, CLS>0.1 or INP>200ms at the relevant field percentile. Local warm lab is not field INP or cold mobile performance. If no data, record “insufficient data”; do not fabricate a green score. |
| Monthly | Product/Offer/breadcrumb metadata versus visible current prices, stock and actual reviews; image availability and internal links | Fix conflicting data first. Unknown product facts remain absent. Review owner-approved copy and actual media; never add schema-only claims. |

## Record a review
Store non-sensitive exports under `work/work-005-seo-optimization/reports/monitoring/YYYY-MM-DD.md` (directory created when real data exists). Include environment, revision/deployment, date window, URL samples, indexing counts, clicks/impressions/CTR/query/landing-page summary, CWV data availability, Merchant issues, finding owner/severity and next action/task link. Retain completed reports; create a small new subtask for a reproducible defect rather than rewriting history.

No credentials, cookies, personal customer data, verification tokens or full session/tracking URLs in reports. Google-account exports remain private if they include nonpublic business data; commit only owner-approved aggregate summaries. No additional tracking or remote telemetry installed.

## Current baseline / limits
Local build96routes; current JS/CSS budgets pass. Existing5.11 local loopback measurements and final5.4 observations are lab evidence only. Search Console, field CWV, Merchant approval and production traffic baselines are unavailable until account setup and accepted launch. Actual preprod/production rollout remains gated by5.4 release acceptance. Initial weekly/monthly review is manual, not an automation claimed as active.

References: [Search Console performance](https://support.google.com/webmasters/answer/7576553), [CWV report](https://support.google.com/webmasters/answer/9205520), and launch-search-console.md. Thresholds are triage signals; indexing or sales results are not guaranteed.

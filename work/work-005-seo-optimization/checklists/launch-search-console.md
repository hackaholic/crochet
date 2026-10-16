# Search Console and SEO launch checklist

Owner: business owner (account/DNS and factual copy); Codex (application/release verification).
Status: application preparation complete; account verification and public launch actions NOT performed.

## Before production
1. Approve factual catalogue descriptions/materials, actual shipping/returns policy and business contacts. Owner approved retaining the500+happy customers message and keeping demo review cards for preprod only. Before production, disable those demo cards via backend/admin content configuration while retaining the approved message; verify no demo testimonial is emitted as production review schema. DB storage alone is not evidence for other claims. No agent should invent policy or rewrite owner copy silently.
2. Run the local release checks in the Work005 final report. Push/deploy only when authorized. Exercise the same revision in preprod; keep `SEO_INDEXING_ENABLED=false`, preprod origin and API configured consistently. Never submit preprod sitemap for indexing.
3. After preprod acceptance, use the existing production build/deployment path with production configuration only. Frontend: `VITE_LAUNCH_MODE=full`, `SEO_PUBLIC_ORIGIN=https://sulocraft.com`, `SEO_INDEXING_ENABLED=true`, public production `SEO_EDGE_API_BASE_URL`/`VITE_API_BASE_URL`, and build-reachable `SEO_API_BASE_URL` where needed. Backend: matching `APP_ENV`, `SEO_PUBLIC_ORIGIN` and explicit `SEO_INDEXING_ENABLED=true`. Recheck the actual environment variable contract in `.env.example`, backend config and deployment docs; do not copy preprod secrets or change shared code.
4. Confirm public HTTP200 for homepage/category/product/About; real404/410 for unavailable records; redirects301 for approved legacy slugs. Initial HTML must contain current content, correct canonical and index,follow. Production must have no unintended X-Robots-Tag:noindex. Private/query pages stay excluded/noindex. Check root `/robots.txt`, `/sitemap.xml` and sitemap children. Keep coming-soon/noindex until owner accepts launch.

## Owner account steps
1. Sign into Google Search Console with the business owner's Google account. Add a Domain property for `sulocraft.com`.
2. Copy Google's actual DNS TXT verification value into Cloudflare DNS at the root requested by Google. Do not invent a token, replace unrelated TXT records, or change mail/SPF/DKIM records. Keep ownership verification in place. Verify inside Search Console after DNS is visible.
3. Record verification date and owner in the private operations record; do not commit account credentials or verification-token screenshots. A URL-prefix property for the approved HTTPS storefront can help isolate its reports from subdomains.
4. Only after accepted indexable production deployment, submit the production sitemap URL `https://sulocraft.com/sitemap.xml` in Sitemaps. Confirm it can be fetched. Sitemap submission does not guarantee indexing.
5. Inspect representative home/category/product/About URLs. Compare live-test render and canonical/indexability with the repository acceptance report. Do not request indexing for private, filtered or preprod URLs. Use the Page indexing report for exclusion/error trends; excluded private/preprod pages are expected.
6. Check product structured-data eligibility using Google's public testing tools and Merchant account Diagnostics after launch. Feed transport is implemented; Merchant account/domain verification/shipping/returns approval remains owner work (`docs/merchant-center.md`). Never invent GTIN, shipping commitments or review provenance.
7. Share a representative public production product and About URL in WhatsApp/social previews after authorization. Check title/image/alt and allow the platform cache to refresh. Localhost cannot be fetched by remote crawlers. No customer/session URLs should enter preview tools.

## Verification record
| Action | Current evidence | Owner / next action |
| --- | --- | --- |
| Local HTML/API/mobile verification | Work005 reports;96 generated routes | Codex final report |
| Preprod on current revision | Not deployed in this work session | Authorized release, then verify |
| Business facts / demo content |500+message approved; demo cards permitted in preprod only | Before production hide demo cards while retaining message; review other business facts |
| Search Console property/DNS | Account state unavailable; no token supplied | Owner steps above |
| Production indexing/sitemap submission | Not performed; production remains gated | Owner approval + accepted preprod |
| Field CWV / impressions/clicks | Not collected; no fabricated baseline | Monitoring checklist after traffic |

Official references reviewed 2026-10-16: [ownership verification](https://support.google.com/webmasters/answer/9008080), [Sitemaps report](https://support.google.com/webmasters/answer/7451001), [Page indexing report](https://support.google.com/webmasters/answer/7440203), [Core Web Vitals report](https://support.google.com/webmasters/answer/9205520). These are operational instructions, not evidence of account completion.

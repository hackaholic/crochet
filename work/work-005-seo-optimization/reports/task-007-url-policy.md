#5.7 — URL/canonical integration

Completed locally2026-10-14. No push/deploy.

## Behavior
Worker runs before HTML and reads the returned backend lifecycle contract. Case/trailing slash/legacy paths redirect directly to validated canonical paths; targets must resolve200 and cannot be private/external/looping. Archived410, missing404 and unavailable/malformed upstream503 never serve stale indexable product HTML. Assets remain served directly. Existing backend alias/migration ownership remains Gemini's.

Public routing policy/API origin is generated from validated build configuration; never falls back to preprod credentials. Initial and runtime canonical origins/noindex policy agree. Build snapshots accept public noindex metadata without pretending those pages are private. Full-storefront builds require a browser/Worker-reachable API URL; internal build API remains separate.

Queries use an empty noindex CSR shell to avoid hydration mismatches. Taxonomy query aliases redirect to their existing path families. Listing currently has no numbered pagination; page>1 returns404 and visible not-found UI rather than silently pretending it is page1. Resolver requests relay only relevant taxonomy selectors, never unrelated search/tracking/auth tokens. Private routes bypass public resolver calls and remain protected by existing authentication.

## Actual bug fixes
- Vite overwrote logical404/410 while sending its shell; local middleware now preserves those response statuses.
- Actual Workers runtime rejected fetch redirect:error and returned503. Changed to manual plus explicit non-success rejection;301/302/307/308 upstream redirects remain rejected. Detailed temporary diagnostics removed; only stage/error class retained.
- Asset refresh caused a temporary Wrangler watcher exit; restarted the completed artifact preview. This was a local tooling issue, separate from the request503.

## Verification
-14 Node rendering/route/failure/security tests and typecheck passed: `/tmp/work005-final-url-tests.log`. Six runtime metadata regressions/typecheck passed: `/tmp/work005-url-regression.log`.
- Normal Docker API startup applied the returned alias migration; existing archived QA slug used read-only. No catalogue mutation/reset. API and frontend rebuilt/restarted. Final configured build rendered96 routes (`/tmp/work005-url-browser-build.log`).
- HTTP localhost8080/Worker4181 matrix: policy and uppercase/trailing-slash aliases301; existing archived product410; unknown product404; page2=404; query listing200/noindex; current product200. Saved `reports/task-007-http-checks.json`. Permanent redirects now also get noindex headers when indexing disabled.
- Actual Worker browser: uppercase/slash URL lands on `/products/sunflower-bouquet`; one canonical equals configured local origin, noindex meta retained, product/images visible, no React hydration errors. Taxonomy query alias lands on `/categories/flowers`; filtered query has no bootstrap and stays noindex; page2 shows not-found UI. Screenshot `/tmp/work005-url-browser.png`.
- Local browser test used existing ADDITIONAL_CORS_ORIGINS via temporary `/tmp/work005-local-browser.yaml` and explicit CLI API/origin inputs. Application code is shared; no testing-specific runtime branch added. Main localhost8080 remains supported.
- Full Docker Semgrep zero blocking High/Critical findings (`/tmp/work005-url-sast.log`); nonblocking existing warnings retained.

## Self-review/limits
No secrets/session data in public policy. Safe paths and same-site targets, bounded requests and manual upstream redirect rejection verified. Unknown content is never redirected to homepage. No access-control bypass. No separate peer review claimed. Lifecycle checks require available backend; outage returns noindex503 deliberately. Dynamic lookup latency/cache tuning belongs to5.11. Preprod deployment verification remains a later release phase; nothing pushed.

Final source guard keeps private admin/account page parameters outside the public unsupported-pagination rule; focused route tests and typecheck pass (`/tmp/work005-private-pagination-tests.log`). Local frontend updated.

# 5.6 — API-backed initial rendering

## Implemented
- Build renderer uses the same React component/provider tree as the browser. Public snapshot bootstrap seeds catalogue, homepage, brand logo and route H1. Customer/session/cart state is never serialized.
- Removed the fixed catalogue/route/business-content prerender dataset and separate HTML design. Build requires a credential-free configured public API URL, validates route paths, counts, visibility and snapshot versions, checks product name/price agreement, and fails before publishing partial rendered pages.
- Shared catalogue refresh now fetches all pages; repeated pages fail instead of silently dropping products beyond100.
- Trailing-slash category hydration mismatch reproduced in the actual browser and corrected through normalized heading paths.
- Worker fallback supplies private routes with an empty noindex CSR shell and unknown routes with404; public assets use Cloudflare drop-trailing-slash HTML handling. Actual Wrangler routing verified below.

## Evidence
- Docker build:96 API-backed pages, successful (`/tmp/work005-render-build.log`).
- Shared Docker runner:4 initial Node boundary/serialization tests;12 focused metadata/schema/shop tests and typecheck passed (`/tmp/work005-render-tests.log`).
- Additional catalogue/hydration regression tests:15 passed; typecheck passed (`/tmp/work005-paging-tests.log`).
- Final snapshot-version/private-shell/404 unit tests:6 passed; typecheck passed (`/tmp/work005-version-tests.log`).
- Full Docker Semgrep:zero blocking High/Critical findings (`/tmp/work005-render-sast.log`); existing nonblocking warnings remain in the shared report.
- Actual built browser at4180:Sunflower2199, expected SKU/schema, no broken main images; Flowers6 filtered products/API H1; homepage API hero visible. Fresh category and homepage console logs have no React418 errors. Local8080 rebuilt storefront also renders Sunflower and images correctly.
- Screenshots: `/tmp/work005-rendered-product.png`, `/tmp/work005-rendered-category.png`.

## Final return
Completed. Gemini5.18.1 returned (420 backend tests passed,7 skipped reported); local API rebuilt and global version checked across actual paginated requests. Final full build succeeded with96 routes (`/tmp/work005-final-build.log`). Local Wrangler clean public routes200, deleted product404, admin/account200 noindex empty shell: `/tmp/work005-routing-checks.json`. Final build/routing unit tests7 passed and typecheck passed. Final browser product/category/home remained correct with no React418. Full security gate passed. Nothing pushed or deployed.

## Refresh policy and limits
Public catalogue/config edits require a fresh frontend build. Current delivery is build-time rendering with post-hydration API refresh, not runtime SSR. Failed API/snapshot consistency checks abort generation; do not deploy stale artifacts from an unsuccessful build. The public catalogue currently fits the complete bootstrap; payload reduction belongs to5.11 performance work before large-catalogue scaling.5.7 retains canonical redirect policy,5.8 root robots/sitemap delivery,5.9 remaining site/breadcrumb schema,5.16 richer social metadata.

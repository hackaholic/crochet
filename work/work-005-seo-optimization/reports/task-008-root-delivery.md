#5.8 — Root sitemap/robots delivery

Completed locally on2026-10-14. No push/deploy.

## Changes
Build exports root XML/text/header artifacts using validated environment policy and backend public route inventory. Public URLs must match configured canonical origin and existing indexable rendered pages. Count/byte splitting respects protocol ceilings; duplicate/private/invalid/unrendered entries and upstream failure abort export. Static generated-today timestamps are omitted; DB entity dates preserved.

Non-indexing builds publish an empty sitemap and crawlable robots, with site-wide HTTP noindex headers. Production requires explicit true/false indexing; true additionally requires a public HTTPS origin. Current tracked preprod and coming-soon configs remain false. Same helper supplies local Vite root responses. Build-time artifacts refresh with the successful storefront rebuild, not live DB edits.

## Verification
- Eight focused resource tests plus typecheck passed in shared frontend Docker runner: `/tmp/work005-root-final-tests.log`. Earlier rendering/resource regressions14 passed (`/tmp/work005-root-tests.log`).
- Rebuilt/restarted local frontend; non-indexing full build renders96 API pages: `/tmp/work005-root-build.log`. Production coming-soon build also passes: `/tmp/work005-coming-soon-seo-build.log`.
- Real localhost8080 and local Wrangler4181: root robots200 text/plain, sitemap200 application/xml parsed by ElementTree, empty sitemap; product HTML200 with noindex header. Evidence: `reports/task-008-http-checks.json`.
- Indexed simulation in isolated `/tmp/work005-indexed-export`: actual public API inventory96 routes exactly matched XML; configured10-URL threshold yields sitemap index plus10 valid XML chunks; production headers do not include global noindex. Nothing deployed.
- Actual browser verified Sunflower heading/images and returned to local homepage. Direct robots navigation was blocked by browser client; HTTP checks verified its successful response independently.
- Full Docker Semgrep passes with zero blocking High/Critical findings: `/tmp/work005-root-sast.log`; existing nonblocking warnings retained.

## Self-review/security
No provider secrets, user/session data, new network exposure or backend edits. Explicit origin/indexing validation; public-path constraints, XML escaping, pagination/file completeness checks and bounds tested. Existing access controls unchanged; robots never substitutes for authentication. No separate peer review claimed.

## Follow-up
Gemini5.18.2/task024 is pickup-ready for backend fallback-origin/development-indexing defaults and lastmod provenance discovered during integration. Root nonproduction protection is effective independently.5.7 canonical/redirect policy remains pending Gemini5.19. Root image sitemap extensions belong to5.10.

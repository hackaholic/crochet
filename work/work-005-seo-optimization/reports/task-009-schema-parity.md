#5.9 — Breadcrumb/category/brand schema

Completed locally2026-10-14. No push/deploy; Gemini5.19 remains separately owned.

## Changes
Shared pure `pageSchemas` builder handles product, visible product/shop BreadcrumbList, CollectionPage, and homepage Organization/WebSite. Returned API brand fields replace hardcoded frontend identities. Unverified legalName, founder/foundingDate, fictitious SearchAction and contact-only sameAs links are omitted. Missing/unsafe links and private/noindex/error schemas are omitted.

Reusable visible breadcrumbs and JSON-LD use the same validated API trail enriched with the actual catalogue category tree, supporting deeper ancestry rather than guessing parents. Links are crawlable; current page is unlinked and aria-current. No speculative ItemList/rankings while there is no shared filtered-list source. Product layout retained around its existing breadcrumb slot.

Initial HTML and runtime use identical builders and stable script IDs, preventing static/runtime duplicates. Optional category schema names match the visible API H1.

## Evidence
-16 focused schema, breadcrumb UI, metadata, hydration and shop tests/typecheck passed: `/tmp/work005-schema-tests.log`;4 brand-truth regression tests/typecheck rerun after final omissions: `/tmp/work005-brand-truth-tests.log`. Prerender guard tests passed before typecheck fixture correction.
- Rebuilt/restarted frontend and final build rendered96 API pages: `/tmp/work005-final-schema-build.log`.
- Actual localhost8080: Sunflower visible trail Home→Shop→Flowers→Sunflowers→Sunflower Bouquet, correct product/images; Flowers breadcrumb link reaches the category and its API H1/CollectionPage.
- Built preview4180: no React418 logs or broken main product images. Initial HTTP JSON-LD compared with actual hydrated browser JSON-LD: exact equality; one Product and one BreadcrumbList ID. Browser proof `/tmp/work005-schema-dom.json`; screenshot `/tmp/work005-breadcrumb-ui.png`.
- Final homepage Organization schema: one stable ID; logo matches visible official logo; no legalName/founder/foundingDate/SearchAction/contact-only sameAs.
- Full Docker Semgrep: zero blocking findings (`/tmp/work005-page-schema-sast.log`). Final follow-up only removed unsupported claims; link/serialization boundaries unchanged and covered by focused tests. Existing nonblocking warnings retained.

## Self-review/security
Public API data only; no private owner/session fields. Credentialed/non-HTTP links rejected; breadcrumb paths exclude private/query/traversal paths, duplicate paths fail; React/text and existing escaped JSON serializer handle markup. Public category traversal bounded to64 depth. No new network endpoint or authentication changes. Self-review only; no peer review claimed.

## Follow-up
Gemini5.17.1/task025 is pickup-ready to remove invented legalName and missing-brand profile defaults in backend. Coordinate shared services/seo.py with5.19; do not repeat official-logo uploads. Frontend independently omits those unsupported claims. Existing rating/content, canonical policy and performance tasks remain separate.

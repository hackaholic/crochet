# Work 005 notes

- Initial SEO resolver exists at `/api/v1/seo/resolve` with 15 passing tests in `backend/tests/test_seo.py`.
- Prerender script at `scripts/prerender.mjs` generates static HTML for 48 routes with hydration support.
- Need to audit schema richness against Google Rich Results guidelines (Product, Offer, AggregateRating, InStock).

2026-10-13 planning: Compared user complete-SEO prompt with existing four tasks and source code. Preserved IDs/filenames/history; added17 focused tasks for a total21. Initial code findings recorded in architecture.md; full raw HTML/HTTP/performance audit5.5 remains Pending. Existing prerender static business data and unsupported schema/policy defaults are priority audit targets. No app changes, test execution, upload or deployment in this pass.

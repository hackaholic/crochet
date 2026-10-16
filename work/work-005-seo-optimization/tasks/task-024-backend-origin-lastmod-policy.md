# Task 5.18.2 — Backend origin/indexing and lastmod provenance

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 005
**Work owner:** Codex

## Objective/context
Read work/GEMINI_WORKFLOW_PROMPT.md, this work README/tasks/decisions and this contract. Root 5.8 delivery is implemented. Remaining backend findings: development defaults to index,follow; missing canonical configuration can fall back to production domain; static inventory/sitemap pages claim today's date without an actual content change. Fix those policies without changing existing catalogue or asset setup.

## Scope
Central validated public-origin/indexing configuration, resolver/inventory/sitemap/robots consistency and nullable truthful lastmod. No new deployment process, catalogue rewrite, asset upload or frontend edits. Keep same code/config-only environment selection. Static dates with no provenance omitted. Never block noindex-page crawling just to hide nonproduction; HTTP authentication remains separate.

## Dependencies and relevant files
- Depends on: 5.17, 5.18
- Dependency context: Both returned. Coordinates with 5.19 because services/seo.py is shared; do not edit concurrently without work-local owner agreement.
- Blocked by: None
- Blocker reason: None
- Next action: Gemini pick up after checking active owner in coordination.md.
- Files: backend/app/services/seo.py; backend/app/core/config.py; backend/app/schemas/seo.py; backend/tests/test_seo.py; docs/api-seo.md

## Verified inputs
5.8 frontend exporter uses API /seo/routes; no asset/DB seeding required. Public tracked frontend mode configs specify no indexing and each site's origin. Frontend root nonproduction sitemap is empty and HTTP headers are noindex. Production sitemap rejects origins differing from configured SEO_PUBLIC_ORIGIN. Existing 5.18 snapshot hash and 5.22 rating provenance must be preserved.

## Tests/acceptance
- Development/preprod resolve to noindex by default; cannot silently advertise production canonical URLs.
- Production missing/malformed public origin/indexing config fails closed; valid config produces consistent resolver/routes/sitemap/robots.
- Static pages without a modification source omit lastmod; entity timestamps remain DB-derived; generators and snapshot DTOs agree.
- Tests for environment boundaries, invalid URLs/credentials, noindex crawler access, genuine timestamp changes and global snapshot hash regression. Run shared backend runner; record security disposition.

## Return handoff
Completed and returned to Codex for integration.

### Summary of Changes:
1. **Central Origin & Indexing Validation (`backend/app/core/config.py`, `backend/app/services/seo.py`)**:
   - Added `validate_public_origin` enforcing strict protocol (`http`/`https` with production requiring `https`), hostname, optional port, and explicitly rejecting credentials (`user:pass@`), paths, query strings, fragments, and production loopback addresses (`localhost`, `127.0.0.1`, `::1`).
   - In production (`ENVIRONMENT="production"`), missing or malformed `SEO_PUBLIC_ORIGIN` / `CANONICAL_BASE_URL` fails closed by raising `RuntimeError`.
   - In preproduction (`ENVIRONMENT="preprod"` / `"staging"`), default canonical base origin is `https://dev.sulocraft.com` unless configured. In development, defaults to `http://localhost:8080`. Non-production environments never fall back to `https://sulocraft.com`.
   - `SeoService._get_robots_directive()` enforces default `noindex,nofollow` for all non-production environments (`dev`, `staging`, `preprod`, `test`). In production, indexing is strictly opt-in via `SEO_INDEXING_ENABLED="true"` (fails closed to `noindex,nofollow` if unset or false).

2. **Truthful Nullable `lastmod` Provenance (`backend/app/schemas/seo.py`, `backend/app/services/seo.py`)**:
   - Updated `SeoRouteItem.lastmod: str | None = Field(default=None)`.
   - Core static pages (`/`, `/shop`, `/about`, `/contact`, `/shipping-policy`, `/return-policy`, `/privacy-policy`, `/terms`, `/faq`) do not have database-backed modification provenance and therefore emit `lastmod = None` in `get_public_route_inventory()`.
   - Categories, collections, and products continue deriving ISO 8601 timestamps from DB `updated_at`/`created_at`.
   - `generate_sitemap_xml()` only renders `<lastmod>` when a non-null timestamp is present. Static pages without DB provenance omit `<lastmod>`.

3. **Crawler Access in `robots.txt` (`backend/app/services/seo.py`)**:
   - `generate_robots_txt()` serves `Allow: /` across all environments so web crawlers can discover the HTTP `X-Robots-Tag: noindex, nofollow` and `<meta name="robots" content="noindex,nofollow">` directives. Private paths (`/admin/`, `/cart`, `/checkout`, `/account/`, `/api/`) remain disallowed.
   - The `Sitemap:` reference in `robots.txt` is only emitted when indexing is enabled.

4. **API Documentation (`docs/api-seo.md`)**:
   - Updated documentation to reflect nullable `lastmod`, fail-closed origin validation, and crawler access policies.

5. **Test Results**:
   - `backend/tests/test_seo.py`: 45 passed (100%).
   - Full regression suite (`./scripts/test.sh backend`): 433 passed, 7 skipped.
   - Zero security regressions; strict validation eliminates SSRF/spoofing risks through host header injection or malformed origins.

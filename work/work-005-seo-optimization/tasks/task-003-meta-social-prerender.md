# Task 5.3 — Meta tags, dynamic social cards, and prerender route coverage

**Owner:** Codex
**Status:** Completed

## Objective

Ensure all eligible public pages in the backend route inventory have unique accurate metadata and initial-HTML parity. Preserve private-page noindex; indexing is not guaranteed.

## Context and contract

Social platforms and search bots do not always execute JavaScript. Pre-rendering ensures bots receive fully-populated `<title>`, `<meta name="description">`, and `<meta property="og:image">` tags in the initial HTTP payload.

## Scope

- In scope:
  - Run `scripts/prerender.mjs` to generate HTML files into `dist/`.
  - Ensure dynamic social card images use validated configured public media URLs.
  - Review concise, descriptive titles/descriptions; avoid arbitrary strict character counts and keyword stuffing.
- Out of scope:
  - Private account or admin pages (must remain `noindex, nofollow`).

## Dependencies and relevant files

- Depends on: 5.5, 5.17
- Dependency context: Audit and backend metadata contract returned;5.6/5.16 own rendering/social implementations.
- Inspect/edit:
  - `scripts/prerender.mjs`
  - `src/components/SeoManager.tsx`

## Acceptance checks — owned runtime scope
- [x] API title/description/canonical/robots applied once; duplicate initial tags removed and unapproved alternate locale links removed.
- [x] Database h1 drives category/collection heading without visual redesign; private/error fallback stays noindex.
- [x]10 focused tests/typecheck, rebuilt local API/frontend and actual browser checks pass; full Semgrep zero blocking High/Critical.
- Initial HTML and complete prerender inventory checks from the original broader description are owned by5.6; social preview acceptance by5.16, per existing planning scope partition. Neither is claimed complete here.

## Handoff back

- Update `work/work-005-seo-optimization/tasks.md` and `notes.md`.

## Planning clarification — 2026-10-13
**Work item:** Work 005
**Work owner:** Codex
Implementation boundary: Own reusable title/description/canonical/robots and heading integration. Original broad scope retained as parent; initial-HTML rendering5.6 and social previews5.16 own their implementations. No duplicate parallel work.
- Blocked by: None
- Blocker reason: Dependency return not yet verified; do not start dependent implementation
- Next action: Read5.5 audit return and exact dependencies above

## Traceable test and security additions
- 5.3-TC01: Test stated acceptance against actual active DB records and raw HTML/client output; record exact automated/local commands and results.
- 5.3-TC02: Test missing/private/unapproved content, injected text/URLs and conflicting canonical/schema/environment input; no secrets, invented facts or duplicate head tags.
- Security: Safe JSON-LD/HTML escaping, bounded typed API data and validated origins; schema must match visible data. Record disposition and self/peer review.
- Local Docker/API/browser acceptance required for behavior changes; no push or production/account action in this planning task.
- Update exact contract plus work-local tasks/notes/coordination on return. Preserve original objective/history above; split ownership prevents duplicate work.

Return2026-10-13: Added reusable head helpers/API canonical+h1 integration with cancellation and callback to ShopPage. Browser Flowers/Gifts H1, one canonical/robots, no default alternates, private/missing noindex verified; About share image200 after backend17. Screenshot /tmp/work005-category-metadata.png. No push. Shared runner SAST used fallback AST checks; separate full Docker Semgrep also passed, /tmp/work005-metadata-full-sast.log. Security self-review: unsafe canonical schemes/credentials ignored, API failure noindex, stale response cannot overwrite head.

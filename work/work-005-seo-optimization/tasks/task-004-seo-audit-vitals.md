# Task 5.4 — Automated SEO test suite and Core Web Vitals verification

**Owner:** Codex
**Status:** Pending

## Objective

Add automated unit and regression tests for all SEO components, ensure zero hydration mismatches, and verify Core Web Vitals (LCP, CLS, FID) to maintain high search ranking scores.

## Context and contract

Follow the project working rule: add automated tests and verify locally in Docker.

## Scope

- In scope:
  - Add/update tests in `src/components/SeoManager.test.tsx`.
  - Add backend test cases for sitemap URL generation in `backend/tests/test_seo.py`.
  - Verify zero layout shifts (`CLS < 0.1`) and fast image loading (`LCP < 2.5s`).
- Out of scope:
  - Third-party paid SEO audits.

## Dependencies and relevant files

- Depends on: Task 5.3.
- Inspect/edit:
  - `src/components/SeoManager.test.tsx`
  - `backend/tests/test_seo.py`

## Acceptance checks

- [ ] `npm test` and `pytest backend/tests/test_seo.py` pass.
- [ ] No hydration errors in browser console during client hydration of pre-rendered pages.

## Handoff back

- Mark Work 005 completed in `work/INDEX.md` and `work/work-005-seo-optimization/tasks.md`.

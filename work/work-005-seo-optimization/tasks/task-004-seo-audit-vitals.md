# Task 5.4 — Automated SEO test suite and Core Web Vitals verification

**Owner:** Codex
**Status:** In Progress

## Objective

Add automated unit and regression tests for all SEO components, ensure zero hydration mismatches, and verify Core Web Vitals (LCP, CLS, INP) to measure real user experience without guaranteeing rankings.

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

- Depends on: 5.1, 5.2, 5.3, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11, 5.12, 5.13, 5.16
- Dependency context: Task 5.3.
- Inspect/edit:
  - `src/components/SeoManager.test.tsx`
  - `backend/tests/test_seo.py`

## Acceptance checks

- [x] Focused pnpm frontend/build tests and isolated backend test runner pass; no shared DB test execution.
- [x] No hydration errors in browser console during client hydration of pre-rendered pages.

## Handoff back

- Mark5.4 complete with evidence; mark Work005 complete only when every required task/account readiness/monitoring acceptance is satisfied.

## Planning clarification — 2026-10-13
**Work item:** Work 005
**Work owner:** Codex
Implementation boundary: Integrated SEO regression/launch acceptance. Performance measurement owned by5.11; use INP rather than obsolete FID. Validate HTTP/root resources, initial HTML/DOM parity, public/private indexability, truthful schema and mobile/browser regression.
- Blocked by: Owner launch acceptance
- Blocker reason: Local checks pass; authorized preprod rollout and external launch/device/account acceptance remain; owner review-content decision recorded in DEC-005-13.
- Next action: Keep demo reviews in preprod; before production hide demo cards via backend/admin config and retain approved500+message. Await authorized preprod verification and documented launch checks.

## Traceable test and security additions
- 5.4-TC01: Test stated acceptance against actual active DB records and raw HTML/client output; record exact automated/local commands and results.
- 5.4-TC02: Test missing/private/unapproved content, injected text/URLs and conflicting canonical/schema/environment input; no secrets, invented facts or duplicate head tags.
- Security: Safe JSON-LD/HTML escaping, bounded typed API data and validated origins; schema must match visible data. Record disposition and self/peer review.
- Local Docker/API/browser acceptance required for behavior changes; no push or production/account action in this planning task.
- Update exact contract plus work-local tasks/notes/coordination on return. Preserve original objective/history above; split ownership prevents duplicate work.

## Final audit pickup
Integration5.13/5.11.1 and checklist5.14/5.21 are being verified in one bounded local pass; no deployment/account changes authorized. Final negative WebP path/MIME tests and built mobile hydration evidence required. External launch/device/account checks must remain explicit if unavailable; do not substitute local loopback for field/cold mobile acceptance.

## Final local return
[Final local audit](../reports/task-004-final-local-audit.md):29Node+52component tests/typecheck,53SEO+11Merchant and final20media cases pass across scoped runs.96-page raw HTML/content/social parity; actual mobile build hydration/images/overflow; local HTTPnoindex resources; WebP MIME/root-boundary fix verified; fallback SASTzero findings. Local acceptance boxes above satisfied. Blocked only on explicit external/owner launch gates listed in report; no unsupported production/browser/field/account completion. No push/deploy.

## Authorized dev release —2026-10-16
User authorized git commit/push and preprod safety verification. Codex will release additive backend/API+responsive manifest first, wait for backend workflow/API health, then frontend/config/docs. Production remains untouched; demo homepage reviews stay enabled in preprod and approved500+message retained. Local complete-backend/security release checks run before first push. Account/production/device acceptance remains separately recorded.

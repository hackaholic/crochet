# Task 15.9 — Mobile campaign labels hidden by fixed header

**Owner:** Codex
**Status:** Completed
**Work item:** Work 015

## Objective / scope
Keep every API campaign eyebrow/title/CTA below the actual fixed header on mobile, including a wrapping announcement. Preserve the compact visible hero, image bounds, arrows, API content and desktop composition. Reuse one measured header-offset token rather than per-slide/phone offsets. Exclude expanded mobile navigation from persistent header measurement.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Existing local services and Work024/025 changes remain uncommitted; preserve them. No backend or asset work required.
- Blocked by: None
- Blocker reason: None
- Next action: Measured shared header offset, focused regression tests, local rebuild and all-slide checks.
- Inspect/edit: src/components/Header.tsx, src/hooks/useHeaderOffset.ts, src/components/HeroCarousel.tsx, src/components/heroLayout.css, relevant tests.

## Test cases
|ID|Category|Scenario|Expected|Evidence|
|---|---|---|---|---|
|15.9-TC01|Regression|Header/announcement resize and mobile menu open|Offset tracks persistent chrome, excluding menu; observer cleaned up|Pass — evidence below|
|15.9-TC02|Boundary|All five campaigns at320/390/430px|At page top all labels below header; CTA above controls; consistent compact visible area|Pass — evidence below|
|15.9-TC03|Regression|Loading/no-data hero and1280px desktop|Same mobile offset for loading/loaded; accepted desktop styles unchanged|Pass — evidence below|
|15.9-TC04|Security/accessibility|Keyboard/swipe, API data, reduced motion|Existing semantics/content/controls preserved; no new HTML or request boundary|Pass — evidence below|

## Acceptance / handoff
- [x] Relevant tests and typecheck pass.
- [x] Frontend rebuilt; actual local all-slide mobile/desktop geometry and screenshot checked.
- [x] Record self-review/security disposition and native-engine limitations.
- [x] Update work-local state; no push requested.

## Return — 2026-10-19
Reproduced at page top390px: fixed header bottom123px, label top109px (14px hidden). Added shared measured header-height token via ResizeObserver with window-resize fallback and cleanup, excluding the expanded mobile menu. Mobile hero/skeleton use that token; visible hero remains312px. Desktop CSS unchanged.

Docker frontend typecheck+16header/hero/hook tests passed (`/tmp/work015-header-tests.log`); frontend rebuilt/restarted (`/tmp/work015-header-build.log`). Browser checked15combinations: five API campaigns×320/390/430px. Every label13pxbelowheader, every CTAatleast21pxabovecontrols, visibleframe312px, nohorizontaloverflow.1280pxdesktopretains620pxhero/112pxtoppadding. [Geometry evidence](../reports/task-009-mobile-geometry.json), [corrected festive preview](../reports/task-009-mobile-label-clearance.jpg).

Security disposition: Pass for layout-only scope. Actual diff self-reviewed: no new API/auth/HTML/DB boundary; observer/listener cleanup and menu exclusion tested. Existing swipe/keyboard/reduced-motion tests pass. Native Firefox/actual device checks not available this turn; these are in-app viewport checks, not claims of new native engine acceptance. No push/deployment.

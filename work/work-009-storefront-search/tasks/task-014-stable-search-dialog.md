# Task 9.14 — Stable search popup loading geometry

**Owner:** Codex
**Status:** Completed

## Scope / cause
App lazy-loads SearchOverlay with generic centered OverlayLoading fallback, then swaps to a top-aligned wider dialog. Content-based height changes again between guidance/loading/results. Share one eagerly loaded top-anchored frame and fixed responsive panel footprint across fallback and loaded states; results scroll internally. Keep auth fallback unchanged. No search API/business-content changes.

## Dependencies
- Depends on: 9.13
- Blocked by: None
- Next action: Owner review on localhost; no push/deployment requested.

## Acceptance / tests / security
Same shell classes/geometry for code-loading and loaded search. Guidance/loading/empty/error/results use constant shell height; small phone/keyboard viewports remain bounded. Search close/Escape/focus and keyboard selection/pagination regressions continue passing. Loading fallback close/Escape usable. No scale/position animation, new network destinations, HTML sinks or auth changes. Typecheck/tests and actual local desktop/mobile checks, including first lazy open and typed/empty states. No Gemini dependency or push.

## Return — 2026-10-24
- Root cause: search's lazy Suspense fallback used generic small centered OverlayLoading; loaded overlay used top margin/wider content-driven shell. API states changed intrinsic height. This was layout replacement, not an intentional scale animation.
- Added eagerly shared SearchDialogFrame/CSS and SearchLoading; App uses it only for search. Responsive fixed shell footprint with internal result scrolling; no translate/scale/size transitions. Prevent-scroll focus, fallback Escape/close, restoration and existing live focus trap retained. Auth loading unchanged.
- Docker frontend typecheck and15 tests passed (SearchOverlay13 + shared frame2): fallback/live share shell hooks, fallback close/Escape/focus, live focus restoration, async cancellation/error/429/pagination, keyboard navigation regressions. Security self-review Pass: no new API/auth/HTML sink, existing failed/stale request protections pass; no secrets/config exposure. No fresh SAST scan for layout-only scope.
- Rebuilt/restarted local frontend. Actual desktop empty→rose results: same80px top/672px width/576px height. Mobile results→no-match: same32px top/356px width/576px height, no overflow. Short320×380 viewport: top32/height332/bottom364. Escape removes dialog/restores Search trigger. First local open exercised; fallback geometry proven through shared eager CSS and unit shell comparison, not a forced slow-network recording.
- Evidence reports/task-014-geometry.json, search-stable-desktop.jpg, search-stable-mobile.jpg. Native Firefox/physical phone keyboard unverified; responsive in-app checks only. No backend/Gemini dependency, push or deployed changes.

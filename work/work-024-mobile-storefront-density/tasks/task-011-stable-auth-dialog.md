# Task 24.12 — Stable centered login popup

**Owner:** Codex
**Status:** Completed

## Scope / dependencies
- Depends on: 24.11
- Dependency context: Work009/9.14 fixed the analogous search fallback; login must remain centered.
- Blocked by: None
Replace generic small centered lazy fallback with eagerly shared authentication frame/header, same width/responsive height as live login. Keep all login/sent/error states centered with internal scrolling, no scale/geometry transition. Preserve OAuth/email API behavior and provider configuration. Add close/Escape/focus containment/restoration to shared frame. No backend/Gemini dependency or push.

## Acceptance / security
Loading/live shell share geometry hooks; center remains constant across content states, viewport overflow prevented. Existing provider/email success/error tests pass; fallback/live keyboard close/focus trap/restoration tests. Typecheck/tests, rebuild frontend, local desktop/mobile/short viewport checks. Do not send real auth emails or alter existing user sessions for visual checks; use existing invalid-link display route if logged in. No auth API/token changes, secrets or new HTML sinks. Record unverified native keyboard/browser checks.

## Return — 2026-10-24
- Added eager AuthDialogFrame/AuthDialogHeader/AuthLoading shared by App Suspense fallback and AuthModal. Removed obsolete small generic OverlayLoading. Login remains centered, max448px wide, responsive672px bounded height; body scrolls internally. Search stays top-aligned and its fallback is unchanged.
- Shared frame provides backdrop/close/Escape, Tab containment, prevent-scroll focus and restoration. OAuth/email API/provider logic unchanged. No live sign-in/email submission or logout during browser QA.
- Docker frontend typecheck and9 tests passed (AuthModal4, AuthDialogFrame3, SearchDialogFrame2): provider visibility/no mock identity fallback, magic-link confirmation, generic token-safe errors, identical loading/live shell hooks, fallback close/Escape and focus trap/restoration. Security self-review Pass: no new auth/token/HTML/network sinks; existing safe error and no-mock provider regressions pass. No fresh SAST scan for presentation-only scope.
- Rebuilt frontend. Actual local invalid-link display route used because browser session already signed in; no session altered. Desktop1280×720 center(635,360), width448/height672; mobile390×844 center(190,422), width348/height672; short320×380 center(155,190), width278/height348. Centers equal usable viewport centers, no horizontal overflow; body scrolls on mobile/short viewports. Escape closes dialog. Native mobile keyboard/Firefox and live provider sign-in not retested; fallback shared geometry verified by tests/eager CSS rather than forced network throttling.
- Evidence reports/task-011-login-geometry.json and centered-login-mobile.jpg. No Gemini/backend dependency, push or deployed change.

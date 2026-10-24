# Task 24.11 — Footer catalogue navigation starts at top

**Owner:** Codex
**Status:** Completed

## Scope / dependencies
- Depends on: 24.10
- Blocked by: None
Footer Shop/Collections links call router navigation directly, unlike App navigation which also resets scroll. Reuse one local navigation callback to reset to top for these explicit link clicks; do not add global route effects or override browser Back/Forward restoration. Keep real href/modifier/new-tab semantics in DestinationLink.

## Acceptance / security
Tests cover All Products, Gifts, Birthday Gifts, Custom Orders query URL and category destinations: route changes and scrollTo top invoked once. Existing footer/destination URL-policy tests retained. No new arbitrary URL handling, API/auth/DB changes; internal URLs still generated from catalogue and safeDestination validated. Rebuild frontend, verify actual footer click while scrolled down (including same-path navigation) lands at top. No Gemini dependency or push.

## Return — 2026-10-24
- Footer Shop/Collections links now share navigateToTop: existing router navigation plus immediate scrollTo(top0,left0). Only explicit footer clicks changed; no global route effect/history restoration override. Native href/modifier/new-tab handling remains in DestinationLink.
- Docker frontend typecheck and8 tests passed (Footer6, DestinationLink2). Parametrized destinations include same-path Shop, Gifts, Birthday Gifts, Custom Orders query and Flowers category; expected URL and one top-scroll call asserted. Link safety/modifier checks retained. jsdom prints existing unsupported full-document navigation notices in DestinationLink tests; actual browser verification passed.
- Frontend rebuilt/restarted. Local browser from bottom: Shop3013→0 (same path), Gifts3013→0, Birthday Gifts3053→0, Custom Orders1730→0, all correct URL/query. Initial homepage4100→Shop0 verified too. Evidence reports/task-010-footer-navigation.json and footer-navigation-top.jpg.
- Security self-review Pass: no new URL construction/sinks/auth/API/DB changes, existing safeDestination negative tests passed. No new SAST scan for scoped scroll callback. Browser Back/Forward logic untouched, not separately retested; native Firefox/mobile engines unverified. No Gemini dependency, push or deployment.

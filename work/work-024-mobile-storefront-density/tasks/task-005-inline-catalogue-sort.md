# Task 24.6 — Inline catalogue sorting beneath navigation

**Owner:** Codex
**Status:** Completed

## Objective / scope
Render the native sort select as compact breadcrumb-sized text beside breadcrumbs directly below the measured menu boundary. Keep Filters beside title/count rather than a dedicated controls row. Shared layout across catalogue routes, no business-content/backend changes.

## Dependencies
- Depends on: 24.5
- Blocked by: None
- Next action: Owner review on localhost; no push requested.

## Acceptance / tests / security
- Mobile320/390/430 and desktop1280: no overflow or menu overlap; sort stays beside breadcrumbs and products move upward. Long sort option must fit without expanding layout.
- Native labelled select retains all options and correctly reorders products; drawer/chip tests remain passing.
- Preserve breadcrumb links, API text escaping and complete description below results. No new trust boundary, requests or HTML sinks. Record self-review and browser evidence.
- No push/deployment in scope. No Gemini dependency.

## Return handoff — 2026-10-20
- Shared catalogue navigation strip now places native labelled sorting beside breadcrumbs at menu boundary. Both use12px text; strip/select32px high. Filters sits beside title/count; no full-width sort row. Visible keyboard focus retained, no menu height change.
- Added regression asserting sorting lives outside title toolbar and low/high price options reorder cards correctly. Typecheck and11 focused frontend tests passed (ShopPage7, CatalogueIntro3, ProductCard1).
- Docker frontend rebuilt/restarted; API and database healthy. Actual localhost Baby320/390/430/1280px checks: no horizontal overflow; sort strip begins at measured menu bottom. At390px first product249.64→209px; at430px233.64→193px. At320px title/count naturally wraps; no content clipped. Long price-sort label stays within viewport.
- Real mobile low-to-high selection orders Bunny1199, HeartBear1799, Trio1999, Blanket2199, Hamper2499. Screenshot `reports/inline-sort-mobile.jpg`; measurements `reports/task-005-after.json`.
- Security/self-review Pass: presentation-only change; existing escaped-description/mismatched-route tests pass, no new API/auth/DB/HTML sinks. Native select remains labelled and keyboard-operable. No new SAST scan warranted for this scoped template/CSS change; no claim of native Firefox/device coverage.
- No Gemini work required. Nothing pushed/deployed.

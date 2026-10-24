# Task 24.8 — Unified catalogue bar and contextual category filters

**Owner:** Codex
**Status:** Completed

## Objective / scope
Remove active-filter chips on desktop/mobile; retain checkbox toggling and Clear filters. Put compact bold heading/count centrally in shared breadcrumb/sort bar, no separate oversized title row. Desktop three columns; mobile wrap gracefully with accessible sort/filter controls. Category routes remain scoped to route category, expose relevant descendant category filters only, plus scoped price/occasion/customizable filters. All-shop allows multiple category filters; heading is All Products, selected category name, or Filtered Products. API names/text remain backend-driven.

## Dependencies
- Depends on: 24.7
- Blocked by: None
- Next action: Owner review at localhost; new changes not pushed.

## Acceptance / tests
1. No active chips; checkboxes deselect, clear resets optional filters without escaping route category; mobile drawer behaves same.
2. Shop zero/one/multiple category selection updates title and count; sort works.
3. Category URL with conflicting category query cannot widen listing; unknown category remains empty; route change clears stale selections.
4. Scoped options exclude unrelated roots and impossible prices; full API description/escaping/breadcrumb links preserved.
5. Local phone320/390/430 and desktop1280 no overflow; compact center summary and native sort work.
Security: public UI filtering only, no authorization substitute; no new API/auth/DB boundary or HTML sink. Negative tampered query/unknown category and escaped content tests required. Run focused tests/typecheck, record self-review and actual local rendering. No backend/Gemini dependency. New changes stay local pending review/push.

## Return — 2026-10-24
- Shared header now places breadcrumb/compact bold h1+count/sort in three desktop columns; mobile uses a tight two-row grid with centered summary and Filters. Removed active chips and old title toolbar. Checkboxes and Clear all filters remain.
- Category URL is immutable listing scope; show only populated descendant categories and scope price/occasion/customizable counts to route products. Shop keeps multi-category selection with All Products / API category name / Filtered Products titles. Breadcrumb navigation clears category state.
- Docker frontend typecheck and18 tests passed: ShopPage10, shopFilters4, CatalogueIntro3, ProductCard1. Tests cover category query tampering, unknown category empty state, clear preserving root, multiple shop selections, checkbox deselection, sort ordering, escaped/mismatched descriptions and image frames.
- Local frontend Docker rebuilt/restarted. Actual320/390/430/1280 checks: no overflow or chips, centered summary matches bar center,5 Baby images loaded. Bar76px mobile/40px desktop; first cards181px at390,149px desktop. Category Blankets→1, Clear→5 Baby; breadcrumb Shop resets scope; Flowers6→Flowers+Baby11 updates heading to Filtered Products, clear resets all. No data mutation.
- Evidence: reports/task-007-after.json, unified-catalogue-mobile.jpg, unified-catalogue-desktop.jpg.
- Security/self-review Pass: public client-side scope is not an auth control; no backend/auth/DB boundary or HTML sink added. Negative tampered query/unknown route and React escaping checks executed/passed. No fresh SAST scan for this frontend-only scope; native Firefox/real-device coverage unavailable and unverified.
- No Gemini dependency. Existing pre-task revision pushed fa49f78; this implementation is local only, no deployment.

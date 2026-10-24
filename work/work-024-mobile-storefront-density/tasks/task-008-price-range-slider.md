# Task 24.9 — Reusable price range slider

**Owner:** Codex
**Status:** Completed

## Scope
Replace fixed brackets with native dual-range inputs, Min/Max numeric fields and Reset price in the existing shared filter panel (desktop/mobile). No slider library exists in dependencies; reuse built-in HTML range controls instead of adding a dependency. Default selectable bounds₹0–₹100000, configurable through validated VITE_CATALOGUE_PRICE_MIN/MAX. Whole rupee precision. Full bounds means no price restriction. Preserve category route scope, other filters, sorting, count and no chips. No backend/Gemini work or push.

## Dependencies
- Depends on: 24.8
- Blocked by: None
- Next action: Owner review locally; no push/deployment requested.

## Acceptance / tests / security
- Sliders and numeric fields update inclusive min/max price selection together; reversed/out-of-range values are clamped, blank/invalid/nonfinite/fractional fields rejected without corrupting state.
- Reset price changes price only; Clear all resets price and optional filters while preserving route scope. Default full range must not hide products.
- Component keyboard/native semantics labelled; independent desktop/drawer instances have unique IDs. Mobile320/390/430 and desktop1280 no overflow; actual filtering works locally.
- Tests cover config bounds/invalid values, component edits/clamps/reset and ShopPage integration. Typecheck plus relevant regressions/security negative tests, Docker rebuild and concise browser acceptance.
- Client price filtering is public presentation, not checkout price authority. No HTML/network/auth/DB sinks introduced; existing escaping and route-tampering regressions required. Record unavailable native engine checks.

## Return — 2026-10-24
- Reused native HTML range controls in reusable PriceRangeFilter; no external dependency. Shared sidebar/drawer supports two bounds, precise fields and Reset price. Bracket UI removed; full range/reset leaves catalogue unrestricted. Validated public env bounds in src/config/catalogue.ts and .env.example.
- Verification: Docker frontend typecheck +30 focused tests passed (component4/config8/ShopPage11/CatalogueIntro3/shopFilters4). Added upper-bound regression then ran only that new test:1 passed,11 previous ShopPage tests intentionally skipped by selection.31 unique tests passed overall; no app changes after main check.
- Negative checks passed: blank/fractional/unsafe values preserve valid filter, negative/out-of-range/crossed values clamp; invalid config throws; category query tampering/unknown category and escaped content regressions pass. Independent component IDs tested. Security self-review Pass: public presentation only, no trusted checkout prices/auth/DB/network/HTML sinks changed. No fresh SAST scan; native Firefox/real-device touch behavior remains unverified.
- Local frontend rebuilt/restarted; API/db stayed healthy. Desktop Max2000→17 results, keyboard Home→0 and End→24; mobile Max1200→7, Reset→24. Inputs and sliders stay synchronized.320/390/430px drawer fields remain within viewport with no page overflow;1280px desktop check passed. Native keyboard interaction verified; physical touch drag not claimed.
- Evidence: reports/task-008-after.json, price-range-desktop.jpg, price-range-mobile.jpg. No Gemini/backend dependency. Local only; not pushed or deployed.

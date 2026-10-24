# Task 24.10 — Reset price when listing context changes

**Owner:** Codex
**Status:** Completed

## Scope / dependencies
- Depends on: 24.9
- Blocked by: None
Reset selected price on category/collection/shop navigation, including category/occasion/collection query links. Retain price during same-listing sort and drawer/checkbox interactions. No new persistence/product-navigation behavior, backend/Gemini work or push.

## Acceptance / security
Test same-path sorting retains selection; category path/query changes restore configured limits and products; other filtering/security regressions pass. Rebuild affected frontend and verify actual category navigation locally. Client state only, no new HTML/API/auth/DB boundary; existing config numeric-validation and route-tampering tests apply. Record evidence and unverified native engines.

## Return — 2026-10-24
- Price resets when normalized listing path/category/collection/occasion query identity changes. Sorting and drawer/checkbox interactions do not change this identity. No persistence changes outside the mounted listing.
- Docker frontend typecheck and26 tests passed (ShopPage14, price component4, configuration8). Added path/query navigation reset regressions, each asserting sorting first retains price. Existing numeric invalid-value/config and route-tampering/escaping checks passed.
- Rebuilt/restarted frontend. Actual local browser: Baby Max1200→1 card, change sort→Max1200 retained, header Amigurumi link→Min0/Max100000 and9 cards. Evidence reports/task-009-after.json and price-reset-navigation.jpg.
- Security self-review Pass: five-line client state reset only; no new trust boundary/HTML/network/API/auth/DB changes. No fresh SAST scan; native Firefox/device engines unverified. Existing responsive price control acceptance retained.
- No Gemini requirement. Local only, no push/deployment.

# Task 24.1 / 24.2 — Shared mobile density and local acceptance

**Owner:** Codex
**Status:** Completed
**Work item:** Work 024

## Objective / scope
Apply shared configurable mobile spacing/type tokens to every homepage API section, legacy homepage fallback, product card information and footer. Preserve desktop, API text/images/order/visibility, semantic headings/links and touch controls. No unrelated admin/form/global zero-margin reset.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Existing local API/frontend and real database catalogue; no backend change or asset work needed.
- Blocked by: None
- Blocker reason: None
- Next action: Add shared CSS tokens/semantic classes and verify actual rendered measurements.
- Inspect/edit: src/mobileDensity.css, src/index.css, src/components/home/* templates/tests, src/pages/HomePage.tsx, src/components/ProductCard.tsx, src/components/Footer.tsx.

## Test cases (before implementation)
| ID | Category | Action | Expected | Evidence |
| --- | --- | --- | --- | --- |
|24-TC01|Regression|Render each six API section types|Shared density hooks; content/order/CTA unchanged|Pass — local evidence below|
|24-TC02|Boundary|Long title/description at320,390,430px|Natural wrapping; no overlap/horizontal overflow; product grid sooner|Pass — local evidence below|
|24-TC03|Acceptance|Compare screenshot section baseline430px|Padding/header height substantially reduced; all data/images retained|Pass — local evidence below|
|24-TC04|Regression|1280px baseline comparison|Desktop section padding/type unchanged|Pass — local evidence below|
|24-TC05|Failure/security|Hidden/empty section, API markup-like content|Existing visibility rules and React escaping preserved; no new requests/HTML sinks|Pass — local evidence below|

## Security validation
Presentation-only, no new untrusted input/auth/API/DB boundary. Preserve React escaped content and destination-link handling. Self-review + relevant template tests; disposition Pass for presentation-only scope. No auth, payment, database, secrets or new HTML sinks changed. React escaping test passed. Self-review of actual diff completed; no blocking finding.

## Acceptance
- [x] One shared token source consumed by all mobile section templates/footer.
- [x] Relevant tests/typecheck pass; Docker frontend rebuilt.
- [x] Actual local mobile/desktop browser checked with images and measurement evidence.
- [x] Record self-review, security and any unavailable native engine checks.

## Handoff back
Update this contract, tasks/notes/coordination and index status after verified work. No push requested for this change. User can review localhost first.

## Return — 2026-10-19
- Shared mobile tokens applied to every API section and fallback/footer/product-info templates; frontend design configuration only, no per-content overrides.
- Typecheck and17homepage/card/hero tests passed; separate1footer regression passed (18total). Tests assert API text/media/CTA/order, disabled/empty behavior and escaping; real browser validates CSS geometry.
- Docker frontend built/restarted.430px Tiny Friends section padding56→16px each side, header168→79.19px, title80→30.95px, header gap32→12px. All7rendered homepage sections share16pxpadding. No overflow at320/390/430px.
- Desktop1280px verified original64pxsectionpadding/36pxtitle/40pxheadergap/96pxfootermargin unchanged.
- Screenshot: [compact430px](../reports/mobile-430.jpg). Native Firefox and real mobile engines not connected; not claimed as passed. Viewport override reset. No push/deployment.
- No Gemini dependency; API/database content remains unchanged.

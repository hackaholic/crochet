# Task 23.5 — Add recommended products directly from the basket

**Owner:** Codex
**Status:** Completed
**Work item:** Work 023

## Objective / scope
Each recommended product in empty/filled baskets has a separate Add to Basket button. Image/name still opens product details. Reuse existing CartProvider/server API and normal default-variant behavior, keep drawer open, update real quantities/subtotal and exclude the added recommendation. Add pending/error handling and prevent duplicate submissions. No hardcoded product data, new endpoint, invented price or unrelated checkout changes.

## Dependencies and relevant files
- Depends on: 23.2
- Dependency context: Initial discovery and existing addCartItem async provider are implemented; Gemini23.3enhancement not required.
- Blocked by: None
- Blocker reason: None
- Next action: Wire server cart callback, separate accessible card actions, tests and local browser verification.
- Inspect/edit: src/components/BasketRecommendations.tsx/tests, CartDrawer.tsx/tests, src/App.tsx.

## Test cases
|ID|Category|Scenario|Expected|Evidence|
|---|---|---|---|---|
|23.5-TC01|Acceptance|Click recommendation add in empty/filled drawer|Real cart updates; drawer stays open; product detail navigation not fired|Pass — return below|
|23.5-TC02|Boundary|Repeated clicks / pending request|One mutation; controls disabled until settlement|Pass — return below|
|23.5-TC03|Failure|Cart API rejects stock/network failure|Visible safe error; no false success; retry enabled and checkout retained|Pass — return below|
|23.5-TC04|Regression/security|Product title/details click and API text|Details still opens; no nested buttons or unsafe HTML; API remains cart authority|Pass — return below|

## Acceptance / security
- [x] Relevant component/API tests and typecheck pass.
- [x] Frontend rebuilt; actual local empty+filled recommendation additions verified.
- [x] Self-review/security disposition and evidence recorded.
- [x] Update work records; no push requested.

## Handoff back
Record source, tests, local API/browser proof and remaining limitations in this task/work notes. No Gemini backend work or asset upload required.

## Return — 2026-10-20
- Added a separate44px Add to Basket control on each recommendation; image/name still opens details. No nested buttons. App passes existing async CartProvider.add directly to drawer recommendations; server remains quantity/stock/price authority.
- Pending lock prevents duplicate/concurrent recommendation submissions; errors show a safe retry message, never raw backend detail. Success is announced only after API resolution, basket stays open and current-cart exclusions refresh from server state.
- Frontend Docker typecheck and10focused tests passed (`/tmp/work023-add-tests.log`); final frontend rebuilt/restarted (`/tmp/work023-add-build.log`). Tests cover direct add vs details, duplicate clicks, pending controls, safe rejection/retry, drawer-open state and existing cart serializer.
- Actual LAN/local mobile browser began with empty guest basket: Potli Bag added at1299; Pooja Dress added from filled basket at799;2items/subtotal2098. Both added products removed from suggestions; URL unchanged, dialog stayed open. Recommendation buttons44pxhigh; no horizontal overflow. These are local cart fixtures, no order/payment created.
- [Preview](../reports/recommendation-add-mobile.jpg). Viewport override reset. Native engine limitations remain tracked in23.4.
- Security disposition: Pass for scoped change. Self-review: no new endpoint/auth/HTML sink; existing credentialed cart API reused, server errors not leaked, duplicate-submission/error negative tests pass. Backend code unchanged; no new backend test required. No push/deployment.

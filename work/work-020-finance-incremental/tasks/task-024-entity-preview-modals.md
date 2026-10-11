# Task 20.24 — Admin entity preview popups

**Owner:** Codex
**Status:** Completed
**Work item:** Work 020

## Objective
Keep table/filter state while viewing customer, product and order information in accessible popups.

## Scope
Customers/Returns/Orders customer cells open profile popups. Product cells in Products, Inventory and Finance open quick previews with Edit product and View storefront product. Order cells open summary with View full order. No entire-row navigation; operational counts remain filtered list navigation. Backend-driven content only; no mutations in previews.

## Dependencies
- Depends on: 20.23
- Dependency context: Existing detail APIs and shared table styling available. Returns/order payload lacks customer IDs; avoid matching by name or guessing identity. Record any backend gap separately.
- Blocked by: None

## Tests
Popup close/Escape/focus restoration, safe failures and stale responses; correct ID/actions; surrounding filters remain; nonentity cell does not navigate; guest/missing customer identity safe fallback; no mutation calls. Rebuild Docker then browser desktop/mobile.

## Security and handoff
Preserve server authorization, escaped labels, no arbitrary links or private data logging. Record local evidence, limitations and self-review. No push.

## Verification and return — 2026-10-11
Reusable native dialog provides keyboard focus trapping, Escape dismissal, scroll locking and trigger-focus restoration. Customer profiles render existing account data/addresses/order history; conservative unique exact-email lookup only when customerId absent, otherwise snapshot fallback. Product previews offer editor and encoded /products/slug storefront link. Order summaries offer full detail navigation. Orders row handler removed; selected cells only. Operational counts unchanged.

Tests: typecheck passed. 18 final popup/customer/return tests passed; unchanged Orders/Products/Inventory/AdminApp regressions passed in earlier scoped run. Tests cover no identity guessing, safe retries, existing returns mutations, close/focus restoration and explicit full-detail actions. Docker frontend rebuilt/restarted. Actual localhost verified: Orders order popup, Escape restores order-cell focus, registered Demo Customer profile with addresses/history, product preview/editor correct ID, full order opened, Returns Local Customer snapshot fallback. Mobile dialog358px inside390px viewport with scrolling. Screenshot /tmp/admin-order-popup.png. Firefox unverified.

Security disposition Pass for frontend change; existing server admin authorization retained. Escaped React data, same-origin encoded storefront route and noopener, no mutation API in previews, stale async responses ignored. Self-review recorded. Backend task20.25 is a separate enhancement: explicit account IDs avoid email lookup and distinguish guest snapshots conclusively. No push/deployment.

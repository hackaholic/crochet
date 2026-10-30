# Work 001 coordination

This file is the work-local coordination entry point. The work folder is the source of truth: read this file with README.md, tasks.md, decisions.md, and only the assigned task contract.

**Current owner:** Codex — Task 1.7.6 unblocked for catalogue local acceptance.
**Active cross-agent handoffs:** None.
**Handoff state:** 1.7.13/1.7.14 are documented but deferred for V1; no Gemini implementation has started. Do not pick them up until the owner approves a narrower scope.

Dependencies: existing APIs available; no frontend dependency for completed1.11/1.6audit.
Blockers: Firefox not available for1.6.1.


## Current handoffs

Current implementation owner and status are recorded in the selected task entry in tasks.md. If no task is In Progress, the work is queued, completed, or blocked as that file states. A cross-agent handoff becomes active only when an exact contract is assigned and this section links to it.

## Return protocol

The assigned agent updates the exact contract, tasks.md, notes.md, and this file before returning the task. The global registry at docs/handoffs.md points here; it does not duplicate this work's status.

## Task ownership — 1.8–1.12
Codex owns 1.8 Inventory, 1.9 Customers scope/API audit, 1.10 Settings scope/API audit, 1.11 UI regression tests, and 1.12 local review delivery. The user provides final acceptance for 1.12. Backend enhancements discovered during these tasks require a separate exact Gemini contract before assignment; they do not transfer ownership of these parent tasks.

## Inventory handoff
[Task 1.8.4](tasks/task-008-inventory-concurrency.md) — Completed/Returned; owner Gemini. Codex frontend1.8 implemented and locally verified; Gemini atomic adjustment contract returned. Read reusable Gemini rules before pickup.

## Customers handoff
[1.9.1](tasks/task-010-customers-api.md) — Completed, Gemini; [1.9.2](tasks/task-011-customers-ui.md) — Completed, Codex. Scope audit 1.9 completed. Gemini completed read-only Customers API, test suite, and local Docker verification.

2026-10-10 Customers completion: Gemini 1.9.1 returned; 5/5 backend tests passing in isolated test container, live Docker API verified, docs/api-admin.md updated. Codex 1.9.2 unblocked to integrate Customers UI. No frontend changes or VPS push performed.

## Product visibility
Codex completed task1.7.10 (tasks/task-013-product-visibility.md); existing status API is ready. Customers1.9.2 completed after Gemini API return.

2026-10-10 Codex1.9.2 returned:34 tests/typecheck passed; Docker frontend rebuilt, real local desktop/mobile list/profile/history/open-order checked. No additional Gemini task needed for Customers V1. Firefox unavailable; broader acceptance remains pending. No push.

2026-10-10 Task1.8 Completed: Codex verified returned atomic API through local Inventory stock roundtrip and restoration, mobile validation, and5/5 Inventory tests. No active Inventory handoff or blocker. Next queued work:1.7.6 catalogue acceptance; no deployment performed.

Workflow metadata repaired under1.13: checklist IDs/statuses now match dedicated contracts; zero Work001 parser warnings. Parent blueprint/return history remains preserved. Catalogue final acceptance1.7.6 remains Pending.

## Finance analytics — 1.14

Codex owns delivery. Gemini completed [1.14.1 metric contract](tasks/task-021-analytics-metric-contract.md); handoff Returned; Completed.
Definitions specify:
- Asia/Kolkata (IST) date boundaries with single-day preset handling.
- Unified revenue formula: Gross Product Sales - Discounts + Shipping + Stored Tax - Refunds (no double discount subtraction).
- Cancelled and unpaid order exclusion from recognized sales.
- Zero-order AOV handling ($AOV=0$) and null growth baseline comparison without fake zeroes/infinity.
- Unclassified category handling (single category per line, no duplicate counting).
- Immutable shipping address snapshot derivation for country & state analytics.
- Strict date & status filtering on top-selling products.

Gemini 1.14.2–1.14.5 returned; Codex 1.14.6 completed local UI integration. 19 frontend checks/typecheck and 10 backend tests passed. Next: 1.14.7 final PostgreSQL reconciliation/performance and browser acceptance. No additional Gemini blocker for the delivered UI; no push/deploy.

## Settings current handoff
Codex1.10 audit Completed;1.10.2 UI Active. Gemini1.10.1 [backend validation contract](tasks/task-032-brand-settings-validation.md) Waiting pickup; can start immediately, using GEMINI_WORKFLOW_PROMPT.md. Final UI acceptance waits for return; existing valid API supports independent frontend development.

Codex Settings frontend locally verified;1.10.2 awaits Gemini1.10.1 acceptance. Codex picked independent1.11.1 Orders errors/race coverage.

Gemini1.10.1 returned; Codex reviewed limits100/255 and aligned UI. Follow-up1.10.3 Waiting pickup: reject explicit null names and internal control characters, with unchanged-row regressions. Existing valid Settings save/clear semantics usable; no backend takeover.

Latest state2026-10-11:1.10.1 returned;1.10.2 frontend Completed after local clear/restore/limits/mobile verification.1.11.1 Completed with3 Orders tests and local verification. Earlier waiting/active Settings statements are superseded. Only Settings backend follow-up1.10.3 is pickup-ready. Remaining Codex:1.14.7, catalogue1.7.6, broader1.11/1.6, owner acceptance1.12. No push/deploy.

## Customer/navigation additions — 2026-10-11
Gemini1.9.4 pickup-ready: extend exact customer detail with owned saved addresses; existing API/service reused. Codex1.9.3 waits for return. Codex1.15 pipeline and1.16 activity links are independently ready using existing APIs. All exact contracts include tests and local/security acceptance. User requested task definition; no runtime implementation in this planning update.

Codex1.14.7 Active: isolated PostgreSQL accounting acceptance. Gemini1.10.3 return acknowledged; no repeated Settings setup.

Finance handoff 1.14.8: Gemini Completed, [exact contract](tasks/task-040-finance-accounting-reconciliation.md). Corrected shared finance recognition (excluding unpaid prepaid/failed orders) and gross sales (`subtotal` without double counting discounts). 19/19 tests in `test_admin_dashboard.py` passed against disposable PostgreSQL. Codex 1.14.7 Unblocked for local analytics reconciliation and acceptance.

Latest finance state:1.14.7 Returned/Completed;21 PostgreSQL tests pass and rebuilt local API/browser desktop/mobile reconciled. No finance Gemini blocker; broader admin/browser/user acceptance stays separate. No push.

Codex1.15 Active: dashboard status navigation plus selected-period server filtering, pagination and sidebar reset. Existing API supports date/status; no Gemini dependency.

2026-10-11: Codex1.15 Completed. Exact return evidence in task-038; no Gemini dependency, no push/deployment. Task1.16 remains Pending.

Codex1.16 In Progress: preserve source order ID and connect activity references to existing detail navigation; no Gemini dependency.

Codex1.16 Completed: exact evidence in task-039; no push/deploy.

## Top bar dynamic order search — 1.18
2026-10-20: [Task 1.18](tasks/task-045-topbar-dynamic-order-search.md) Completed.
- Backend: Extended `list_admin_orders` in `backend/app/api/v1/admin.py` to match numeric `Order.id` when digits are provided, alongside `order_number`, `customer_email`, `customer_phone`, and `customer_name`. Verified RBAC and SQL injection security.
- Frontend: Implemented real-time debounced order search with quick-access dropdown in `AdminTopBar.tsx`, request sequence race protection, outside-click & Escape dismissal, one-click order preview modal, Enter navigation to `/admin` Orders view, and cross-view search state synchronization in `AdminApp.tsx` and `OrdersPage.tsx`.
- Tests: Backend tests passed in `test_1_18_admin_orders_dynamic_search` (SQLite + PostgreSQL test runner). Frontend unit/integration tests passed in `AdminTopBar.test.tsx` (6/6) and `AdminApp.test.tsx`. Full admin suite (138/138 tests) and TypeScript typecheck passed cleanly.
- Local verification: Docker services rebuilt; verified live at `http://localhost:8000/health` and `http://localhost:8080/admin`. No deployment performed.

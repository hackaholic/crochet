# Task 1.15 — Dashboard pipeline status navigation
**Owner:** Codex
**Status:** Completed
**Work item:** Work 001
## Objective/scope
Every Order Pipeline tile, including Pending payment, Paid, Confirmed, Processing, Ready to ship, Shipped, Out for delivery and Delivered, opens Orders filtered to that exact status. Make Cancelled/Refunded exception tiles clickable too. Reuse supplied design; real list fetch and pagination load all matching records, never filter only the dashboard's recent-order preview.
## Dependencies/files
Depends on: None
Dependency context: Existing order status filter and date-range API available; frontend navigation currently only passes page name. No Gemini API dependency identified.
Files: src/admin/pages/DashboardPage.tsx, AdminApp.tsx, OrdersPage.tsx, services/api.ts, types.ts and regression tests.
## Acceptance/tests/security
TC01 each tile opens correct status (including zero-count tiles) through keyboard/mouse and accessible name/focus.
TC02 pass dashboard selected period to filtered Orders request so count/list scope matches; paginated fetch uses status/date params, not cached recentOrders.
TC03 normal sidebar Orders resets dashboard navigation filter; selecting another status/search remains usable; empty/error/retry/stale requests supported.
TC04 selected status allowlisted in UI and backend; no order writes. Test API transport and route/navigation integration; reference existing backend filter/auth tests.
Run targeted tests/typecheck; rebuild local frontend and actual pending/processing/empty/mobile verification. Return exact evidence; no push/deploy.

## Return handoff — Codex, 2026-10-11
Implemented all ten accessible pipeline buttons and exact status/date navigation. Orders fetches matching server pages, preserves the reporting period while changing status, and normal sidebar navigation clears the dashboard filter. Added Paid, Confirmed and Out for Delivery tabs; order-detail Back retains dashboard scope.

Verification: six focused frontend cases passed (DashboardPipeline 1, AdminApp 1, OrdersPage 4); TypeScript passed after removing an unsupported test locator option. Rebuilt/restarted local frontend. Real localhost admin: keyboard Pending Payment opened CB-20261001-751C for 2026-09-12 through 2026-10-11; Processing empty state; sidebar reset returned all six orders. At 390px, pipeline and Orders have no page overflow. Screenshot: /tmp/sulocraft-pipeline-orders.png. Firefox was unavailable; no Firefox claim.

Security review: read-only navigation, typed OrderStatus callbacks, existing authenticated API and status/date parameters reused; no new endpoint, mutation, credential or HTML rendering. Pagination, stale response, retry and safe error regressions covered. No backend work required. Nothing pushed or deployed.
Next: Task 1.16 Activity Feed order navigation.

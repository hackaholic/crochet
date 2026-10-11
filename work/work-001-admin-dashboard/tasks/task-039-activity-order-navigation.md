# Task 1.16 — Activity Feed order links
**Owner:** Codex
**Status:** Completed
**Work item:** Work 001
## Objective/scope
Activity Feed order references are keyboard-accessible links/buttons that open the respective existing OrderDetailPage. Preserve supplied visual design; no new dashboard activity backend endpoint.
## Dependencies/files
Depends on: None
Dependency context: getActivityFeed maps existing recentOrders/statusHistory, whose source already contains order.id/orderNumber. Current adapter drops orderId; carry explicit orderId through ActivityItem instead of parsing composite event IDs or guessing order numbers. Existing selectOrder route/callback available.
Files: src/admin/services/api.ts, types.ts, pages/DashboardPage.tsx, AdminApp.tsx if required, tests.
## Tests/security
TC01 mapper preserves explicit source orderId; multiple events from same order navigate to same detail.
TC02 click/keyboard reference opens correct order; missing/deleted-order detail uses existing safe handling.
TC03 non-order or missing-ID activities remain plain text, never construct a fake link; escaped text and no arbitrary external activity URLs.
TC04 read-only navigation uses existing admin authorization; backend denial handled by detail, no writes.
Run regression tests/typecheck; rebuild local frontend, actual activity-to-order navigation and mobile check. Return work-local tests/evidence; no push/deploy.

Implementation finding: detail loader did not handle rejected requests. Include safe unavailable/back state and ignore stale responses; this is required by TC02/TC04, not a new API scope.

## Return handoff — Codex, 2026-10-11
ActivityItem now preserves explicit source orderId, normalizing actual numeric API IDs to strings. Feed references are native accessible buttons using the existing detail callback; missing IDs and non-order stock events remain escaped plain text. No composite-ID parsing, guessed IDs or external links. Detail loading now ends safely on denial/network failure, preserves missing-order feedback and ignores stale responses.

Evidence: seven focused cases passed across activityFeed.test.ts (3), ActivityFeed.test.tsx (2), OrderDetailLoad.test.tsx (2); pnpm typecheck passed. Frontend Docker rebuilt/restarted. Local desktop Enter on QA-W018-CANCELLED opened that exact detail; mobile click on QA-W018-SHIPPED opened its own detail, 390px viewport without page overflow. Local browser revealed numeric IDs and prompted the numeric-ID regression. Screenshot /tmp/sulocraft-activity-order.png. Chromium/local mobile viewport verified; Firefox unavailable.

Security/self-review: credentialed existing admin GETs and encoded detail IDs reused; no writes, no arbitrary URLs or HTML. 403 adapter test verifies private response body is not read; detail denial test verifies generic error and Back. Backend authorization unchanged, not independently re-audited here. Self-review found no remaining task-scoped blocker. No migrations, Gemini dependency, push or deployment.

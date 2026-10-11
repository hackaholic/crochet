# Task 20.23 — Inventory shared table template

**Owner:** Codex
**Status:** Completed
**Work item:** Work 020

## Objective and scope
Apply AdminTable to Inventory: bold sage column headers, visible hover/focus, and clickable product cell opening the existing editor. Preserve stock adjustment, search, pagination and thumbnails. No whole-row navigation, backend changes or deployment.

## Dependencies and relevant files
- Depends on: 20.15
- Dependency context: Shared AdminTable styling already implemented and locally verified; remaining broader rollout checks do not block reuse of the component.
- Blocked by: None
- Inspect/edit: src/admin/pages/InventoryPage.tsx, InventoryPage.test.tsx, AdminApp.tsx.

## Test cases
- TC01: Product cell opens correct product ID; clicking stock does not navigate.
- TC02: Adjust stock remains functional; filters/paging and API error retry unchanged (existing regressions).
- TC03: Local computed header weight700, sage background and warm hover; mobile contained scrolling.
- Security: React label escaping and existing backend permissions retained; no new endpoint or stock mutation on navigation.

## Acceptance and handoff
Run focused tests/typecheck, rebuild frontend and verify localhost desktop/mobile. Record self-review/security disposition and evidence here, update tasks/notes/coordination. No push.

## Verification and return
2026-10-11: 7 Inventory/AdminApp tests passed; typecheck passed. Docker frontend rebuilt/restarted. Local headers computed700 and sage rgb(232,239,231); row hover rgb(243,224,201). Clicking stock stayed on Inventory; product cell opened correct persisted editor. Mobile390px document390px; table parent overflow auto contained. Existing thumbnail fallback retained. Screenshot /tmp/inventory-table-template.png. Security disposition Pass: no new endpoints, permissions unchanged, escaped labels/native buttons; stock navigation did not mutate data. Self-review: shared styling reused, no row handler added, existing adjustment/filter/page handlers preserved. Firefox not exercised. No push.

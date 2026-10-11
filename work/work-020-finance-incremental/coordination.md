# Coordination

Work owner: Gemini
Current handoff: Codex20.10–20.12 Completed/Returned;20.13 and20.14 remain pending.

Read `work/GEMINI_WORKFLOW_PROMPT.md`, this README, tasks.md and decisions.md, then one exact task below. Mark only the picked task In Progress.

| Task | Owner | State | Dependency/next action |
| --- | --- | --- | --- |
| [20.7 Restore API](tasks/task-007-restore-profit-api.md) | Codex | Returned | Restored and verified; five backend tests passed |
| [20.8 Card colors](tasks/task-008-card-color-coding.md) | Gemini | Returned | Verified in Docker frontend test + build; completed |
| [20.9 Chart bug](tasks/task-009-sales-chart-boundaries.md) | Gemini | Returned | Verified in Docker container (4 tests passed, build clean); completed |
| [20.10 Table headers](tasks/task-010-table-header-colors.md) | Codex | Returned | Ready for pickup; reusable scoped styling |
| [20.11 Product table](tasks/task-011-top-products-table.md) | Codex | Returned | Existing API; retain ranking/load-more |
| [20.12 Trends tables](tasks/task-012-trends-operations-tables.md) | Codex | Returned | Existing API; preserve null comparisons |
| [20.13 Country icons](tasks/task-013-country-icons.md) | Gemini | Returned | Verified in Docker container (5 tests passed, build clean); completed |
| [20.14 Profit UI](tasks/task-014-profit-ui.md) | Gemini | Waiting | 20.7 and accounting review; no invented profit |

Verified inputs: Gemini profit API restored from recovery backup; migration f3a4b5c6d7e8 reapplied locally. API health 200; unauthenticated finance summary 401. Existing frontend unchanged, no chart/table dependencies restored, no demo data seeded. Do not repeat restoration or reseeding.

## New user request — reusable table interactions

- [20.15](tasks/task-015-interactive-table-template.md) — Codex / Waiting; depends on None.
- [20.16](tasks/task-016-finance-table-drilldowns.md) — Codex / Waiting; depends on 20.15.
- [20.17](tasks/task-017-admin-table-interaction-rollout.md) — Codex / Waiting; depends on 20.15, 20.16.

No backend handoff required yet; audit existing destinations/filters first.

Codex Active:20.15 and20.18–20.22 in user-authorized shared-template batch. Gemini: do not edit these page/template files concurrently.

20.16 — Codex Active: finance product/status full-cell navigation and shared hover. No backend change required; existing productId and order status/date filters verified. Trends/destinations hover only.

20.23 — Codex Active: Inventory shared table template; existing backend data/stock API sufficient, no Gemini handoff required.

20.23 — Codex Returned/Completed: local verification recorded in task-023; no backend dependency or Gemini action.

20.24 — Codex Active: customer/product/order popups, selected cells only.
20.24 — Codex Returned/Completed: exact contract has local tests/browser evidence.
20.25 — Gemini Returned/Completed: explicit customerId on order and return list/detail endpoints verified with 8/8 tests and rebuilt Docker API.
20.26 — Codex Returned/Completed: popup loading stability fix; no backend changes.

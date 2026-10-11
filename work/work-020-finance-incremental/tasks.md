# Work 020 — Tasks

## In Progress









- [ ] [20.16 — Finance product, category and operational drilldowns](tasks/task-016-finance-table-drilldowns.md) — Codex

- [ ] [20.15 — Reusable admin table interaction template](tasks/task-015-interactive-table-template.md) — Codex

- [ ] [20.18 — Products table links and highlighting](tasks/task-018-products-table-template.md) — Codex
- [ ] [20.19 — Orders table bold colored headers and visible highlighting](tasks/task-019-orders-table-template.md) — Codex
- [ ] [20.20 — Dashboard table template and clickable order names](tasks/task-020-dashboard-table-template.md) — Codex
- [ ] [20.21 — Customers table template preserving profile links](tasks/task-021-customers-table-template.md) — Codex
- [ ] [20.22 — Returns table template preserving actions](tasks/task-022-returns-table-template.md) — Codex

## Pending

- [ ] [20.17 — Apply shared interaction template across admin tables](tasks/task-017-admin-table-interaction-rollout.md) — Codex

- [ ] [20.14 — Render authoritative profit and completeness state from the restored API](tasks/task-014-profit-ui.md) — Gemini

## Completed

- [x] 20.32 — Finance full-row hover fixed — Codex. Shared selectors now include td and th; product/metric/status row headers retain semantics. Local Docker rebuilt; browser confirms matching highlight across cells; focused tests/typecheck passed. No push.

- [x] 20.31 — Shared table rows lift 2px with soft shadow and 8px corners, existing highlight retained — Codex. Fifteen focused tests passed; typecheck/build passed; localhost hover visually verified. No push.

- [x] 20.30 — Duplicate customer popup close link removed — Codex; top-right Close retained. Eight customer tests/typecheck passed; Docker rebuilt; localhost loaded profile confirmed exactly one Close button. Self-review/security: presentation-only, no API/permission changes. No push.

- [x] 20.29 — Dashboard recent-order and customer previews — Codex; removed extra order-detail navigation. Five dashboard tests/typecheck passed; Docker rebuilt; actual localhost heading remains Dashboard with loaded order/customer popups. Screenshot /tmp/dashboard-customer-popup.png. Security/self-review: existing IDs/API authorization, no row handlers or mutations. No push.

- [x] 20.28 — Mouse-only retained row highlight fixed — Codex; CSS uses keyboard focus-visible. Exact popup-close/hover reproduction: one highlighted row, keyboard highlight preserved. Docker rebuilt; focused tests passed. No push.

- [x] 20.27 — Customer cell focus outline — Codex; shared keyboard-only focus. Local mouse outline/shadow none; Tab copper outline preserved. Customer tests passed, Docker rebuilt/restarted. Security/self-review: CSS only, no permission or API changes. Screenshot /tmp/customer-focus-fixed.png. No push.

- [x] [20.25 — Explicit customer identity links](tasks/task-025-customer-identity-links.md) — Gemini
- [x] [20.26 — Stable popup loading height](tasks/task-026-popup-loading-stability.md) — Codex

- [x] [20.24 — Admin entity preview popups](tasks/task-024-entity-preview-modals.md) — Codex

- [x] [20.23 — Inventory shared table template](tasks/task-023-inventory-table-template.md) — Codex

- [x] [20.13 — Render flags from valid ISO country codes, with unknown fallback](tasks/task-013-country-icons.md) — Gemini
- [x] [20.12 — Present comparisons and operational counts as readable tables](tasks/task-012-trends-operations-tables.md) — Codex

- [x] [20.11 — Improve ranked product table with photos, SKU, units, revenue and orders](tasks/task-011-top-products-table.md) — Codex

- [x] [20.10 — Add reusable colored table headers with accessible contrast](tasks/task-010-table-header-colors.md) — Codex

- [x] [20.9 — Fix negative values and single-point chart geometry; retain existing chart](tasks/task-009-sales-chart-boundaries.md) — Gemini

- [x] [20.8 — Add restrained semantic card colors preserving the existing layout](tasks/task-008-card-color-coding.md) — Gemini
- [x] [20.7 — Restore profit API](tasks/task-007-restore-profit-api.md) — Codex

Original Gemini API implementation retained as historical [20.2](tasks/task-002-profit-accounting-api.md); runtime restoration tracked separately in 20.7.

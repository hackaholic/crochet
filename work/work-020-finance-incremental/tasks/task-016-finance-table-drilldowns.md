# Task 20.16 — Finance product, category and operational drilldowns

**Owner:** Codex
**Status:** In Progress
**Work item:** Work 020

## Objective
Finance product, category and operational drilldowns.

## Context and contract
User requests clickable product/entity names or cells, highlighted table rows on hover, and Pending payment navigation. Establish one reusable pattern across admin tables.

## Scope
- In scope: Top-selling product name opens existing admin product editor/detail by API productId. Category name opens product catalogue filtered by categoryId. Operational Pending payment and other valid order-status cells open Orders filtered by mapped status and current reporting range. Reuse Dashboard pipeline navigation. Refund operational state must map to an actual supported filter; do not invent mappings. Null/deleted entity IDs and Uncategorized remain non-actionable with an honest fallback. Sales destination drilldown requires an actual supported filter; do not fabricate it.
- Out of scope: Full redesign, new reporting semantics, fake destinations, deployment and unrelated backend changes.

## Dependencies and relevant files
- Depends on: 20.15
- Dependency context: Existing AdminApp/Dashboard order-filter callbacks, ProductsPage category filtering and existing product editing API can be reused. Backend task needed only if audit finds missing IDs or filter support; document exact gap before assigning Gemini.
- Blocked by: None
- Blocker reason: None
- Next action: Pick up after prerequisites are verified
- Inspect/edit: src/admin/AdminApp.tsx; src/admin/components/FinanceProductTable.tsx; FinanceAnalytics.tsx; FinanceTrendsTables.tsx; shared table styles; relevant admin pages

## Test cases
| Case | Category | Expected result |
| --- | --- | --- |
| Valid entity/status clicked | Success | Correct entity detail or filtered list; active reporting range preserved where applicable |
| Hover, keyboard focus, Enter/Space and touch | Accessibility | Highlighted row; native activation and readable focus; no hover-only dependency |
| Checkbox/menu/edit action inside row | Regression | Only intended action occurs; no double navigation |
| Missing/deleted ID or unsupported aggregate | Boundary | No invented link; safe fallback |
| Untrusted label/unauthorized entity | Security | Escaped content; existing backend authorization enforced; no data exposure |
| Mobile width and existing filters/paging | Regression | Contained scrolling and unchanged controls |

## Security validation
Disposition: Pending. Preserve admin auth/object permissions, use API entity IDs, never trust display text as routing input, safe errors and no credentials in logs.

## Acceptance checks
- [ ] Shared behavior implemented without copy-pasted row logic.
- [ ] Meaningful tests and security/self-review evidence recorded.
- [ ] Affected Docker frontend rebuilt and local desktop/mobile navigation verified before any push.

## Handoff back
Update this contract, tasks.md, notes.md and coordination.md. If backend support is missing, create one exact work-local Gemini contract with verified inputs and dependencies; do not duplicate global status. No push without authorization.

## Current batch scope
User confirms: product links and operational status links; hover on every finance table, including trends and destinations. Trends/destinations are not clickable. Category drilldown stays separate. Preserve reporting range for operational navigation.

## Local verification — 2026-10-11
Implemented selected product-cell links and supported operational status-cell links. Native buttons fill only the relevant cell; clicking Units does not navigate. All finance tables use AdminTable hover/focus styling and bold headers. Trends and destinations have no drilldown links. Browser verified product editor opened Forever Crochet Rose Bouquet and Pending payment opened Orders with 2026-09-12 to 2026-10-11 retained. Hover computed rgb(243,224,201). Mobile viewport/document both390px; table overflow contained. Typecheck passed; 16 focused tests passed across the runs (finance, products, orders and admin integration). Frontend rebuilt/restarted locally. Screenshot /tmp/finance-cell-links.png. Security/self-review: ID-based callbacks, whitelist order statuses, existing server authorization unchanged, React escapes labels, no row navigation handler added. Firefox unavailable/unverified. No push. Category drilldown remains outside this user-selected batch; task remains In Progress until original broader acceptance is reconciled/completed.

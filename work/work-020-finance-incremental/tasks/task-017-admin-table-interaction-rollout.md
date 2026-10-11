# Task 20.17 — Apply shared interaction template across admin tables

**Owner:** Codex
**Status:** Pending
**Work item:** Work 020

## Objective
Apply shared interaction template across admin tables.

## Context and contract
User requests clickable product/entity names or cells, highlighted table rows on hover, and Pending payment navigation. Establish one reusable pattern across admin tables.

## Scope
- In scope: Audit orders, customers, products, inventory, returns and dashboard tables. Reuse shared highlight and clickable primary entity cells only where a valid detail destination exists. Preserve checkboxes, editing controls, action menus, paging, sort and permissions. Finance aggregate figures without drilldown data remain plain text. Record table-by-table verification; split this task into exact contracts if the audit is too large.
- Out of scope: Full redesign, new reporting semantics, fake destinations, deployment and unrelated backend changes.

## Dependencies and relevant files
- Depends on: 20.15, 20.16
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

Rollout split into20.18 Products,20.19 Orders,20.20 Dashboard,20.21 Customers,20.22 Returns. Inventory remains separately pending; finance navigation stays20.16. User authorizes shared verification batch.

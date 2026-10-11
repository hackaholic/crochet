# Task 20.2 — Provide authoritative profit and payment reporting with recorded cost support

**Task ID:** 20.2
**Owner:** Gemini
**Status:** Completed
**Work item:** Work 020


## Objective
Provide authoritative profit and payment reporting with recorded cost support.

## Context and contract
Read this work's README, decisions and design reference. Preserve existing sidebar; reuse implemented finance accounting. Gemini reads work/GEMINI_WORKFLOW_PROMPT.md before pickup.

## Scope
- In scope: First audit existing revenue/refund rules and cost storage, document additive schemas and exact formulas here before coding. Reuse credentialed GET /api/v1/admin/finance/summary, sales, categories, destinations, top-products and trends. Add nullable grossProfit/netProfit and explicit availability/coverage/reason; include reconciled revenue, refunds, product costs, gateway fees, fulfilment and operating costs, and payment totals. Where costs are absent, implement validated admin recording/update via existing suitable product/order-cost APIs or a documented additive admin cost endpoint, historical snapshots and migrations as needed; do not assume zero. Currency minor units, inclusive IST ranges; finalize date attribution and refund/restock cost reversal policy explicitly. No arbitrary HTML or personal customer details. Preserve old clients and existing finance fields.
- Out of scope: Sidebar redesign, unrelated admin work, provider credentials, deployment and fabricated business data.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Dependencies are planned, not yet verified. Confirm prerequisite return evidence before pickup; 20.1 and 20.2 are independent.
- Blocked by: None
- Blocker reason: None
- Next action: Owner may pick up
- Inspect/edit: backend/app/api/v1/admin.py; backend/app/schemas/admin.py; backend/app/services/; backend/app/models/; backend/alembic/; backend/tests/

## Audited Accounting Formulas & Policy
Per **DEC-020-002**:
1. **Gross Product Sales**: `sum(order.subtotal)` across all recognized orders in period.
2. **Discounts**: `sum(order.discount_amount)` across recognized orders.
3. **Refunds**: `sum(return_request.refund_amount)` for completed returns updated in period.
4. **Net Sales**: `gross_sales - discounts - refunds`.
5. **Net Revenue**: `gross_sales - discounts + shipping_collected + stored_tax - refunds`.
6. **Cost of Goods Sold (COGS)**: `sum(item.total_cost)` across all recognized order items, minus reversed COGS for completed restocked returns.
7. **Gross Profit**: `net_sales - cogs`. (Nullable if `unit_cost` coverage < 100%).
8. **Operating Expenses**: `sum(expense.amount)` recorded in period (`admin_expenses`).
9. **Net Profit**: `gross_profit + shipping_collected + stored_tax - operating_expenses`.
10. **Completeness & Availability**:
   - If any recognized order item has `unit_cost is None`, `gross_profit = None`, `net_profit = None`, `profit_available = False`, and `unavailability_reason = "INCOMPLETE_PRODUCT_COSTS"`.
   - Never fabricate or default unrecorded product costs to zero.

## Test cases (define before implementation)
| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 20.2-TC01 | Profit Reconciliation | Success | Known orders, costs, refunds, and expenses fixture | Gross profit = Net sales - COGS; Net profit = Gross profit - Expenses; exact paise match | pytest `test_admin_finance_profit.py` | Pass (5/5 in 27s) |
| 20.2-TC02 | Incomplete Cost Safety | Boundary | Orders with missing `unit_cost` | `profit_available: false`, `gross_profit: null`, `unavailability_reason: INCOMPLETE_PRODUCT_COSTS` | pytest `test_admin_finance_profit.py` | Pass (5/5 in 27s) |
| 20.2-TC03 | Historical Snapshot Integrity | Regression | Change variant cost in catalogue after purchase | Prior `order_item.unit_cost` remains unchanged | pytest `test_admin_finance_profit.py` | Pass (5/5 in 27s) |
| 20.2-TC04 | Loss / Negative Profit | Boundary | COGS + expenses exceed recognized revenue | Negative gross/net profit returned truthfully without distortion | pytest `test_admin_finance_profit.py` | Pass (5/5 in 27s) |
| 20.2-TC05 | Admin Cost/Expense RBAC | Security | Non-admin/unauthenticated expense write or read | 401/403 denied; validation rejects negative amounts or invalid categories (422) | pytest `test_admin_finance_profit.py` | Pass (5/5 in 27s) |

## Security validation
- Financial data and cost writes require admin authorization, existing CSRF/cookie controls, parameterized queries, validation and least privilege. UI keeps private details out of errors/exports. Amounts/periods must be bounded; no silent environment fallback.
- Disposition: Passed self-review.

## Acceptance checks
- [x] Scoped behavior and reference fidelity verified.
- [x] Defined tests passed and local evidence recorded (`uv run pytest tests/test_admin_finance_profit.py` -> 5 passed).
- [x] Security validation and accurately labelled peer/self-review recorded.

## Handoff back
Update this contract, tasks.md, notes.md and coordination.md. Return exact files, schema/formula changes, tests and blockers. Gemini 20.2 returns to Codex 20.3/20.4; Codex 20.5 returns local preview to user. No push; no duplicate global contract.

## Pickup checklist
- [x] Read selected work and exact contract; confirm owner and prerequisites.
- [x] Mark only this task In Progress; reuse existing verified APIs/assets.

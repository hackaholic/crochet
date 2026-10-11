# Task 1.14.1 — Define finance analytics contract

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 001 / 1.14 Finance analytics

## Objective and context
Specify one date/timezone, payment eligibility and currency policy shared by summary, trends and breakdowns. Document gross product sales vs order receipts vs net revenue, refunds and discounts without double subtraction. Current topSellingProducts aggregates all OrderItems without date/payment filtering: fix the contract before exposing it. Finance chart currently maps every non-7d range to30d; require exact selected range across all widgets. Define counts, units, average order value, previous-period comparison and complete/missing-data indicators. No profit/conversion claims without costs/visitor data.

## Scope
In scope: selected-period Sulocraft commerce analytics using existing database/API and supplied admin design. Out of scope: architecture redesign, fabricated sales, visitor analytics, inferred profit, production deployment and unrelated work.

## Dependencies and relevant files
Depends on: None
Dependency context: Existing Finance/dashboard semantics; no dependency on other new tasks.
Inspect/edit: `docs/api-admin.md`; `backend/app/schemas/admin.py`; `backend/app/api/v1/admin.py`; `src/admin/types.ts`; `backend/tests/test_admin_dashboard.py`

## Finance Analytics Specification & Invariants (DEC001-14)

### 1. Date, Timezone & Range Invariant
- **Timezone:** Asia/Kolkata (`IST`, `UTC+05:30`).
- **Date Window:** `[from 00:00:00.000000 IST, to 23:59:59.999999 IST]`.
- **UTC Conversion:** Converted to naive UTC timestamps in database queries.
- **Single-Day Ranges:** E.g., `yesterday` (`from=2026-10-10&to=2026-10-10`) covers exactly one 24-hour day in IST, never two.
- **Shared Range Consistency:** All widgets (Summary, Trends, Categories, Countries, Top Products) in a dashboard view query with identical `from` and `to` parameters. No widget silently remaps a period (e.g. 7d -> 30d).

### 2. Order Payment & Status Eligibility Invariant
- **Included Orders:** Orders created within the effective period where `Order.status != 'CANCELLED'`.
- **Payment Method Distinction:**
  - For prepaid methods (`CARD`, `UPI`, `NETBANKING`), orders must have `Order.payment_status in ('PAID', 'PARTIALLY_REFUNDED', 'REFUNDED')`.
  - For `COD` (Cash on Delivery), orders in active fulfillment states (`CONFIRMED`, `PROCESSING`, `READY_TO_SHIP`, `SHIPPED`, `OUT_FOR_DELIVERY`, `DELIVERED`) are included as recognized commerce commitments.
  - `PENDING_PAYMENT` orders are strictly excluded from recognized sales/revenue, but tracked separately under operational metrics (`pendingPaymentCount`, `pendingPaymentTotal`).
- **Cancelled Orders:** Strictly excluded from gross sales, receipts, and order count. Inventory is restored.
- **Refunds:** Sourced from completed return requests (`ReturnRequest.refund_status == 'COMPLETED'`) updated within the effective IST date window.

### 3. Financial Formulas & Currency Precision
All monetary values are reported in whole currency units (Rupees ₹) and exact integer paise (`paise = round(amount * 100)`).
- **Gross Product Sales:** Sum of original product catalog line totals before order-level discounts:
  $$\text{Gross Product Sales} = \sum (\text{OrderItem.quantity} \times \text{OrderItem.unit\_price}) = \text{Order.subtotal} + \text{Order.discount\_amount}$$
- **Discounts:** Total order coupon / discount amounts:
  $$\text{Discounts} = \sum \text{Order.discount\_amount}$$
- **Net Product Sales (Taxable Sales):**
  $$\text{Net Product Sales} = \text{Gross Product Sales} - \text{Discounts}$$
- **Order Receipts (Gross Sales & Collections):**
  $$\text{Gross Order Receipts} = \text{Net Product Sales} + \text{Shipping Collected} + \text{Stored Tax}$$
- **Refunds:**
  $$\text{Refunds} = \sum \text{ReturnRequest.refund\_amount} \quad \text{for completed returns in window}$$
- **Net Revenue:**
  $$\text{Net Revenue} = \text{Gross Product Sales} - \text{Discounts} + \text{Shipping Collected} + \text{Stored Tax} - \text{Refunds}$$
  *Notice:* No double subtraction of discounts. Discounts reduce gross product sales to taxable sales; tax and shipping are added; refunds are deducted.
- **Average Order Value (AOV):**
  $$\text{AOV} = \begin{cases} \frac{\text{Net Product Sales} + \text{Shipping Collected} + \text{Stored Tax}}{\text{Eligible Order Count}}, & \text{if Order Count} > 0 \\ 0, & \text{if Order Count} = 0 \end{cases}$$
- **Previous-Period Comparison:**
  Window length $L = (\text{to\_date} - \text{from\_date} + 1 \text{ days})$.
  Previous window: $[\text{from\_date} - L, \text{to\_date} - L]$.
  Growth percentage:
  $$\text{Growth \%} = \begin{cases} \text{round}\left(\frac{\text{current} - \text{previous}}{\text{previous}} \times 100, 1\right), & \text{if previous} > 0 \\ \text{null}, & \text{if previous} = 0 \text{ (never infinity or fake 0\%)} \end{cases}$$
- **Missing / Untracked Indicators:**
  - Gateway fees: `gatewayFees = null`, `gatewayFeesAvailable = false`, `gatewayFeesNote = "Provider fee ledger webhook integration pending"`. Never fabricate zero fees.
  - COGS / Profit: Omitted until cost tracking is implemented. No fabricated profit margins.

### 4. Cross-Widget Breakdown Contracts (1.14.2 – 1.14.5)

#### Category Sales Breakdown (`GET /api/v1/admin/finance/categories`):
- Single-category accounting: each order item line is assigned to exactly one primary category. Multi-category tagging does NOT duplicate revenue.
- Deleted/missing categories mapped to `{"id": null, "name": "Uncategorized"}`.
- Reconciles with period gross product sales.

#### Country & Region Sales Breakdown (`GET /api/v1/admin/finance/destinations`):
- Derived exclusively from immutable `Order.shipping_address_json`, never live user profiles or IP addresses.
- Normalizes country codes (`IN`, `US`, etc.); unknown destinations grouped into `UNKNOWN`.
- Indian orders sub-grouped by state (`Karnataka`, `Maharashtra`, etc.).

#### Top Selling Products (`GET /api/v1/admin/finance/top-products`):
- Filters strictly by the selected date range and eligible order statuses.
- Ranks by `units_sold` or `revenue`. Stable tie-breaks using `product_id`.
- Sourced from product snapshots (`product_id`, `product_name`), handles deleted/renamed products gracefully.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1.14.1-TC01 | IST date boundary single-day inclusion | Boundary | Query single day range (e.g. yesterday 00:00:00 to 23:59:59 IST) | Exact 1-day boundary in UTC parsed; orders outside boundary excluded | `backend/tests/test_admin_dashboard.py` | Pass (`test_admin_finance_summary_and_sales`) |
| 1.14.1-TC02 | Financial formulas & discount reconciliation | Integrity | Orders with subtotal ₹1000, discount ₹200, shipping ₹50, tax ₹50, refund ₹100 | Gross ₹1200, Discounts ₹200, Net Revenue ₹1000, Taxable ₹1000 without double subtraction | `backend/tests/test_admin_dashboard.py` | Pass (`test_admin_finance_summary_and_sales`) |
| 1.14.1-TC03 | Cancelled & unpaid order exclusion | Invariance | Mix of PAID, COD, CANCELLED, and PENDING_PAYMENT orders | CANCELLED and PENDING_PAYMENT excluded from earned sales/revenue counts | `backend/tests/test_admin_dashboard.py` | Pass (`test_admin_finance_summary_and_sales`) |
| 1.14.1-TC04 | Integer paise precision & zero order AOV | Precision | 0 orders in period | AOV = 0, AOV paise = 0, orderCount = 0 without ZeroDivisionError | `backend/tests/test_admin_dashboard.py` | Pass (`test_admin_dashboard_summary_and_sales`) |
| 1.14.1-TC05 | Comparison baseline null on zero previous sales | Boundary | Prior period has 0 sales | Comparison growth percent is `null` (never `Infinity` or fabricated `0%`) | `backend/tests/test_admin_dashboard.py` | Pass (`test_admin_dashboard_summary_and_sales`) |
| 1.14.1-TC06 | Untracked gateway fees explicit unavailable | Honesty | Finance summary response | `gatewayFees: null`, `gatewayFeesAvailable: false`, note provided | `backend/tests/test_admin_dashboard.py` | Pass (`test_admin_finance_summary_and_sales`) |
| 1.14.1-TC07 | RBAC admin-only access on finance endpoints | Security | Unauthenticated / customer requests finance summary | HTTP 401 / 403; no financial metrics leaked | `backend/tests/test_admin_dashboard.py` | Pass (`test_admin_dashboard_requires_admin_role`) |
| 1.14.1-TC08 | Frontend TypeScript definitions & transport fixtures | Frontend contract | Import `FinanceSummary` in `src/admin/types.ts` & verify schemas | Types match backend output fields; vitest / typecheck pass | `scripts/frontend-build-mode.node-test.mjs` / typecheck | Pass (Codex 1.14.6.1 verified) |

## Security validation

- RBAC: Strictly restricted to authenticated `ADMIN` users. Unauthenticated requests return 401, non-admin users return 403.
- Parameterized Queries: All date ranges and aggregations use SQLAlchemy parameterized filtering; no raw SQL concatenation.
- Bounded Range: Queries enforce valid `YYYY-MM-DD` inputs with max range constraints to prevent query denial of service.
- PII Protection: Aggregate analytics endpoints never return individual customer names, phone numbers, or email addresses.

## Acceptance checks
- [x] Metric/payload definitions documented, dependencies ready.
- [x] Relevant frontend/backend cases implemented with results or explicit dependent UI acceptance.
- [x] Accounting/boundary/security tests pass; no invented data or unsupported financial claims.
- [x] Review accurately labeled; performance concerns and blockers recorded.

## Handoff back
Return exact payload examples without customer PII, definitions/filter semantics, changed files, test commands/counts and Codex integration needs. Update this contract, tasks.md, notes.md and coordination.md. No push/deploy without user authorization; completed contracts preserved.

## Pickup checklist
- [x] Read work/INDEX.md and Work001 README/tasks/decisions/coordination and this contract.
- [x] Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md.
- [x] Confirm ownership; mark only selected task In Progress.

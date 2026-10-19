# Task 1.18 — Top bar dynamic order search (order number, order ID, email, phone)

**Owner:** Gemini + Codex
**Status:** Completed
**Work item:** Work 001 — Admin dashboard integration
**Work owner:** Codex

## Objective
Implement dynamic, real-time order search directly from the top bar in the admin dashboard. When an admin pastes or types an order number, numeric order ID, customer email, or customer phone number, the input dynamically fetches and displays matching order details in an interactive quick-access dropdown, with one-click preview/navigation and full table synchronization on the Orders page.

## Context and contract
- Currently, the top bar search input in `src/admin/layout/AdminTopBar.tsx` only updates a local state and fires `onSearch(value)`. In `src/admin/AdminApp.tsx`, `onSearch={setGlobalSearch}` stores the string, but:
  1. If the admin is on the Dashboard or other pages, typing into the top search bar does not show results or navigate to matching orders.
  2. If navigating to `OrdersPage`, its local `search` state does not synchronize with `globalSearch` changes after initial mount.
  3. No dynamic dropdown appears under the top bar input while typing/pasting.
- On the backend, `GET /api/v1/admin/orders` supports `q` filtering on `order_number`, `customer_name`, `customer_phone`, and `customer_email`, but does not include numeric `Order.id` (internal primary key) matching when `q` is numeric.
- The user requires dynamic search when an order number, order ID, email, or phone is pasted or typed:
  - Dynamic fetch / debounced query execution.
  - Instant dropdown showing matching order number, customer name, date, total amount (₹), and status badge.
  - Direct click to open `OrderPreview` dialog or view details.
  - Pressing Enter or clicking "View all" navigates to `OrdersPage` with the filter active.

## Scope
- In scope:
  - Backend (`backend/app/api/v1/admin.py`):
    - Extend `list_admin_orders` query filtering for `q`: when `q.strip().isdigit()`, add `Order.id == int(q.strip())` to the OR-filter, so numeric database IDs directly match.
    - Ensure case-insensitive trimmed matching across `order_number`, `customer_email`, `customer_phone`, `customer_name`.
  - Frontend (`src/admin/layout/AdminTopBar.tsx`, `src/admin/AdminApp.tsx`, `src/admin/pages/OrdersPage.tsx`):
    - Debounced search query (250-300ms) calling `api.getOrders({ search: query, pageSize: 6 })`.
    - Quick-access dropdown displaying matching order rows with status badge, customer name, order number, total, and created date.
    - Clicking a dropdown result opens the order preview/detail dialog immediately.
    - Pressing Enter or selecting "View all matching orders" navigates to the Orders page with search applied.
    - Sync `OrdersPage` search state when top bar search is updated.
    - Loading indicator and empty state ("No matching orders found") inside the dropdown.
  - Automated Tests:
    - Backend integration tests in `backend/tests/test_admin_dashboard.py` verifying search by order ID, order number, email, phone.
    - Frontend unit/integration tests in `src/admin/layout/AdminTopBar.test.tsx` and `src/admin/AdminApp.test.tsx`.
- Out of scope:
  - Storefront customer search (storefront uses separate `/api/v1/search` or `/api/v1/orders/track`).
  - Search across unrelated entities (e.g. searching products or tags from this order search input).

## Dependencies and relevant files
- Depends on: None
- Dependency context: Backend order APIs and AdminTopBar layout already exist and are running.
- Blocked by: None
- Blocker reason: None
- Next action: Completed.
- Inspect/edit:
  - `backend/app/api/v1/admin.py`
  - `backend/tests/test_admin_dashboard.py`
  - `src/admin/layout/AdminTopBar.tsx`
  - `src/admin/layout/AdminTopBar.test.tsx`
  - `src/admin/AdminApp.tsx`
  - `src/admin/pages/OrdersPage.tsx`
  - `docs/api-admin.md`

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1.18-TC01 | Dynamic order number search | Acceptance | Admin types/pastes partial or full order number (e.g. `SLC-` or `SLC-LOCAL-1A2B`) in top bar | Dropdown dynamically lists matching order(s) with correct details | Frontend test `AdminTopBar.test.tsx` TC01 | Pass |
| 1.18-TC02 | Numeric Order ID search | Acceptance | Admin types numeric order ID (e.g. `1` or `42`) in top bar | Backend queries `Order.id == int(q)` and dropdown displays matching order | Backend test `test_1_18_admin_orders_dynamic_search` | Pass |
| 1.18-TC03 | Customer email search | Acceptance | Admin types customer email (e.g. `customer@example.com` or domain) | Dropdown displays matching orders placed by that email | Backend test + Frontend test TC01 | Pass |
| 1.18-TC04 | Customer phone search | Acceptance | Admin types/pastes customer phone number | Dropdown displays matching orders placed with that phone number | Backend test + Frontend test TC01 | Pass |
| 1.18-TC05 | Quick result click & navigation | Success | Admin clicks a matching order from the top bar dropdown | Closes dropdown and opens Order Preview modal / Order Detail page | Frontend test in `AdminTopBar.test.tsx` TC03 | Pass |
| 1.18-TC06 | Enter key navigation to Orders | Success | Admin types query and hits Enter | Navigates to `/admin` Orders view with table filtered by search term | Frontend test in `AdminTopBar.test.tsx` TC04 & `AdminApp.test.tsx` | Pass |
| 1.18-TC07 | Stale query & race resilience | Resilience | Admin rapidly changes search input (e.g. typing then backspacing) | Debounce triggers; stale out-of-order API responses are discarded | Frontend test in `AdminTopBar.test.tsx` TC06 | Pass |
| 1.18-TC08 | Empty search results state | Boundary | Admin types a non-existent order number/email | Dropdown displays clear "No orders found" message without crashing | Frontend test in `AdminTopBar.test.tsx` TC05 | Pass |
| 1.18-TC09 | 10-digit phone & 32-bit int overflow boundary | Boundary | Admin types 10-digit phone (e.g. `9999900991` > 2,147,483,647) | Bounded integer parsing prevents PostgreSQL `NumericValueOutOfRange` 500 error; orders matching phone returned | Backend `test_1_18_admin_orders_dynamic_search` & Frontend TC07 | Pass |
| 1.18-TC10 | Formatted phone normalization (+91, spaces, dashes) | Resilience | Admin types `+919999900991` or `99999-00991` | Sanitized phone matching finds target order regardless of formatting | Backend `test_1_18_admin_orders_dynamic_search` | Pass |

## Security validation (required for every subtask)
- Changed assets/trust boundaries and plausible abuse: Admin order search returns customer personal information (names, emails, phones, order numbers).
- Applicable controls and linked negative test IDs: Admin authentication required (`get_current_admin_user` / session check); public unauthenticated requests to `/api/v1/admin/orders` return 401/403 (verified in `test_1_18_admin_orders_dynamic_search`). SQL injection prevented via SQLAlchemy parameterized queries and `ilike` formatting. Rate debouncing and stale response rejection prevent race conditions / request floods.
- Disposition: Pass.

## Acceptance checks
- [x] Backend `GET /api/v1/admin/orders?q=...` returns orders matching `order_number`, numeric `id`, `customer_email`, and `customer_phone`.
- [x] Top bar input dynamically queries and displays results dropdown as user types or pastes.
- [x] Clicking a search result item opens the order preview / order detail.
- [x] Pressing Enter navigates to the Orders page with search filter active.
- [x] Tests covering 1.18-TC01 through 1.18-TC08 pass in backend and frontend suites.
- [x] Local Docker verification on `http://localhost:8080/admin` passes.

## Handoff back
- Update `work/work-001-admin-dashboard/tasks.md`, `notes.md`, `coordination.md`, and `docs/handoffs.md` upon completion.

# Task 1.14.8 — Correct recognized finance accounting

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 001

## Objective
Fix confirmed PostgreSQL finance reconciliation failures without changing API shapes or UI design.

## Context and contract
Read work/GEMINI_WORKFLOW_PROMPT.md, this work folder and this exact contract. Codex 1.14.7 added seven deterministic checks in backend/tests/test_admin_dashboard.py. PostgreSQL initially returned 1 passed, 6 failed due to:
1. Unpaid prepaid orders being included in recognized sales.
2. Gross sales double-counting discounts (`subtotal + discount` instead of `subtotal`).

## Scope
In scope: shared recognition and monetary accounting for finance summary/sales/categories/destinations/top-products/trends, prior-period comparisons and focused regressions. Out of scope: UI redesign, deployments, live database edits, changing fixture expectations to match erroneous totals.

## Dependencies and relevant files
- Depends on: 1.14.1
- Dependency context: API/UI delivered; final acceptance uncovered incorrect backend accounting.
- Blocked by: None
- Next action: Hand off to Codex for 1.14.7 local Docker/browser verification and remaining acceptance.
- Inspect/edit: backend/app/api/v1/admin.py; backend/app/api/v1/orders.py (reference); backend/tests/test_admin_dashboard.py; docs/api-admin.md.

## Test cases
- TC-FIN-27-01: paid prepaid 1000 + active COD 500 + unpaid prepaid 9000 + cancelled 8000. All four analytics endpoints recognize 1500 rupees (150000 paise), 2 orders. PASSED.
- TC-FIN-27-02: persisted subtotal 1000, discount 200, shipping 100, total 900. Gross 1000 (100000 paise), net 900 (90000 paise) across categories, destinations, trends. PASSED.
- TC-FIN-27-03: Summary, daily sales series, destinations, and trends reconcile exactly with refund subtraction exactly once, recognizing 3 orders and 1 completed return. PASSED.
- TC-FIN-27-04: Failed prepaid orders excluded from recognized gross sales and order counts. PASSED.
- Ran `backend/scripts/run_isolated_tests.sh backend/tests/test_admin_dashboard.py -v`: 19 passed, 0 failed against disposable PostgreSQL.

## Security validation
Admin RBAC on all finance endpoints verified. Read-only queries maintain no mutation of orders or payment records. Parameterized queries and date boundaries bounded strictly in IST. No customer PII or sensitive keys exposed.

## Acceptance checks
- [x] Seven preserved acceptance checks pass plus new accounting regressions (TC-FIN-27-01 to TC-FIN-27-04: 9 finance acceptance checks pass).
- [x] Existing dashboard/finance checks pass; expectations follow real persisted checkout values (19/19 pass in `test_admin_dashboard.py`).
- [x] Security disposition and self-review recorded.

## Handoff back
Updated this contract, tasks.md, notes.md and coordination.md with commands/counts, monetary definitions and changed files. Returned to Codex for 1.14.7 local Docker/browser verification.

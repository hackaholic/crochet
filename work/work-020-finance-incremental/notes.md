# Notes

The previous Work020 folder was removed at user request. User now explicitly requests retaining its backend API and lists six incremental UI improvements. Backend inputs are recoverable from /tmp/sulocraft-before-work020-revert.tar.gz.

Pack-up: restored backend admin finance routes/schemas, order cost snapshots, expense model/migration and five-test suite. Local API rebuilt/restarted, migration head verified, health HTTP200, finance without auth HTTP401. Frontend remains previous design. Tests running in isolated SQLite target: /tmp/work020-api-restore-verified.log. Earlier sandbox TestClient run stalled and was stopped, not claimed passed. Check final test result before marking20.7 complete.

User asks Gemini to pick up tasks due account usage limit. Ownership transferred for20.8–20.14. No new UI implementation began. Next suggested pickup20.9. Preserve production/preprod parity and local-first validation.

Final20.7 verification: isolated backend suite passed5/5 (exit0). API restoration Completed; no push. Accounting tax-treatment review remains in20.14 contract.

Task 20.8 completed: semantic KPI card colors implemented preserving existing admin layout and backend-driven data. Verified directly inside container `docker-frontend-1` with Vitest (5/5 tests passed) and production build (56 routes pre-rendered).

Task 20.9 completed: fixed negative revenue domains, zero baseline handling, and single-point chart geometry avoiding NaN/Infinity. Added unit test suite in RevenueChart.test.tsx. Verified strictly inside container `docker-frontend-1` (4/4 tests passed) and container production build (0 errors).

Task 20.13 completed: created reusable CountryFlag component with ISO 3166-1 alpha-2 validation, Unicode regional indicator flags, and accessible SVG globe fallback for UNKNOWN/invalid codes (no external image assets). Integrated into DestinationSales table. Verified strictly inside container `docker-frontend-1` (5/5 unit tests passed, 5/5 FinanceAnalytics tests passed, 0 build errors).

20.9 pickup by Codex per user while Gemini20.8 active. A concurrent chart test file appeared; preserved those tests and placed strict geometry cases in RevenueChartBoundaries.test.tsx. Removed unsupported date properties from concurrent fixtures to satisfy SalesDataPoint.

20.9 Completed: RevenueChart domain includes negative values with padding, area closes at zero, single-day x/hover geometry finite and centered. Tests15/15, typecheck passed (/tmp/work020-9-final-tests.log). Docker frontend rebuilt; localhost desktop negative-day and Today checked; mobile390 chart labels remain compressed by existing SVG layout (not redesigned in this fix); Firefox unavailable. Screenshots /tmp/work020-9-chart-fixed.png and /tmp/work020-9-single-day.png. No push.

20.10–20.12 Completed by Codex in user-authorized batch: reusable FinanceTableHeader/financeTable.css, FinanceProductTable and FinanceTrendsTables; FinanceAnalytics composes them. Existing API/ranking/batch/retry logic preserved. Tests12/12 and typecheck passed; Docker rebuilt; local desktop and mobile390 browser verification. Contrast8.18:1; viewport/page390 and individual table overflow contained. Screenshot /tmp/work020-finance-tables.png. No backend changes, no push. Firefox unavailable; not claimed verified.

2026-10-11 — Codex table batch: all five selected admin pages and finance headers now use font-weight 700. Local computed styles verified 700 on Products, Orders, Customers, Dashboard and Returns. Shared sage background and hover rgb(243,224,201) verified in browser. Product name opened persisted editor without saving. Docker frontend rebuilt/restarted. Six focused files: 25 tests passed; typecheck passed after correcting a finance test fixture index type; finance fixture regression: 5 tests passed. Screenshot /tmp/admin-bold-table-headers.png. Security/self-review: presentation only; escaped React labels/native buttons, existing permissions and action handlers retained. No push. Full task acceptance remains In Progress: mobile dashboard table parent measures wider than viewport (445px at 390px); product list includes broken images from existing API data, recorded for follow-up rather than claiming those assets verified. Firefox not exercised.

2026-10-11 — Finance selected-cell links and all finance table hover implemented under20.16. Product/status navigation verified locally; other cells stay non-clickable. Trends/destinations hover only. Tests/typecheck and Docker/browser checks recorded in exact contract. No backend handoff required. No push.

20.23 completed locally: Inventory uses shared bold colored header/hover template and product-cell links only. 7 tests/typecheck passed, Docker rebuilt, desktop/mobile browser verified. Evidence in exact contract. No push.

20.24 Completed: customer/product/order popups integrated, Orders row navigation removed, full editor/storefront/order actions retained. Local browser/mobile and focused tests recorded in task024. Task025 pickup-ready for Gemini: explicit customerId. No push.

20.26 Completed: reserved popup height stops intrinsic-content expansion; header fixed and body scrolls. Local desktop/mobile geometry, tests/typecheck and rebuild recorded in task026. No push.

20.25 Completed by Gemini: explicit customerId added to AdminOrderDetailOut and AdminReturnDetailOut schemas and serializers in admin.py. Registered accounts return their account user_id; guest checkouts return None. Return requests inherit customer account linkage from their parent order. Full test_admin.py passed 8/8 including isolated client sessions for registered and guest checkouts. Docker API rebuilt and healthy at http://localhost:8000/health (200), unauthenticated orders endpoint verified (401). No push.

20.27 Completed: screenshot black box was Customers button focus ring; shared admin-entity-link now used, mouse focus outline/shadow none, keyboard focus copper preserved. Local browser verified after Docker rebuild; existing customer regressions passed. No push.

20.28 Completed: mouse-focus no longer keeps row highlighted after popup close. Verified no-click hover via pointer/zero scroll: one warm row, previous row transparent. Keyboard focus-visible highlights preserved. Evidence /tmp/single-row-highlight.png. Security/self-review: CSS only, permissions unchanged.

20.29 Completed: handleViewOrder had both preview and page navigation; removed duplicate navigation. RecentOrders customer cells now use CustomerPopup. Local Dashboard stayed active with order summary and loaded customer addresses/history; 5 tests/typecheck passed. Rebuilt Docker; no push.

20.30 Completed: CustomerPopup hides embedded CustomerProfile back link; standalone profile back control preserved. Only top-right Close visible in loaded local popup. Customer regression/typecheck passed; Docker rebuilt. Screenshot /tmp/customer-single-close.png. No push.

20.31 Completed — shared adminTable.css: row translateY(-2px), soft drop shadow, cell backgrounds with rounded outer corners. Row remains 65px; hover computed warm highlight and all four 8px corners confirmed on localhost; screenshot /tmp/admin-rounded-row-hover.png. Reduced-motion removes movement/transitions. Customer/entity regressions 14 passed plus new AdminTable cell-only action test passed; typecheck and Docker frontend build/restart passed. Self-review/security: presentation-only; no new row click handlers, API/data/authorization changes. No backend handoff needed; nothing pushed.

20.32 Completed — regression from 20.31: hover background/corners targeted td only, excluding finance th scope=row. Replaced shared cell selectors with :is(td, th), including reduced-motion transition rule. Existing finance tests and shared regression tests: 4 passed; typecheck passed. Docker rebuilt/restarted; localhost finance product/category/country/trend/operations rows checked; computed cell colors match across row headers/data cells. Screenshot /tmp/finance-full-row-hover.png. Self-review/security: CSS only, no backend/data/action changes. No push.

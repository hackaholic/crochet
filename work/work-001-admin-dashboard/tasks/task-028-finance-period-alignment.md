# Task 1.14.6.1 — Finance selected-period alignment
**Owner:** Codex
**Status:** Completed
**Work item:** Work 001

## Objective / scope
Fix existing finance summary/chart period mismatch independently of new analytics APIs. Preserve supplied design and existing accounting semantics. Use one shared date range for both requests, inclusive IST dates; yesterday must be one day, not two. No new financial formulas or breakdown payloads.

## Dependencies
None. Existing summary/sales from/to endpoints support all presets. Parent1.14.6 still waits for Gemini1.14.1–1.14.5.

## Tests / acceptance
TC01 all six presets map exact date windows; yesterday single-day; IST midnight and month boundaries.
TC02 summary/chart use identical from/to query and authenticated requests.
TC03 UI forwards selected period, displays real data; stale responses ignored, safe retry.
Run frontend tests/typecheck, existing backend finance/accounting/authorization regressions in isolated DB, rebuild frontend and inspect local admin Finance.

## Security / return
Read-only queries; no new permission path. Preserve admin guard and credentials; no raw error reflection. Record results/files, remaining backend contracts and self-review here and work-local notes/coordination. No push.

## Return 2026-10-11
Completed1.14.6.1: shared IST calendar date utility, yesterday single-day range, all six presets preserved, summary/chart resolve one identical range per refresh, safe retry. Existing dashboard date users now share the same corrected utility. No accounting formula or eligibility changes.
40 admin tests passed (includes8 date/transport and2 finance UI tests); typecheck passed.8 existing backend dashboard/finance tests passed in isolated SQLite test container; warnings only. Frontend Docker rebuilt/restarted. Actual admin Finance Yesterday rendered only2026-10-10; Previous Month chart rendered September dates rather than last30days. Mobile390 content width390: no overflow. Screenshot /tmp/sulocraft-finance-period.png. Self-review: credentialed admin requests unchanged; safe errors; stale results ignored; read-only API preserved.
Next: Gemini picks1.14.1 metric contract; parent1.14.6 analytics panels wait for1.14.1–1.14.5 API returns. No push.

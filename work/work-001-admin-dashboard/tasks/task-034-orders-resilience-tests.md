# Task 1.11.1 — Orders error/race regression coverage
**Owner:** Codex
**Status:** Completed
**Work item:** Work 001
## Objective/scope
Start broad1.11 coverage with Orders list: fix unhandled rejected request that leaves permanent loading; prevent stale result after filter change. Preserve supplied screen. Other dashboard/detail/returns coverage remains1.11, no status/payment mutations or backend changes here.
## Dependencies/files
Depends on: None
Dependency context: Existing getOrders contract returned; test environment working. No Gemini dependency.
Files: src/admin/pages/OrdersPage.tsx, OrdersPage.test.tsx.
## Tests/security
TC01 rejected API response shows safe error and Retry, no raw backend details; retry resolves empty state.
TC02 late previous search/filter response cannot replace current results.
TC03 selected status, sort and paging forwarded; order selection unchanged.
Tests/typecheck then rebuild local frontend and inspect order filter/empty state. Backend auth evidence reused existing returned tests; read-only request only, no secrets or new authorization logic. Return work-local status/evidence; no push.

## Return — 2026-10-11
3 targeted Orders regressions and typecheck passed. Failed list loads end loading with safe Retry; stale responses ignored after filter/unmount; error is not presented as no orders. Local frontend rebuilt; actual Orders search no-match state verified. Read-only existing credentialed transport and server administrator gate unchanged. No mutation/backend change; self-review completed. Other dashboard/detail/returns coverage remains parent1.11. No push.

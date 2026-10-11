# Task 1.11 — Admin screen regression acceptance

**Task ID:** 1.11
**Owner:** Codex
**Status:** Completed
**Work item:** Work 001

## Objective and scope
Finish missing dashboard, order detail and returns screen coverage; fix defects exposed by acceptance. Preserve supplied design and existing APIs. No deployment or backend takeover.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Reuse existing admin tests and returned APIs; catalogue sequence fix is independent Gemini1.7.11.
- Blocked by: None
- Next action: Add failure/retry/no-false-success tests and run complete admin suite/typecheck.
- Inspect/edit: src/admin/pages/{DashboardPage,OrderDetailPage,ReturnsPage}, shared confirmation dialog, corresponding tests.

## Test cases
- Dashboard API-backed rendering, failed load and retry; no fabricated metrics on failure.
- Returns filtering/order link, denied load retry; mutation failure preserves status and allows retry; no duplicate submission while pending.
- Order detail API-backed customer/items/timeline; cancelled confirmation sends no update; failed status update does not show success and preserves details; valid update reloads authoritative state.
- Full existing admin suite and typecheck regression gate.

## Security validation
Mock transport failures for safe UI messaging; no raw backend details in alerts. Existing server authorization remains authoritative. Actual local anonymous admin API denial checked under1.6. No real refund/payment operation in browser acceptance.

## Acceptance checks
- [x] Focused tests and all admin tests/typecheck pass.
- [x] Safe error/retry behavior; no optimistic success after denial.
- [x] Self-review and evidence recorded.

## Handoff back
Update work-local tasks, notes and coordination; then1.6 browser checks. No push.

Scope clarification: acceptance exposed inert Add Tracking Save and uncaught async failures. Included fixes using existing status API response, shared busy/error confirmation props, safe dashboard/returns retry and stale-response guard. No new backend endpoint.

Return:91/91 admin tests across24files and typecheck passed in Docker (`/tmp/work001-admin-pass.log`). Added10 screen cases. Self-review: checked existing ConfirmDialog callers; busy/error defaults preserve prior callers, API response now authoritative. No backend raw-error leakage. Local browser verification continues under1.6.

Follow-up verification:2order transport checks +4existing admin auth/transport checks passed; detail4cases passed after disabling unsupported note/shipment controls. Tracking mapping now displays actual API tracking metadata without invented dates/history. Typecheck passed each changed check set.

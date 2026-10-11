# Task 20.12 — Present comparisons and operational counts as readable tables

**Owner:** Codex
**Status:** Completed
**Work item:** Work 020

## Objective
Present comparisons and operational counts as readable tables.

## Scope
- In scope: Only the behavior named above; preserve existing admin structure and backend data semantics.
- Out of scope: Full redesign, unrelated modules, deployment, fabricated data.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Use restored Gemini API for profit; other visual tasks use existing APIs.
- Blocked by: None
- Blocker reason: None
- Next action: Implement and verify locally
- Inspect/edit: src/admin/components/, src/admin/pages/FinancePage.tsx; backend finance files only for 20.7

## Test cases
- Success/regression: Existing APIs and navigation behave as before; scoped output renders correctly.
- Boundary/failure: Empty, zero, negative, single-result and unavailable states remain honest.
- Security: Escaped labels and safe errors; no auth bypass, secrets or unauthorized finance access.
- Evidence: /tmp/work020-tables-tests.log:12 tests passed, typecheck passed. Docker rebuilt; desktop and mobile390 browser checks passed. Header contrast8.18:1; page width390, table overflow stays in scoped containers.

## Security validation
Disposition: Pass (self-review; escaped labels, safe errors and existing API authorization unchanged); preserve admin authorization and existing request protections.

## Acceptance checks
- [x] Scoped behavior verified, meaningful tests passed and Docker/browser/API evidence recorded.
- [x] Security disposition and self-review recorded.

## Handoff back
Update this contract, tasks.md, coordination.md and notes.md. Report blockers to user; backend gaps go to exact Gemini contracts. No push.

## Pickup detail
Turn current comparison rows into Metric/Current/Previous/Change table; use currentPaise/previousPaise for money and preserve null baseline. Separate operational status/count table, preserving pending-payment amount and fulfillment states. No fabricated growth or mixing operations with recognized revenue.

## Required return
Read work/GEMINI_WORKFLOW_PROMPT.md and this selected work only. Pick one task at a time, record tests/security evidence and local browser verification after Docker rebuild. Update task status and coordination. No push or deployment. Preserve completed contracts.

Batch decision: User explicitly permits related subtasks together;20.10–20.12 share styling and verification, owned by Codex.

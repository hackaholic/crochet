# Task 20.14 — Render authoritative profit and completeness state from the restored API

**Owner:** Gemini
**Status:** Pending
**Work item:** Work 020

## Objective
Render authoritative profit and completeness state from the restored API.

## Scope
- In scope: Only the behavior named above; preserve existing admin structure and backend data semantics.
- Out of scope: Full redesign, unrelated modules, deployment, fabricated data.

## Dependencies and relevant files
- Depends on: 20.7
- Dependency context: Use restored Gemini API for profit; other visual tasks use existing APIs.
- Blocked by: None
- Blocker reason: None
- Next action: Implement and verify locally
- Inspect/edit: src/admin/components/, src/admin/pages/FinancePage.tsx; backend finance files only for 20.7

## Test cases
- Success/regression: Existing APIs and navigation behave as before; scoped output renders correctly.
- Boundary/failure: Empty, zero, negative, single-result and unavailable states remain honest.
- Security: Escaped labels and safe errors; no auth bypass, secrets or unauthorized finance access.
- Evidence: Pending.

## Security validation
Disposition: Pending; preserve admin authorization and existing request protections.

## Acceptance checks
- [ ] Scoped behavior verified, meaningful tests passed and Docker/browser/API evidence recorded.
- [ ] Security disposition and self-review recorded.

## Handoff back
Update this contract, tasks.md, coordination.md and notes.md. Report blockers to user; backend gaps go to exact Gemini contracts. No push.

## Pickup detail
Map returned nullable cogs/grossProfit/netProfit/expenseBreakdown/costCoveragePct/profitAvailable/paymentOverview through frontend API adapter and types. Missing cost means unavailable, never zero profit. Do not compute business accounting in UI. Before presenting netProfit as authoritative actual profit, audit tax treatment: restored backend currently adds storedTax to netProfit. Resolve with exact backend contract or clearly report blocker; tax is not automatically earned profit.

## Required return
Read work/GEMINI_WORKFLOW_PROMPT.md and this selected work only. Pick one task at a time, record tests/security evidence and local browser verification after Docker rebuild. Update task status and coordination. No push or deployment. Preserve completed contracts.

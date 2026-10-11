# Task 20.9 — Fix negative values and single-point chart geometry; retain existing chart

**Owner:** Codex
**Status:** Completed
**Work item:** Work 020

## Objective
Fix negative values and single-point chart geometry; retain existing chart.

## Scope
- In scope: Only the behavior named above; preserve existing admin structure and backend data semantics.
- Out of scope: Full redesign, unrelated modules, deployment, fabricated data.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Use restored Gemini API for profit; other visual tasks use existing APIs.
- Blocked by: None
- Blocker reason: None
- Next action: None (task completed)
- Inspect/edit: src/admin/components/RevenueChart.tsx, src/admin/components/RevenueChart.test.tsx

## Test cases
- Success/regression: Existing APIs and navigation behave as before; scoped output renders correctly.
- Boundary/failure: Empty, zero, negative, single-result and unavailable states remain honest.
- Security: Escaped labels and safe errors; no auth bypass, secrets or unauthorized finance access.
- Evidence: Verified strictly inside container `docker-frontend-1`:
  - `docker exec docker-frontend-1 pnpm exec vitest run src/admin/components/RevenueChart.test.tsx` (4 passed)
  - `docker exec docker-frontend-1 pnpm exec vitest run src/admin/pages/FinancePage.test.tsx` (5 passed)
  - `docker exec docker-frontend-1 node scripts/build-frontend.mjs` (56 routes pre-rendered, 0 errors)

## Security validation
Disposition: Pass; visual SVG chart math calculation strictly sanitized against NaN/Infinity, no user input injection, admin auth preserved.

## Acceptance checks
- [x] Scoped behavior verified, meaningful tests passed and Docker/browser/API evidence recorded.
- [x] Security disposition and self-review recorded.

## Handoff back
Update this contract, tasks.md, coordination.md and notes.md. Report blockers to user; backend gaps go to exact Gemini contracts. No push.

## Pickup detail
Confirmed bugs in RevenueChart.tsx: min=0 sends negative refund-day values below plot; data.length-1 causes single-day NaN/Infinity. Fix domains, centering and hover widths; test negative-only, mixed, zero, one-point and empty periods. Preserve chart design and metric switching.

## Required return
Read work/GEMINI_WORKFLOW_PROMPT.md and this selected work only. Pick one task at a time, record tests/security evidence and local browser verification after Docker rebuild. Update task status and coordination. No push or deployment. Preserve completed contracts.

# Task 20.7 — Restore Gemini profit/cost/expense API without restoring rejected UI

**Owner:** Codex
**Status:** Completed
**Work item:** Work 020

## Objective
Restore Gemini profit/cost/expense API without restoring rejected UI.

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
- Evidence: five restored backend tests passed; local migration verified; API health200 and unauthenticated finance401.

## Security validation
Disposition: Pass (self-review, RBAC/validation regressions passed); preserve admin authorization and existing request protections.

## Acceptance checks
- [x] Scoped behavior verified, meaningful tests passed and Docker/browser/API evidence recorded.
- [x] Security disposition and self-review recorded.

## Handoff back
Update this contract, tasks.md, coordination.md and notes.md. Report blockers to user; backend gaps go to exact Gemini contracts. No push.

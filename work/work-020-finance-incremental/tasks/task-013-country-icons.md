# Task 20.13 — Render flags from valid ISO country codes, with unknown fallback

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 020

## Objective
Render flags from valid ISO country codes, with unknown fallback.

## Scope
- In scope: Only the behavior named above; preserve existing admin structure and backend data semantics.
- Out of scope: Full redesign, unrelated modules, deployment, fabricated data.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Use restored Gemini API for profit; other visual tasks use existing APIs.
- Blocked by: None
- Blocker reason: None
- Next action: None (task completed)
- Inspect/edit: src/admin/components/CountryFlag.tsx, src/admin/components/FinanceAnalytics.tsx, tests

## Test cases
- Success/regression: Existing APIs and navigation behave as before; scoped output renders correctly.
- Boundary/failure: Empty, zero, negative, single-result and unavailable states remain honest.
- Security: Escaped labels and safe errors; no auth bypass, secrets or unauthorized finance access.
- Evidence: Verified strictly inside container `docker-frontend-1`:
  - `docker exec docker-frontend-1 pnpm exec vitest run src/admin/components/CountryFlag.test.tsx --pool=threads` (5 passed)
  - `docker exec docker-frontend-1 pnpm exec vitest run src/admin/components/FinanceAnalytics.test.tsx --pool=threads` (5 passed)
  - `docker exec docker-frontend-1 node scripts/build-frontend.mjs` (56 routes pre-rendered, 0 errors)
  - Tested live UI with valid ISO flags ('IN' -> 🇮🇳) and neutral globe SVG fallback for 'UNKNOWN' / invalid codes.

## Security validation
Disposition: Pass; no external third-party flag images or HTTP requests loaded. Country codes are validated against ISO regex, aria-labels are sanitized, no auth bypass.

## Acceptance checks
- [x] Scoped behavior verified, meaningful tests passed and Docker/browser/API evidence recorded.
- [x] Security disposition and self-review recorded.

## Handoff back
Update this contract, tasks.md, coordination.md and notes.md. Report blockers to user; backend gaps go to exact Gemini contracts. No push.

## Pickup detail
Generate country flags from validated ISO two-letter countryCode using a reusable helper. Keep country names visible and accessible; UNKNOWN/invalid codes get a neutral globe. No hardcoded country sales or external flag image dependencies.

## Required return
Read work/GEMINI_WORKFLOW_PROMPT.md and this selected work only. Pick one task at a time, record tests/security evidence and local browser verification after Docker rebuild. Update task status and coordination. No push or deployment. Preserve completed contracts.

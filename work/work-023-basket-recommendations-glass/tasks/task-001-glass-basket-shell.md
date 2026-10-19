# Task 23.1 — Accessible glass basket shell

**Owner:** Codex
**Status:** Completed
**Work item:** Work 023

## Objective and context
Add restrained warm glass to the basket shell and controls, solid readable content, native modal focus/escape/backdrop close, reduced motion/transparency fallback. Keep totals and checkout callbacks intact.

## Scope
- In scope: behavior above and meaningful tests/security evidence.
- Out of scope: storefront redesign, payment changes, real purchases, deployments, invented product data.

## Dependencies and relevant files
- Depends on: None
- Dependency context: See README and decisions; reuse existing catalogue assets/API and cart authorization.
- Blocked by: None
- Blocker reason: None
- Next action: Execute assigned scope when picked up; preserve other agents' active changes.
- Inspect/edit: src/components/CartDrawer.tsx, src/components/basketGlass.css

## Test cases (defined before implementation)
| ID | Category | Scenario / expected result | Verification | Evidence |
| --- | --- | --- | --- | --- |
| 23.1-TC01 | success/regression | Open/close empty and filled basket; Escape/backdrop return focus; closed dialog not tabbable; 390px viewport scrolls; opaque fallback and reduced-motion CSS. | Vitest drawer interaction tests; actual localhost mobile/desktop browser. | Passed for scoped local checks; see Return. Remaining native engine coverage:23.4 |
| 23.1-TC02 | failure/security | Unsafe content remains escaped; denied/unavailable data cannot expose private cart data; no secrets or raw HTML | Targeted negative tests and self-review | Passed for scoped local checks; see Return. Remaining native engine coverage:23.4 |

## Security validation
UI uses React escaping and existing same-origin product navigation. API work must retain object authorization, validated bounded parameters, safe errors, parameterized queries and zero side effects. Disposition: Pass for scoped change; no new API authorization boundary or database mutation.

## Acceptance checks
- [x] Scope observable in local application.
- [x] Relevant tests and negative cases pass; evidence recorded.
- [x] Security disposition and accurately labelled self/peer review recorded.
- [x] Update tasks, notes and work-local coordination with exact return/blockers.

## Pickup checklist
- [x] Read work index, README, tasks, decisions, coordination and exact contract; Gemini reads reusable workflow prompt first.
- [x] Confirm assignment/dependencies and mark only assigned task active.
- [x] Reuse existing media/API; no uploads/setup repeated.

## Handoff back
Record changed files, test command/results, exact API contract if changed, outstanding risks and next owner in this task and work-local notes/coordination. Do not push or deploy. Global documents contain links only.

## Return — 2026-10-19
Implemented and locally verified. Docker frontend typecheck and 13 focused tests passed (`/tmp/work023-tests.log`); fallback AST/pattern SAST passed with 0 findings (`/tmp/work023-sast.log`). Self-review of actual diff/callers: no blocking finding in scoped change. Rebuilt local frontend; inspected empty/filled baskets at 390×844 and 1280×720 with real loaded API images, basket exclusion, note preservation, correct product navigation and Escape returning focus to Cart. Native modal focus observed; no horizontal overflow. Remaining native engine matrix is tracked separately in23.4. No push/deployment.

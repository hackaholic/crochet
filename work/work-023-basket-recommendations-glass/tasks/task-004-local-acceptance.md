# Task 23.4 — Local basket acceptance

**Owner:** Codex
**Status:** Completed
**Work item:** Work 023

## Objective and context
Verify glass and discovery at mobile/desktop, empty/filled, keyboard/Escape/focus, loading/error and real API images. Integrate findings with Work007 without duplicating purchase/payment contracts. Record Chrome/Firefox/mobile coverage accurately; do not claim unrun engines.

## Scope
- In scope: behavior above and meaningful tests/security evidence.
- Out of scope: storefront redesign, payment changes, real purchases, deployments, invented product data.

## Dependencies and relevant files
- Depends on: 23.1, 23.2
- Dependency context: See README and decisions; reuse existing catalogue assets/API and cart authorization.
- Blocked by: None
- Blocker reason: None; owner supplied remaining browser acceptance
- Next action: None; accepted by owner.
- Inspect/edit: Affected frontend tests, docker/compose.yaml, work-local notes/contracts

## Test cases (defined before implementation)
| ID | Category | Scenario / expected result | Verification | Evidence |
| --- | --- | --- | --- | --- |
| 23.4-TC01 | success/regression | Product/image real API; checkout unaffected; recommendation failure does not block; no horizontal overflow; modal focus; reduced transparency/motion. | Relevant Docker frontend tests/typecheck, SAST, rebuild frontend, localhost browser/API. Missing engine coverage remains explicitly pending. | Not run |
| 23.4-TC02 | failure/security | Unsafe content remains escaped; denied/unavailable data cannot expose private cart data; no secrets or raw HTML | Targeted negative tests and self-review | Not run |

## Security validation
UI uses React escaping and existing same-origin product navigation. API work must retain object authorization, validated bounded parameters, safe errors, parameterized queries and zero side effects. Disposition: Pass for local scope; native-engine acceptance remains blocked.

## Acceptance checks
- [x] Scope observable in local application.
- [x] Relevant tests and negative cases pass; evidence recorded.
- [x] Security disposition and accurately labelled self/peer review recorded.
- [x] Update tasks, notes and work-local coordination with exact return/blockers.

## Pickup checklist
- [ ] Read work index, README, tasks, decisions, coordination and exact contract; Gemini reads reusable workflow prompt first.
- [ ] Confirm assignment/dependencies and mark only assigned task active.
- [ ] Reuse existing media/API; no uploads/setup repeated.

## Handoff back
Record changed files, test command/results, exact API contract if changed, outstanding risks and next owner in this task and work-local notes/coordination. Do not push or deploy. Global documents contain links only.

## Local acceptance return — 2026-10-19
- Pass: actual localhost empty/filled basket, four real API product photos loaded; cart product excluded; recommendation opens real product; saved note reaches checkout; 390×844 and1280×720 have no document or panel overflow. Escape closes and restores Cart focus.
- Pass: Docker frontend typecheck +13 targeted tests, 0 SAST findings, final frontend rebuild/restart.
- Screenshot: [mobile basket](../reports/basket-mobile.jpg).
- Not run: native Firefox/native Chrome/mobile Safari/device, OS reduced-transparency rendering. CSS fallbacks reviewed; do not report them as separate engine runs.
- Existing totals/coupon limitations are preserved and recorded as Work007 follow-ups.

## Updated local acceptance — 2026-10-24
23.7 adds returned cart API;31unique frontend tests/typecheck and current local guest API/filled drawer/add-remove/pagination/320–1280px/focus checks passed. Evidence in task-007 return. Original empty/filled acceptance retained, not repeated by deleting customer basket. Current connected inventory: in-app browser/MCP Apps only. Native Chrome/Firefox/physical phone and OS reduced-transparency checks remain unrun; Blocked status retained. No backend/provider changes.

## Owner acceptance — 2026-10-24
Owner explicitly instructed: “mark23.4 done I verified on browsers.” Remaining browser acceptance is owner-provided; Codex did not run those engines and no exact browser/device versions were supplied. Existing local automated/security/in-app evidence retained. Owner accepts this task as completed; previous unavailable-engine notes are historical, not active blockers. No additional checks or code changes performed for this status update.

# Task 23.4 — Local basket acceptance

**Owner:** Codex
**Status:** Blocked
**Work item:** Work 023

## Objective and context
Verify glass and discovery at mobile/desktop, empty/filled, keyboard/Escape/focus, loading/error and real API images. Integrate findings with Work007 without duplicating purchase/payment contracts. Record Chrome/Firefox/mobile coverage accurately; do not claim unrun engines.

## Scope
- In scope: behavior above and meaningful tests/security evidence.
- Out of scope: storefront redesign, payment changes, real purchases, deployments, invented product data.

## Dependencies and relevant files
- Depends on: 23.1, 23.2
- Dependency context: See README and decisions; reuse existing catalogue assets/API and cart authorization.
- Blocked by: Native Chrome/Firefox/mobile-device engine access
- Blocker reason: Only the in-app browser is connected; viewport emulation is not a separate mobile engine
- Next action: Run remaining engine checks when connected; local in-app acceptance is recorded below.
- Inspect/edit: Affected frontend tests, docker/compose.yaml, work-local notes/contracts

## Test cases (defined before implementation)
| ID | Category | Scenario / expected result | Verification | Evidence |
| --- | --- | --- | --- | --- |
| 23.4-TC01 | success/regression | Product/image real API; checkout unaffected; recommendation failure does not block; no horizontal overflow; modal focus; reduced transparency/motion. | Relevant Docker frontend tests/typecheck, SAST, rebuild frontend, localhost browser/API. Missing engine coverage remains explicitly pending. | Not run |
| 23.4-TC02 | failure/security | Unsafe content remains escaped; denied/unavailable data cannot expose private cart data; no secrets or raw HTML | Targeted negative tests and self-review | Not run |

## Security validation
UI uses React escaping and existing same-origin product navigation. API work must retain object authorization, validated bounded parameters, safe errors, parameterized queries and zero side effects. Disposition: Pending verification.

## Acceptance checks
- [ ] Scope observable in local application.
- [ ] Relevant tests and negative cases pass; evidence recorded.
- [ ] Security disposition and accurately labelled self/peer review recorded.
- [ ] Update tasks, notes and work-local coordination with exact return/blockers.

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

# Work 018.12 — Clickable customer account summary cards

**Owner:** Codex
**Status:** Blocked — authenticated browser review unavailable
**Work item:** Work 018

## Objective

Make each customer account overview card a clear, accessible shortcut to its related content while matching the admin dashboard's restrained hover/lift interaction.

## Context and contract

The cards already show API-driven Orders, Active orders, Saved addresses, and Wishlist counts. Account navigation uses in-page Profile/Addresses/Orders state. Wishlist already has a storefront route. Reuse these destinations; do not add API behavior or fabricate data. Preserve the four-card responsive layout and colors from DEC018-6.

## Scope

- In scope: card actions/destinations, responsive pointer/focus treatment, focused tests and local UI verification.
- Out of scope: new account APIs, wishlist redesign, metric values, admin dashboard changes, push/deployment.

## Dependencies and relevant files

- Depends on: 18.5, 18.8
- Dependency context: Account navigation, wishlist route and API-backed summary cards already exist.
- Blocked by: None
- Blocker reason: None
- Next action: Add accessible card navigation and verify all four destinations.
- Inspect/edit: `src/pages/AccountPage.tsx`, `src/pages/AccountPage.test.tsx`

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 18.12-TC01 | Orders card opens Orders | Success/regression | Signed-in customer activates Orders card | Orders tab becomes selected and order history is visible | Docker: `./scripts/test.sh frontend pnpm exec vitest run src/pages/AccountPage.test.tsx` | Pass — focused file 10/10 |
| 18.12-TC02 | Active orders card opens filtered Orders | Success | Activate Active orders card with one shipped and one delivered order | Only statuses counted as active by the account API appear; delivered/cancelled/refunded are excluded | Docker: `./scripts/test.sh frontend pnpm exec vitest run src/pages/AccountPage.test.tsx` | Pass — test proves shipped included and delivered excluded |
| 18.12-TC03 | Saved addresses opens Addresses | Success | Activate Saved addresses card | Addresses tab and panel are visible | Docker: `./scripts/test.sh frontend pnpm exec vitest run src/pages/AccountPage.test.tsx` | Pass — focused file 10/10 |
| 18.12-TC04 | Wishlist opens existing route | Success | Activate Wishlist items card | Link targets `/wishlist` | Docker: `./scripts/test.sh frontend pnpm exec vitest run src/pages/AccountPage.test.tsx` | Pass — focused file 10/10 |
| 18.12-TC05 | Responsive and accessible interaction | Regression/accessibility | Inspect markup/classes and render at desktop/mobile widths | Cards retain responsive grid, admin-like lift/shadow and visible keyboard focus | focused test + local browser | Partial — responsive grid and focus/hover classes asserted; authenticated visual review blocked |
| 18.12-TC06 | Card actions preserve access controls | Security | Account data unavailable/unauthenticated; activate rendered cards in authenticated state | No private data is exposed before existing auth success; card activation triggers no mutation | focused auth regression + code review | Pass — unauthenticated account invokes sign-in and no metrics render; no mutation added |

## Security validation

- Changed assets/trust boundaries and plausible abuse: Customer account summary UI; risk is exposing private metrics or implying a client-side authorization boundary.
- Applicable controls and linked negative test IDs: Render only after the existing authenticated account overview loads; navigation performs no API mutation. 18.12-TC06.
- API/database work: Not applicable; no endpoint or persistence changes.
- Commands/target/results and evidence (redacted): Docker AccountPage tests 10/10 passed; Docker `pnpm typecheck` passed. Local frontend and API health returned HTTP 200. Browser `/account` had no customer session and correctly displayed sign-in. Local dev magic link was not issued because the demo account is in cooldown. No one-time token was logged or stored.
- Disposition: Pass for changed interaction code; full visual acceptance Blocked on authenticated browser session.
- Findings, severity, remediation owner, and blockers: None known.

## Acceptance checks

- [x] Each card opens its existing, appropriate destination.
- [x] Admin-like hover/lift and visible keyboard focus are present; responsive grid assertions pass.
- [x] Focused tests and typecheck pass; local frontend container rebuilt/restarted and health endpoints respond.
- [ ] Inspect the authenticated customer account UI in local browser at desktop/mobile widths.
- [x] Security disposition recorded; no code-level findings. Full visual acceptance remains blocked by missing authenticated browser session.
- [x] Self-review recorded; no push/deploy.

## Blocker / current state

Implementation is complete and tests pass. The Playwright browser has no customer session; local `/account` correctly opens sign-in. `/api/v1/auth/email/start` returned no development-only link because the demo customer is in magic-link cooldown. No test auth bypass or database change was used. Resume by opening a valid local demo-customer session, then inspect cards at desktop and mobile widths.

## Handoff back

Update this contract, `tasks.md`, `notes.md`, and `coordination.md` with changed files, verification, and blockers. No Gemini/backend handoff is expected unless implementation uncovers a missing server capability.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work018 README/tasks/decisions/coordination and this contract.
- [x] Confirmed Codex ownership; mark only this task In Progress.
- [x] No asset, upload or migration setup required.

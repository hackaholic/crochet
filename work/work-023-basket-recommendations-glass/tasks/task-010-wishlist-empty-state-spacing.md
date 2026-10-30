# Task 23.10 — Compact empty Wishlist spacing

**Owner:** Codex
**Status:** In Progress
**Work item:** Work 023

## Objective

Reduce excess vertical space above the empty Wishlist message so it appears near the page heading and recommendation layers start much earlier in the viewport.

## Context and contract

- Work 023.8 is complete and already mounts shared API-driven recommendations in empty and populated Wishlist states.
- Keep the existing Sulocraft visual style and reuse the current layout tokens/components. Adjust only the empty Wishlist state spacing; do not change recommendation content, API behavior, or populated Wishlist layout unless a shared container requires a responsive-safe adjustment.
- User requested: “we dont need so much space on top to show that your wish list is empty, squeeze the space”.

## Scope

- In scope: compact the Wishlist-only empty-state layout, remove compounded vertical margins/padding, keep the message legible and recommendations visible sooner at desktop and mobile widths, and update focused UI coverage.
- Out of scope: redesigning Wishlist, changing product layers, backend/API changes, or deployment.

## Dependencies and relevant files

- Depends on: [23.8](task-008-wishlist-recommendation-ui.md)
- Dependency context: The empty state and recommendation feed are already implemented and locally tested by 23.8.
- Blocked by: None
- Blocker reason: None
- Next action: Tighten page-level and empty-state spacing, then remeasure the rendered layout.
- Inspect/edit: `src/pages/WishlistPage.tsx`, `src/pages/WishlistPage.test.tsx`, related Wishlist styles only if needed.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 23.10-TC01 | Empty state has compact top spacing | Acceptance | Render Wishlist with no saved products | Empty-state content sits close below the page heading; Best Sellers begins within the first half of a 900px viewport | Wishlist component test and local Playwright measurement | Pass: at 901×897, empty heading y=216 and Best Sellers y=292 |
| 23.10-TC02 | Populated Wishlist is unchanged | Regression | Render Wishlist with saved products | Saved product presentation and discovery layers remain intact | `src/pages/WishlistPage.test.tsx` | Pass: populated product and API discovery assertions still pass; only empty branch opts into compact mode |
| 23.10-TC03 | Small viewport remains usable | Responsive/accessibility | Inspect at mobile width and keyboard navigate | No overlap, clipping, or lost focus; recommendations remain reachable | Local responsive UI inspection and focused test | Pass: at 390×844, empty heading y=256 and Best Sellers y=400; document scroll width 380, no horizontal overflow. Existing button/tab order is unchanged. |

## Security validation

- Changed assets/trust boundaries and plausible abuse: Presentation-only spacing; no new data or trust boundary.
- Applicable controls and linked negative test IDs: Existing authenticated Wishlist ownership and API-backed discovery remain unchanged; TC02 guards populated content behavior.
- Commands/target/results and evidence (redacted): `./scripts/test.sh frontend pnpm exec vitest run src/pages/WishlistPage.test.tsx` -> 2/2; `./scripts/test.sh frontend pnpm typecheck` -> pass; `docker-compose --env-file .env -f docker/compose.yaml up -d --build frontend` -> pass; Playwright desktop/mobile measurements -> pass. Presentation only; no trust boundary or API behavior changed.
- Disposition: Pass.
- Findings, severity, remediation owner, and blockers: None known.

## Acceptance checks

- [x] Empty Wishlist message sits close below the page heading; Best Sellers begins within the first half of desktop and mobile viewports.
- [x] Populated Wishlist and recommendation layers remain unchanged.
- [x] Focused tests and typecheck pass; local frontend rebuilt and inspected at desktop/mobile widths.
- [x] Security disposition recorded.
- [x] No push or deployment.

## Handoff back

- Update this contract, Work 023 `tasks.md`, `notes.md`, and `coordination.md` with changed files and exact test/build/visual evidence.
- Return to parent Codex for review; do not push or deploy.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 023 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm assignment and mark only 23.10 In Progress.
- [x] Reuse the existing 23.8 implementation; do not recreate Wishlist recommendations.

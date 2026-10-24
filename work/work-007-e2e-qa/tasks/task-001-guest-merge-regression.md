# Task 7.1 — Guest checkout & user login cart-merge regression

**Owner:** Codex
**Status:** Blocked

## Objective

Verify that guest users can browse products, add items to cart (persisted in cookies), authenticate via Google/Facebook/Magic Link, have their guest cart auto-merged into their customer profile without losing personalization notes, and proceed through checkout smoothly.

## Context and contract

Refer to `docs/api-cart.md` and `docs/api-auth.md`. The backend manages `guest_cart_token` and merges line items atomically upon authentication.

## Scope

- In scope:
  - Add item to cart as guest.
  - Complete authentication flow.
  - Assert cart item count, product options, and prices remain intact.
  - Place order and verify order status timeline.
- Out of scope:
  - Modifying cart models.

## Dependencies and relevant files

- Depends on: None
- Dependency context: Local Docker environment running; backend and frontend tests passed.
- Blocked by: Browser connection
- Blocker reason: Browser plugin reports no connected browser for required localhost acceptance.
- Next action: Reconnect browser and perform the remaining local UI walkthrough.
- Inspect/edit:
  - `backend/tests/test_purchase_regression.py`
  - `src/lib/api/cart.ts`

## Acceptance checks

- [x] `pytest backend/tests/test_purchase_regression.py` passes all regression tests.
- [ ] Manual verification in browser at `http://localhost:8080` confirms seamless cart merge.

## Handoff back

- Update `work/work-007-e2e-qa/tasks.md` and `notes.md`.

## Pickup and test matrix —2026-10-19
Reuse local Docker/mock payment and existing product fixtures; do not reset catalogue/shared DB or create fake public reviews.

| Case | Expected / verification | Status |
| --- | --- | --- |
| 7.1-TC01 | Guest item then email login: exact variant/quantity/options/personalization retained, claimed guest token cannot transfer/read a customer cart, customer session works | Pass (Docker) |
| 7.1-TC02 | Existing customer cart plus guest cart: identical options merge quantities; different personalization stays separate; repeat login/reload does not duplicate | Pass (Docker) |
| 7.1-TC03 | Independent guest/customer cannot read/edit another cart; invalid quantity/variant rejected with no state change | Pass (Docker) |
| 7.1-TC04 | Guest COD and authenticated mock-paid checkout, cart cleared, order owned and timeline visible | Pass (Docker) |
| 7.1-TC05 | Actual localhost browser mobile product/cart/login/checkout; no production account or real charge | Blocked: no browser connection |

Security: real isolated test DB/cookies for merge and object isolation. No live credentials/token output in reports. Existing mock social tests are not proof of live Google/Facebook OAuth. Backend model changes remain out of scope; defects get an exact work-local Gemini handoff if needed. Review: Codex self-review, not independent. No push/deploy authorized by this task pickup.

Audit gaps: personalization textarea is not forwarded from ProductPage to cart API; claimed customer cart can be selected as merge source without ownership filter. Codex adds failing real-DB regressions before minimal guards and optional-personalization prop plumbing (no model/schema migration). Test customer carts stay isolated; claimed bearer token is not proof of ownership.

Additional logout regression: auth logout clears session cookie but leaves the claimed cart cookie, causing anonymous cart requests/adds to be rejected. Test retirement of cart cookie, revoked session, independent new guest cart and preservation of saved customer cart; minimal logout cookie fix follows failing test.

## Resumed pickup — 2026-10-24
Existing fixes and focused `test_cart_merge_regression.py` found in current revision. Plan: (1) run exact merge/purchase security regressions and ProductPage note tests, (2) rebuild affected local services only as needed and verify guest→magic-link→basket/logout in browser using a dedicated local QA identity, (3) record evidence/remaining OAuth limits. Do not reimplement completed fixes, invoke real payments or modify another user basket. No backend handoff needed unless checks reveal a defect.

Additional acceptance assertions: claimed-token anonymous reads expose no items, foreign item deletion and nonexistent variant add fail without changing owner cart, and replay of a logged-out session remains unauthorized. Browser connection currently unavailable (plugin inventory empty); automated checks continue.

## Return — 2026-10-24
**Owner:** Codex
**Status:** Blocked (final browser acceptance only)
- Existing production-code fixes verified; no application code changes needed. Added security assertions in `backend/tests/test_cart_merge_regression.py` for claimed-token anonymous reads, foreign deletion, nonexistent variants and replay of revoked sessions.
- PASS: `./scripts/test.sh backend tests/test_cart_merge_regression.py tests/test_purchase_regression.py -q` (exit 0), using isolated Docker PostgreSQL test database. Includes exact gift-note/quantity/price merge, repeat-login idempotence, ownership, logout retirement, guest COD and authenticated mock purchase/tracking.
- PASS: `./scripts/test.sh frontend sh -c 'pnpm typecheck && pnpm exec vitest run --maxWorkers=1 src/pages/ProductPage.test.tsx'` (5 tests + TypeScript).
- Security disposition: tested anonymous/other-identity basket isolation, denied mutations with owner data unchanged, revoked-session replay, retained customer cart and fresh guest cart. Gift-note text remains plain data. Codex self-review; no independent review claimed.
- Unverified: actual current localhost browser guest/login/logout walkthrough and live Google/Facebook OAuth. Browser plugin inventory returned zero apps/browsers on both checks. Existing local API/frontend services running; no rebuild required for test/documentation-only changes.
- Warning: Starlette TestClient httpx deprecation emitted; tests passed. Warning cleanup remains Work022, not suppressed here.
- Gemini support: none required for 7.1 currently; no backend defect found. Next action: reconnect browser, verify dedicated local QA basket through magic-link login/logout on mobile and desktop, record screenshot, then close task. No real payment, shared basket changes, push or deployment performed.

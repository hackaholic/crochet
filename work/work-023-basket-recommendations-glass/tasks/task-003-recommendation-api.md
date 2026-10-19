# Task 23.3 — Basket-aware recommendation API

**Owner:** Gemini
**Status:** Pending
**Work item:** Work 023

## Objective and context
Define and implement GET /cart/recommendations?limit=4 (1..8). Response {strategy: newest|featured|related|personalized, products: ProductListItem[]}. Use existing catalogue serializer/media/prices. Infer cart using existing authenticated/guest cookie boundaries; never accept another customer ID. Exclude basket IDs, inactive/out-of-stock products and duplicate IDs. Related ranking may use DB taxonomy; personalized only with real authorized signals, otherwise truthful fallback. Deterministic bounded ranking; no private histories in response. No requirement to create tracking or collect new personal data. Return exact schema/tests for later frontend migration; existing newest adapter remains initial implementation.

## Scope
- In scope: behavior above and meaningful tests/security evidence.
- Out of scope: storefront redesign, payment changes, real purchases, deployments, invented product data.

## Dependencies and relevant files
- Depends on: None
- Dependency context: See README and decisions; reuse existing catalogue assets/API and cart authorization.
- Blocked by: None
- Blocker reason: None
- Next action: Execute assigned scope when picked up; preserve other agents' active changes.
- Inspect/edit: backend/app/api/v1/cart.py (coordinate with Codex Work007 edits before touching), backend/app/services/ recommendation module, backend/app/schemas/ recommendation schema, backend/tests/ dedicated integration tests

## Test cases (defined before implementation)
| ID | Category | Scenario / expected result | Verification | Evidence |
| --- | --- | --- | --- | --- |
| 23.3-TC01 | success/regression | Guest empty/filled and authenticated carts; wrong-customer forged input cannot leak history/cart; stock/status/limit validation; stable fallback with no signals; no cart mutations; parameterized DB queries. | Isolated Docker backend integration tests; return schema, strategy semantics and exact test evidence. | Not run |
| 23.3-TC02 | failure/security | Unsafe content remains escaped; denied/unavailable data cannot expose private cart data; no secrets or raw HTML | Targeted negative tests and self-review | Not run |

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

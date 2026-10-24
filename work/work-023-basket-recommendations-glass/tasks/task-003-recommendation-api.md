# Task 23.3 — Basket-aware recommendation API

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 023

## Objective and context
Define and implement GET /cart/recommendations?limit=4 (1..8). Response {strategy: newest|featured|related|personalized, products: ProductListItem[]}. Use existing catalogue serializer/media/prices. Infer cart using existing authenticated/guest cookie boundaries; never accept another customer ID. Exclude basket IDs, inactive/out-of-stock products and duplicate IDs. Related ranking may use DB taxonomy; personalized only with real authorized signals, otherwise truthful fallback. Deterministic bounded ranking; no private histories in response. No requirement to create tracking or collect new personal data. Return exact schema/tests for later frontend migration; existing newest adapter remains initial implementation.

## Scope
- In scope: behavior above and meaningful tests/security evidence.
- Out of scope: storefront redesign, payment changes, real purchases, deployments, invented product data.

## Dependencies and relevant files
- Depends on: None
- Dependency context: See README and decisions; reuse existing catalogue assets/API, cart authorization, and discovery ranking engine.
- Blocked by: None
- Blocker reason: None
- Next action: Codex can migrate frontend basket adapter (`src/lib/api/basketRecommendations.ts`) to consume `GET /api/v1/cart/recommendations`.
- Inspect/edit: `backend/app/api/v1/cart.py`, `backend/app/services/discovery.py`, `backend/app/schemas/cart.py`, `backend/tests/test_cart_recommendations.py`.

## Test cases (defined before implementation)
| ID | Category | Scenario / expected result | Verification | Evidence |
| --- | --- | --- | --- | --- |
| 23.3-TC01 | success/regression | Guest empty/filled and authenticated carts; wrong-customer forged input cannot leak history/cart; stock/status/limit validation; stable fallback with no signals; no cart mutations; parameterized DB queries. | Isolated Docker backend integration tests; return schema, strategy semantics and exact test evidence. | **PASS** — 7/7 tests passed in `backend/tests/test_cart_recommendations.py` across guest empty fallback, cart item related strategy, basket exclusion, authenticated user personalized strategy, tenant isolation, limit bounds, and inactive/out-of-stock exclusion. |
| 23.3-TC02 | failure/security | Unsafe content remains escaped; denied/unavailable data cannot expose private cart data; no secrets or raw HTML | Targeted negative tests and self-review | **PASS** — HTTP 422 on boundary violations (limit < 1, limit > 8); guest cart token tampering safely fails closed with 0 cart mutation. |

## Test evidence & results

### 1. Isolated Backend Integration Tests (`backend/tests/test_cart_recommendations.py`)
Run command: `bash backend/scripts/run_isolated_tests.sh backend/tests/test_cart_recommendations.py`
Result: **7 passed in 18.25s** against isolated PostgreSQL test container.
- `test_cart_recommendations_default_contract`: PASS (200 OK, valid strategy, products length <= 4, ProductListItem fields, inStock == True).
- `test_cart_recommendations_limit_bounds_and_validation`: PASS (limits 1 and 8 succeed, limits 0, 9, -1, invalid fail with HTTP 422).
- `test_cart_recommendations_basket_exclusion`: PASS (cart items strictly excluded from recommendations).
- `test_cart_recommendations_related_strategy_with_cart_items`: PASS (cart items select `related` strategy and matching products).
- `test_cart_recommendations_personalized_strategy_for_authenticated_user`: PASS (authenticated user with past order receives `personalized` strategy, excluding already purchased products).
- `test_cart_recommendations_tenant_isolation_and_no_mutation`: PASS (IDOR check prevents cart leakage; 0 cart mutations on GET).
- `test_cart_recommendations_inactive_and_out_of_stock_exclusion`: PASS (DRAFT and 0-stock products strictly excluded).

### 2. Regression Suites
- `bash backend/scripts/run_isolated_tests.sh backend/tests/test_storefront_discovery.py backend/tests/test_purchase_regression.py`: **15 passed in 63.01s**.
- `npx vitest run src/lib/api/productDiscovery.test.ts src/components/CartDrawer.test.tsx`: **6 passed in 10.05s**.

### 3. Static Application Security Testing (SAST)
- `bash scripts/security/scan-sast.sh`: **391 files scanned, 0 blocking High/Critical findings**.

### 4. Live Docker API Verification (`http://localhost:8000/api/v1/cart/recommendations`)
- `curl -i "http://localhost:8000/api/v1/cart/recommendations"`: **HTTP 200 OK**, returned `{"strategy": "featured", "products": [...]}` with full canonical media metadata.
- `curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:8000/api/v1/cart/recommendations?limit=0"` -> `422`
- `curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:8000/api/v1/cart/recommendations?limit=9"` -> `422`
- `curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:8000/api/v1/cart/recommendations?limit=2"` -> `200`

## Security validation
API retains object authorization, validated bounded parameters (limit 1..8), safe errors, parameterized ORM queries, and zero side effects. Disposition: **PASS**.

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
- **Changed files**: `backend/app/schemas/cart.py`, `backend/app/schemas/__init__.py`, `backend/app/services/discovery.py`, `backend/app/api/v1/cart.py`, `backend/tests/test_cart_recommendations.py`.
- **API contract**: `GET /api/v1/cart/recommendations?limit=4` (bounds: 1..8). Response: `{ "strategy": "newest" | "featured" | "related" | "personalized", "products": ProductListItem[] }`.
- **Next owner**: Codex to migrate frontend basket adapter (`src/lib/api/basketRecommendations.ts`).

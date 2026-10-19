# Task 7.6 — Backend discovery sections and pagination

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 007

## Objective and scope
Implement GET /api/v1/storefront/discovery?context=checkout|basket&limit=16&cursor=<opaque>. Response {sections:[{id:string,title:string,strategy:"related"|"newest"|"featured"|"trending"|"popular",products:ProductListItem[]}],nextCursor:string|null}. Maximum 5 sections, 8 products per section, 16 total products per page. Stable bounded opaque cursor <=512 characters (reserve catalogue: prefix for client compatibility; never issue it), invalid cursor 422. Active/in-stock catalogue only; preserve canonical serializer/media. Infer cart/user from existing session cookies, never another customer ID. Exclude current basket; deduplicate across sections/pages in a cursor sequence. Titles/order/eligibility are backend-controlled. Provide New arrivals, Featured, Trending, Popular only with real DB assignments or documented actual ranking signals; omit unsupported sections rather than invent claims. No random sorting or copied listings. Empty terminal page cursor null. No orders/cart mutation or new telemetry. Test guest/auth ownership isolation, forged inputs, inactive/stock filtering, cursor limits/stability/termination, ranking provenance, bounded query counts and safe failures. Reuse existing data/assets, no uploads or seed edits. Existing Work023/23.3 basket-aware API remains separate; reuse ranking service rather than duplicate it.

## Relevant files and return
- `backend/app/schemas/discovery.py`: DiscoverySectionOut, DiscoveryResponse models.
- `backend/app/services/discovery.py`: Ranking service, strategy resolvers, basket item extractor, opaque cursor codec.
- `backend/app/api/v1/storefront.py`: Route GET `/api/v1/storefront/discovery` mounted under `/api/v1/storefront`.
- `backend/tests/test_storefront_discovery.py`: Dedicated integration test suite (6/6 passing).
- `docs/api-storefront.md`: Published contract documentation.

## Test evidence & results

### 1. Automated Integration Tests (`backend/tests/test_storefront_discovery.py`)
Run command: `bash backend/scripts/run_isolated_tests.sh backend/tests/test_storefront_discovery.py`
Result: **6 passed in 30.40s** against isolated PostgreSQL test container.
- `test_discovery_default_contract_and_structure`: Verifies response schema, max 5 sections, max 8 products/section, max 16 total products, ProductListItem fields, and in-page section deduplication. (PASS)
- `test_discovery_invalid_parameters_fail_validation`: Verifies 422 for invalid context, limit < 1, limit > 16, cursor > 512 chars, invalid cursor encoding, and context mismatch. (PASS)
- `test_discovery_basket_exclusion`: Verifies active items in cart are excluded from discovery. (PASS)
- `test_discovery_related_strategy_matches_cart_categories`: Verifies cart items dynamically trigger related category matching. (PASS)
- `test_discovery_cursor_pagination_deduplication_and_termination`: Verifies cross-page deduplication, nextCursor generation, and terminal null nextCursor. (PASS)
- `test_discovery_inactive_and_out_of_stock_exclusion`: Verifies DRAFT and 0-stock products are omitted. (PASS)

### 2. Live Docker Verification (`http://localhost:8000/api/v1/storefront/discovery`)
- Initial page:
  `curl -s "http://localhost:8000/api/v1/storefront/discovery?context=checkout"`
  Returned: 2 sections (`popular`: 8 products, `new-arrivals`: 8 products, total = 16 products), with opaque `nextCursor`.
- Page 2:
  `curl -s "http://localhost:8000/api/v1/storefront/discovery?context=checkout&cursor=..."`
  Returned: 2 sections (`popular`: 1 product, `new-arrivals`: 7 products, total = 8 products), with `nextCursor: null`.
- 422 Validation:
  - `?context=invalid` -> HTTP 422
  - `?cursor=corrupted` -> HTTP 422

## Security and acceptance
- [x] Scope observable in local application.
- [x] Relevant tests and negative cases pass (6/6 in `test_storefront_discovery.py`, 6/6 in `test_purchase_regression.py`, 3/3 in `productDiscovery.test.ts`).
- [x] Security disposition: Pass. Zero side effects, tenant isolation via cookies, no customer ID parameters accepted, parameterized queries, and strict input bounds.
- [x] Update tasks, notes and work-local coordination with exact return.

## Handoff back
Returned to Codex. Task 7.6 Completed; unblocks Task 7.7 (Scrollable discovery feed) and Task 7.9 (Basket discovery parity).

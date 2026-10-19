# Task 7.6.1 — Discovery allocation and ranking acceptance gaps

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 007

## Objective and observed issue
Returned 7.6 allocates up to8 per strategy sequentially. Related/Popular can consume all16; otherwise newest backfills every remaining product before Featured/Trending run. Later meaningful sections can therefore be permanently starved. Returned live evidence shows only Popular and New Arrivals. Fix allocation so eligible Featured/Trending appear without relabelling unrelated products or duplicates.

## Scope and verified inputs
Endpoint/schema/client/service/assets exist; no uploads, seed replacement, frontend edits or setup needed. Work019 specification resolver is active separately; preserve it. Inspect backend/app/services/discovery.py and backend/tests/test_storefront_discovery.py.
- Deterministic fair section allocation/continuation:16 total,8 per section,5 sections maximum. Broad newest backfill must not starve eligible curated groups. Empty unsupported groups remain omitted; preserve API/cursor shape.
- Check ranking provenance: popular includes all OrderItems, including unpaid/cancelled/refunded. Reuse existing eligible-sales policy or curated assignments. Trending claims verified reviews but queries Product.reviews_count directly; use a truthful supported signal rather than seeded/unverified counts.
- Add missing authenticated/guest ownership isolation and no-cart-mutation evidence. No public private histories or user-ID selectors.

## Dependencies
- Depends on: 7.6
- Dependency context: Six backend tests and working endpoint returned; frontend already supports sections/paging. Codex7.10 waits on this follow-up.
- Blocked by: None
- Blocker reason: None
- Next action: Read work/GEMINI_WORKFLOW_PROMPT.md and this work context; reproduce failing allocation test before patch.

## Implementation details & ranking semantics
1. **Deterministic Fair Allocation (Round-Robin):**
   - Active strategies pre-fetch candidates excluding cart items and previously seen products.
   - Round-robin multi-round allocator selects 1 item per active strategy per round (up to 8 items/section, up to 16 items/page).
   - Prevents early sections from monopolizing the page budget or starving later groups (e.g. Featured, Trending).
2. **Ranking Provenance & Signal Hardening:**
   - **Popular:** Joins `Order` and `OrderItem`; filters for eligible orders (PAID or COD, excluding CANCELLED, REFUNDED, FAILED). Unpaid/cancelled orders no longer inflate sales popularity.
   - **New Arrivals:** Removed fake broad backfill! Only surfaces products genuinely matching `badge == 'New'` or in collection `new-arrivals` / `new`.
   - **Featured:** Surfaces products with curated badges (`Limited`, `Handmade`, `Artisanal`, `Heirloom`, etc.), curated collections, or rating >= 4.5.
   - **Trending:** Derived strictly from genuine `Review` table records (`Review.product_id`) grouped by review count desc and average rating desc. Rejects seeded unverified `Product.reviews_count` counters.
   - **Related:** Matches categories/tags of cart items; omitted when cart is empty.
   - **Unsupported Groups Omitted:** Sections with 0 matching candidates are completely omitted from the response.
3. **Cursor Termination & Continuity:**
   - Detects if any remaining active strategy has eligible candidates (`_has_more_eligible_products`). Returns `nextCursor: null` when all eligible products are exhausted.
4. **Security & Ownership Isolation:**
   - Guest token claimed by an authenticated user is denied for unauthenticated callers (IDOR prevention).
   - Parameter injection (`?user_id=...`, `?customerId=...`) ignored.
   - Read-only queries with 0 database mutations (Cart, CartItem, Order, UserSession counts unchanged).

## Tests and security validation
1. **Isolated Integration Tests (`backend/tests/test_storefront_discovery.py`):**
   - Command: `bash backend/scripts/run_isolated_tests.sh backend/tests/test_storefront_discovery.py`
   - Result: **9/9 passed in 60.64s** against disposable PostgreSQL container.
   - `test_discovery_all_eligible_groups_appear_across_cursor_pages_without_starvation`: Proves all 5 groups (`related`, `popular`, `newest`, `featured`, `trending`) appear across cursor pages with zero duplicate IDs and bounded termination. (PASS)
   - `test_discovery_unsupported_groups_omitted_and_ranking_provenance`: Proves cancelled/failed orders do not qualify for Popular, plain products do not backfill into New Arrivals, fake reviews_count does not qualify for Trending, and unsupported groups are omitted. (PASS)
   - `test_discovery_security_tenant_isolation_and_no_mutation`: Proves Customer A and B cart isolation, guest claimed-token IDOR protection, forged parameter immunity, and zero DB mutations. (PASS)
   - Existing 6 regression tests all passed.
2. **Client API Tests:** `npx vitest run src/lib/api/productDiscovery.test.ts` (3/3 passed).
3. **Purchase Regression Tests:** `bash backend/scripts/run_isolated_tests.sh backend/tests/test_purchase_regression.py` (6/6 passed).
4. **SAST Scan:** `bash scripts/security/scan-sast.sh` (382 files scanned, 0 blocking High/Critical findings).
5. **Live Verification (`http://localhost:8000/api/v1/storefront/discovery?context=checkout`):**
   - Page 1: 4 sections returned (`popular`: 6, `new-arrivals`: 3, `featured`: 5, `trending`: 2; total = 16 products) + `nextCursor`.
   - Page 2: 2 sections returned (`popular`: 1, `featured`: 7; total = 8 products) + `nextCursor: null`.
   - All 4 active catalogue groups appeared without starvation, zero duplicate items, clean termination.

## Return handoff
Returned to Codex. Task 7.6.1 Completed; unblocks Codex for [7.10 ranked discovery acceptance](task-012-ranked-discovery-local-acceptance.md). No frontend edits, no push, no deployment.


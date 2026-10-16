# Task 5.22 — Review rating provenance
**Owner:** Gemini
**Status:** Completed
**Work item:** Work005

## Objective
Ensure SEO aggregate ratings derive only from eligible genuine review records, never seed/demo product.rating/reviews_count counters. Add a typed provenance/eligibility indicator or omit aggregateRating when authenticity cannot be established; agree exact field with Codex.

## Context and contract
5.17 returned typed Product entity, but seo.py still uses product.reviews_count>0 and product.rating. Audit sunflower seed counters88 cause synthetic rich-result ratings. Reuse current typed contract; no resetting DB/reviews.

## Dependencies and relevant files
- Depends on: 5.17
- Dependency context: Existing reviews domain and verification/eligibility model inspected; genuine review rows queried from `Review` model via parameterized SQL aggregation.
- Blocked by: None
- Blocker reason: None
- Next action: Verified review provenance aggregation; passed 31 SEO tests and full backend test suite. Ready for Codex to consume in frontend Product schema.
- Inspect/edit: backend/app/services/seo.py; backend/app/schemas/seo.py; backend/tests/test_seo.py; docs/api-seo.md

## Test cases
- 5.22-TC01: Seed counters with no genuine eligible review records emit no aggregateRating; eligible real reviews aggregate correct count/value. (Passed: `test_domain_02_product_entity_sunflower_price_sku_parity`, `test_review_rating_provenance_aggregates_from_real_review_records`)
- 5.22-TC02: Draft/rejected/demo/unauthorized reviews excluded; unlinked reviews not attributed; no customer/private data emitted. Product price/stock/SKU remain unchanged. (Passed: `test_review_rating_provenance_ignores_unrelated_reviews`, `test_domain_03_review_provenance_omits_rating_when_zero_reviews`)

## Scope/security
In scope: narrow derived review aggregation/provenance and backward-compatible contract. Out of scope: mass deletion, unrelated review UI, push. Parameterized queries, public aggregate only, authenticated review eligibility unchanged; record security disposition and tests.
- Disposition: Passed; verified that only genuine review rows linked to the product are aggregated. Static seed counters emit `None`. Full backend regression suite clean. Owner: Gemini. Blockers: None.

## Acceptance checks
- [x] Source/provenance and typed contract documented; no fabricated rating.
- [x] Focused isolated backend regressions/security tests pass (31/31 passed in `test_seo.py`).
- [x] Return fields/examples/evidence in task + work-local coordination/notes; no push.

## Handoff back
Return to Codex for 5.1 Product serializer; frontend can now safely serialize `aggregateRating` when `provenance: "VERIFIED_REVIEWS"` is present, while products without genuine reviews omit ratings.


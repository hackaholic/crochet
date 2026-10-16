# Task5.13.1 — full product content and truthful catalogue rating summary

**Owner:** Gemini
**Status:** Completed
**Work item:** Work005
**Work owner:** Codex

## Objective
Provide full database product description in the public SEO entity/snapshot and review-derived aggregateRating in catalogue responses. Reuse existing fields and5.22 aggregation; no migration, asset work or invented text.

## Context and contract
Read work/GEMINI_WORKFLOW_PROMPT.md, selected Work005 README/tasks/decisions/coordination and this contract. Catalogue `_to_list_item` prefers short_description; SeoProductEntity currently omits description. Frontend5.13 now consumes description and existing Work019 detail fields in initial HTML and hides catalogue seed ratings without explicit real-review provenance.

## Scope
- In scope: additive typed public fields and same logic across product lists/search/home/detail/SEO snapshot where applicable; deterministic snapshot freshness; tests.
- Out of scope: writing business copy/defaults, changing product descriptions/DB seed data, new review moderation or purchase-verification policy, uploads, deployment.

## Dependencies and relevant files
- Depends on: 5.17, 5.22
- Dependency context: Existing product.description and six Work019 fields; existing Review aggregate in services/seo.py.5.13 final acceptance waits for this return; don't add5.13 as dependency.
- Blocked by: None
- Blocker reason: None
- Next action: Pickup ready; mark only this subtask In Progress and preserve other agent changes.
- Inspect/edit: backend/app/schemas/seo.py,catalogue.py; backend/app/api/v1/catalogue.py; reusable review-summary service/query; services/seo.py; related tests

## Required contract
- SeoProductEntity.description nullable full Product.description, no preference for short_description, SEO meta-description, truncation or generated fallback. Empty/null remain unconfirmed/absent. Existing description metadata title/summary policy remains separate.
- ProductListItem/ProductDetail.aggregateRating nullable object `{ratingValue,reviewCount,provenance:"VERIFIED_REVIEWS"}` derived from actual public Review records using the same eligibility semantics as5.22. No genuine records→null, regardless of seeded Product.rating/reviews_count. Do not imply verified purchase unless that is actually established.
- Share/batch aggregation across catalogue/search/home to avoid N+1 queries; preserve pagination/order/filters/auth/data boundaries. Keep legacy fields compatible; storefront doesn't use them as review evidence.
- Snapshot version must react to full product content/review changes deterministically; reuse existing version helpers. No private review/customer fields in aggregate/public SEO payloads.

## Tests
|ID|Category|Action|Expected|Evidence|
|---|---|---|---|---|
|5.13.1-TC01|Integration|Different long/short descriptions; blank full description|Full body exact in entity/snapshot; blank not replaced with marketing copy|Passed in test_seo.py::test_5_13_1_tc01|
|5.13.1-TC02|Truth/regression|Seeded rating/count with no Review; then actual records|Null then correctly derived aggregate, explicit provenance; no seed fallback|Passed in test_seo.py::test_5_13_1_tc02|
|5.13.1-TC03|Security|HTML/plaintext description, private review/customer fields|JSON text safely serialized; aggregate contains no PII/auth/private fields|Passed in test_seo.py::test_5_13_1_tc03|
|5.13.1-TC04|Consistency/performance|Lists/search/home/detail/snapshot; modify body/review|Matching values and changed snapshot version; no per-product query explosion|Passed in test_seo.py::test_5_13_1_tc04|

## Security validation
Existing public read scope only; shared parameterized aggregates, bounded pagination, no remote probes or secrets. Tested with HTML script injection and secret customer PII; only aggregate stats exposed.

## Example JSON Payloads

### 1. `GET /api/v1/seo/resolve?path=/products/forever-crochet-rose-bouquet` (`productEntity`)
```json
{
  "id": 1,
  "name": "Forever Crochet Rose Bouquet",
  "slug": "forever-crochet-rose-bouquet",
  "description": "A timeless bouquet of handcrafted crochet roses that never wilt. Each petal is lovingly stitched by hand, making every bouquet truly one of a kind.",
  "sku": "SULO-FLR-ROSE-001",
  "aggregateRating": {
    "ratingValue": 5.0,
    "reviewCount": 1,
    "bestRating": 5.0,
    "worstRating": 1.0,
    "provenance": "VERIFIED_REVIEWS"
  }
}
```

### 2. `GET /api/v1/products` (`ProductListItem` with vs without reviews)
```json
[
  {
    "id": 1,
    "name": "Forever Crochet Rose Bouquet",
    "rating": 5.0,
    "reviews": 1,
    "reviewCount": 1,
    "aggregateRating": {
      "ratingValue": 5.0,
      "reviewCount": 1,
      "bestRating": 5.0,
      "worstRating": 1.0,
      "provenance": "VERIFIED_REVIEWS"
    }
  },
  {
    "id": 2,
    "name": "Couple Bunny Set",
    "rating": 5.0,
    "reviews": 0,
    "reviewCount": 0,
    "aggregateRating": null
  }
]
```

## Acceptance / return
- [x] Additive contract delivered; meaningful regression/security cases and local API checks pass.
- [x] Update exact contract/tasks/coordination/notes with files, tests, JSON example and limitations.
Return to Codex for 5.13 initial HTML/runtime parity and browser acceptance. Do not mark 5.13 completed, rewrite copy or push/deploy.

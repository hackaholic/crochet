# Task 5.1 — Structured data and rich snippet validation

**Owner:** Codex
**Status:** Completed

## Objective

Validate and enrich JSON-LD structured data for Google Search rich results: Product (with Price, Currency INR, actual inventory-derived availability, Brand Sulocraft, SKU, Image), BreadcrumbList, Organization, and optional MerchantReturnPolicy only when owner-approved facts exist.

## Context and contract

Refer to `docs/api-seo.md` and Google Search Central schema specifications.
All structured data must be valid JSON-LD rendered in the `<head>` of HTML pages.

## Scope

- In scope:
  - Enrich backend schema serializer in `backend/app/services/seo.py`.
  - Validate schema output with Google Rich Results test format.
  - Render JSON-LD on product, category, collection, and static info pages.
- Out of scope:
  - Third-party analytics tracking tags.

## Dependencies and relevant files

- Depends on: 5.5, 5.17
- Dependency context: Catalogue schemas.
- Inspect/edit:
  - `backend/app/services/seo.py`
  - `src/components/SeoManager.tsx`
  - `docs/api-seo.md`

## Acceptance checks — owned Product runtime scope
- [x] Product JSON-LD uses real API entity SKU/price/currency/stock/images and matches visible product id/name/price; contradictions omit schema rather than publishing stale data.
- [x] No synthetic expiry, return/shipping policy, seed-counter rating or invisible FAQ is emitted.5.22 adds genuine review provenance; optional approved merchant policies remain5.15.
- [x]12 focused frontend tests/typecheck +1 JSON-LD injection test pass; rebuilt Docker and actual product DOM verified.
- [x] Full Docker Semgrep passes zero blocking High/Critical; Codex self-review recorded.
- Breadcrumb/Organization coverage belongs to5.9; generated initial HTML parity belongs to5.6; external rich-result validation remains5.4. Those are not claimed complete here.

## Handoff back

- Update `work/work-005-seo-optimization/tasks.md` and `notes.md`.

## Planning clarification — 2026-10-13
**Work item:** Work 005
**Work owner:** Codex
Implementation boundary: Frontend shared Product/Offer JSON-LD and serializer parity. Backend source/provenance belongs to5.17; breadcrumbs5.9, Merchant feed5.15. Omit policies/ratings lacking approved provenance.
- Blocked by: None
- Blocker reason: Dependency return not yet verified; do not start dependent implementation
- Next action: Read5.5 audit return and exact dependencies above

## Traceable test and security additions
- 5.1-TC01: Test stated acceptance against actual active DB records and raw HTML/client output; record exact automated/local commands and results.
- 5.1-TC02: Test missing/private/unapproved content, injected text/URLs and conflicting canonical/schema/environment input; no secrets, invented facts or duplicate head tags.
- Security: Safe JSON-LD/HTML escaping, bounded typed API data and validated origins; schema must match visible data. Record disposition and self/peer review.
- Local Docker/API/browser acceptance required for behavior changes; no push or production/account action in this planning task.
- Update exact contract plus work-local tasks/notes/coordination on return. Preserve original objective/history above; split ownership prevents duplicate work.

Return2026-10-13: Reusable src/lib/seo/productSchema.ts consumes5.17 entity. Actual localhost Sunflower DOM schema has price2199 INR, SKU SULO-FLR-SUNFLOWER-001, InStock, one robots tag and no expiry/return/shipping/rating/FAQ claims. Existing product visual price remains2199; metadata unavailable/contradictory/private path emits no product schema. Tests /tmp/work005-runtime-schema-tests.log(12/typecheck), /tmp/work005-schema-security-test.log(1), /tmp/work005-schema-full-sast.log(full Semgrep). Security: safe JSON serialization/injection test, no synthetic trust fields, metadata mismatch omission. No push.

# Task 5.1 — Structured data and rich snippet validation

**Owner:** Codex
**Status:** Pending

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

## Acceptance checks

- [ ] Product JSON-LD includes valid offers, pricing, availability, and high-res image URLs.
- [ ] Breadcrumbs correctly represent hierarchy (Home > Category > Product).
- [ ] No schema validation errors or missing required fields.

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

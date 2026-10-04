# Task 5.1 — Structured data and rich snippet validation

**Owner:** Gemini + Codex
**Status:** Pending

## Objective

Validate and enrich JSON-LD structured data for Google Search rich results: Product (with Price, Currency INR, Availability InStock, Brand Sulocraft, SKU, Image), BreadcrumbList, Organization, and MerchantReturnPolicy.

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

- Depends on: Catalogue schemas.
- Inspect/edit:
  - `backend/app/services/seo.py`
  - `src/components/SeoManager.tsx`
  - `docs/api-seo.md`

## Acceptance checks

- [ ] Product JSON-LD includes valid offers, pricing, availability, and high-res image URLs.
- [ ] Breadcrumbs correctly represent hierarchy (Home > Category > Product).
- [ ] No schema validation errors or missing required fields.

## Handoff back

- Update `work/5-seo-optimization/tasks.md` and `notes.md`.

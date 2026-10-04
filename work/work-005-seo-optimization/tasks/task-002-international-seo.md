# Task 5.2 — International SEO & hreflang architecture

**Owner:** Gemini + Codex
**Status:** Pending

## Objective

Implement multinational SEO architecture to allow Sulocraft to rank effectively across global regions (India, US, UK, Canada, Australia) while adhering to internationalization best practices.

## Context and contract

Multi-region e-commerce requires explicit canonicalization, `hreflang` tags (including `x-default`), regional currency formatting hints, and localized metadata.

## Scope

- In scope:
  - Add `hreflang="en"` and `hreflang="x-default"` tags to page `<head>`.
  - Ensure canonical tags point unambiguously to canonical URL without tracking parameters.
  - Add geo-targeting and OpenGraph locale metadata (`og:locale="en_IN"`, `og:locale:alternate="en_US"`).
- Out of scope:
  - Full multi-language translation machine in V1 (content is in English).

## Dependencies and relevant files

- Depends on: Task 5.1.
- Inspect/edit:
  - `src/components/SeoManager.tsx`
  - `backend/app/services/seo.py`
  - `scripts/prerender.mjs`

## Acceptance checks

- [ ] Every rendered route includes `<link rel="canonical">` and appropriate `<link rel="alternate" hreflang="...">` tags.
- [ ] Canonical tags strip query parameters (`?sort=`, `?page=`, `?filter=`).

## Handoff back

- Update `work/work-005-seo-optimization/tasks.md` and `notes.md`.

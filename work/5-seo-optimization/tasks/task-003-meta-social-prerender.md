# Task 5.3 — Meta tags, dynamic social cards, and prerender route coverage

**Owner:** Codex
**Status:** Pending

## Objective

Ensure all public storefront pages (Home, Shop, 5 Categories, 4 Collections, 8 Occasions, 16 Products, About, Contact, Terms, Privacy) have unique meta titles, descriptions, OpenGraph images, and Twitter Card tags pre-rendered into static HTML for instant search engine indexing.

## Context and contract

Social platforms and search bots do not always execute JavaScript. Pre-rendering ensures bots receive fully-populated `<title>`, `<meta name="description">`, and `<meta property="og:image">` tags in the initial HTTP payload.

## Scope

- In scope:
  - Run `scripts/prerender.mjs` to generate HTML files into `dist/`.
  - Ensure dynamic social card images use absolute `https://images.sulocraft.com` URLs.
  - Verify character length limits (Title: 50-60 chars; Description: 140-160 chars).
- Out of scope:
  - Private account or admin pages (must remain `noindex, nofollow`).

## Dependencies and relevant files

- Depends on: Task 5.2.
- Inspect/edit:
  - `scripts/prerender.mjs`
  - `src/components/SeoManager.tsx`

## Acceptance checks

- [ ] `node scripts/prerender.mjs` completes successfully and produces HTML for 48+ routes.
- [ ] Direct curl on built static HTML confirms `<meta>` tags and JSON-LD are present without JS execution.

## Handoff back

- Update `work/5-seo-optimization/tasks.md` and `notes.md`.

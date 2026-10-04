# Work 005 — Global SEO optimization & multinational ranking

**GitHub Issue:** [#5](https://github.com/hackaholic/crochet/issues/5) · Work 005

**Objective:** Implement enterprise-grade, multinational search engine optimization (SEO) across Sulocraft to rank high globally for handcrafted crochet gifting, artisanal bouquets, and amigurumi.

**Scope:** JSON-LD structured data (Product, Organization, BreadcrumbList, FAQ, MerchantReturnPolicy), international hreflang & canonicalization, dynamic sitemap generation, OpenGraph/Twitter social cards, Core Web Vitals optimization, and static route pre-rendering.

**Current state:** Pending. Initial SEO schemas, resolver endpoint (`/api/v1/seo/resolve`), and route pre-rendering script exist in the codebase. Multinational internationalization and structured data audit remain to be completed.

**Dependencies:** Product catalogue domain; `docs/api-seo.md`; prerender script at `scripts/prerender.mjs`.

**Done when:** All public routes have complete, validated JSON-LD structured data; sitemap and robots.txt are dynamically verified; hreflang tags support global and regional traffic; automated tests pass; prerender generates all 48+ public routes with accurate metadata.

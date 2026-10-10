# Work 016 — Product taxonomy and tagging audit

**Objective:** Verify every catalogue product is classified correctly using its image, description, categories, tags and occasions, so filters/search/homepage collections retrieve the intended products.
**Work owner:** Codex
**Current state:** Pending; Gemini backend contracts ready. No product audit or database correction has been performed yet.
**Scope:** Full product inventory (including untagged products), classification evidence, uncertain-product questions to the user, narrow repeatable corrections and local verification. Check toys/amigurumi, baby products, flowers, decor, devotional products and occasion associations against the existing taxonomy.
**Architecture:** Existing ProductCategory, tags, ProductOccasion and collection associations remain database-owned; frontend renders API data. A product can belong to multiple valid groups (e.g. bunny: animal, soft toy, gift and an appropriate occasion). Tags do not establish baby-safety certification or suitability without evidence.
**Dependencies:** Existing catalogue schema and taxonomy; existing uploaded images/public URLs. Image creation/upload is outside this work unless a separately approved missing-asset task is added.
**Constraints:** Preserve SKU/id, prices, assets, stock, orders and all unrelated fields. No DB reset, invented products, forced nonempty filters or unapproved safety claims. Ask the user with product id/SKU, image and proposed classification when ambiguous.
**Done when:** Every product has a reviewed mapping or a clearly recorded unresolved question; approved corrections are repeatable and verified against local APIs/filters; regression checks pass before preprod promotion.

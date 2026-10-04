# Work 005 decisions

### DEC-005-1 — Backend-driven SEO metadata resolver

**Decision:** Maintain SEO title, description, canonical, and structured data schemas dynamically in the backend via `/api/v1/seo/resolve` with catalogue fallbacks.

**Reason:** Catalog items, occasions, and campaigns change over time. Storing SEO rules in the backend guarantees that both server-side pre-render scripts and client-side hydration use the exact same metadata.

### DEC-005-2 — Canonical URLs and International targeting

**Decision:** Use absolute canonical URLs pointing to `https://sulocraft.com/` for production and `x-default` hreflang tags for international reach with English (`en`) default.

**Reason:** Prevents duplicate content penalties across query params (`?sort=`, `?page=`) and establishes clear international discoverability.

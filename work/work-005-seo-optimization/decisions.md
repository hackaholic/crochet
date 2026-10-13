# Work 005 decisions

### DEC-005-1 — Backend-driven SEO metadata resolver

**Decision:** Maintain SEO title, description, canonical, and structured data schemas dynamically in the backend via `/api/v1/seo/resolve` with catalogue fallbacks.

**Reason:** Catalog items, occasions, and campaigns change over time. Storing SEO rules in the backend guarantees that both server-side pre-render scripts and client-side hydration use the exact same metadata.

### DEC-005-2 — Canonical URLs and International targeting

**Decision:** Use absolute canonical URLs pointing to `https://sulocraft.com/` for production and `x-default` hreflang tags for international reach with English (`en`) default.

**Reason:** Prevents duplicate content penalties across query params (`?sort=`, `?page=`) and establishes clear international discoverability.

### DEC-005-3 — Complete scope and preserve existing work
Extend Work005; retain original four contracts/IDs and completed foundations. Focused task-NNN-description.md contracts follow existing repository convention; no giant SEO history or competing new work item.

### DEC-005-4 — Preserve design; inspect before migration
CURRENT5.5 is read-only audit. Existing modular API/frontend/build boundaries remain default. Prefer DB snapshot static generation; SSR/framework migration requires measured evidence and ADR. No app implementation in this planning pass.

### DEC-005-5 — Truthful configured metadata; supersedes automatic targeting in DEC-005-2
Canonical origin and indexing policy come from validated environment config. Actual supported languages/markets determine hreflang; do not invent international variants or emit alternate tags merely for global rankings. Unknown policy/review/material claims omitted. No ranking guarantees.

### DEC-005-6 — Ownership split
Codex owns frontend/rendering/HTTP delivery/acceptance. Gemini owns exact backend5.17–5.20 and5.15 contracts after audit. Typed schema/snapshot return precedes frontend consumption; backend task status/testing belongs to Gemini; global handoffs only link here.

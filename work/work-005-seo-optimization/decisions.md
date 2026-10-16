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

### DEC-005-7 —5.2 targeting/origin decision (2026-10-13)
Context: Current site is English with INR/India copy, but approved international shipping/locale support is not established. Existing scripts/runtime emit alternate tags and conflicting origins by default.
Decision: Keep current canonical route families; no new locale/country URLs or geo/alternate tags until actual equivalent localized content and owner-approved supported markets exist. Single English content can be discoverable without invented US/UK/etc duplicates.
Origin/indexability: Same application code receives validated public origin and indexability policy via environment/config. Local/preprod are noindex; production indexing must be explicitly configured with valid production origin. No implicit production credential/domain fallback. Self-canonical nonproduction URLs plus noindex avoid pretending preprod is the published store.
Consequences: Gemini5.17/5.18 return configured canonical/indexing fields and optional real locale equivalents. Codex5.3/5.6/5.7 remove unconditional alternates and conflicting metadata sources.5.2 completes the policy decision only; these implementation tasks must prove actual output.

### DEC-005-9 — Shared React build rendering and hydration
Use the same public React tree with route-specific frozen public bootstrap data for static rendering and client hydration. Fetch API data before rendering; no HTML-only alternative layout, framework migration or private/session data. Background refresh happens after hydration. Snapshot/path validation fails the build rather than fabricating content. Prerender freshness requires rebuild on approved catalogue/content edits; describe stale-asset invalidation and missing-route handling explicitly.

### DEC-005-10 — Root resources and indexing boundary
Generate root sitemap artifacts from the backend public route inventory during the same verified frontend build. No runtime provider secrets or hardcoded catalog list. Non-indexing builds publish an empty sitemap, crawlable robots and site-wide X-Robots-Tag:noindex,nofollow; robots is not authentication. Explicit production indexing and validated public origin are required to advertise sitemap URLs. Omit generated-today static-page lastmod until real provenance exists; entity timestamps stay DB-driven. Same code path/config-selected policy across environments.

### DEC-005-11 — Content provenance
Visible category/collection intro uses the matching entity description, never the generic SEO meta-summary. Product initial details reuse matching Work019 entity fields and refresh the same detail API; unknown facts stay absent. Static demo testimonials/seed rating counters are not review evidence. Full body description and actual-review summaries are additive backend5.13.1 fields; no duplicate editor/content store.

### DEC-005-12 — Preparation is separate from public launch evidence
5.14delivers an exact owner checklist and5.21a monitoring runbook, without pretending account verification/field data exists. Monitoring planning does not need a completed rollout; live results depend on5.4. Final local5.4test gates may pass while production sign-off stays Blocked for owner-approved facts and gated deployment/external/device evidence. Local loopback metrics cannot substitute for cold mobile/fieldCWV.

### DEC-005-13 — Owner-approved preprod review content
Owner confirmed2026-10-16: retain demo homepage reviews during preprod; hide the review cards before production launch. Retain the owner-approved500+happy customers message. No review data or UI removed in this turn. Use backend/admin content configuration, not a hardcoded frontend environment check; if existing section visibility also hides its heading, separate the approved message from review-card visibility during launch preparation. Demo quotes must not be represented as genuine production testimonials or review schema. Production release checklist must verify review cards are absent while approved message remains.

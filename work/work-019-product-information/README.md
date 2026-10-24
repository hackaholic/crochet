# Work 019 — Editable product information and defaults

**Owner:** Codex
**Status:** In Progress (19.5 diagnosis complete;19.6 backend deployment pending)

## Objective
Provide six editable product-information fields in admin product creation/editing: Handmade Details, Materials Used, Size & Dimensions, Processing Time, Care Instructions, Shipping & Delivery. New products begin with backend-managed defaults, which admins can override. Storefront accordions show persisted product values.

## Current state
19.4 restored missing public specifications using saved product text first, backend defaults otherwise; API/SEO align and all24 local products verified. Saved product records unchanged. DEC019-6 supersedes prior empty-field display behavior.
19.1–19.3 completed. Six-field editing/defaults/public accordions and local acceptance verified. Owner requested neutral timing/delivery wording, applied without overwriting custom defaults or product descriptions. No push/deployment.

## Scope and architecture
Keep existing React/FastAPI/catalogue architecture. Use a controlled six-field schema, plain text with line breaks, reusable editor and accordion template. Defaults are database-managed and editable by admin, not embedded in UI. Snapshot defaults into new product form/product on creation; later default changes must not overwrite existing product overrides. No arbitrary HTML or React structures. All environments share code and configuration rules.

## Dependencies and definition of done
Gemini19.1 delivers persisted defaults/admin create-update/read/public detail contract and migration; Codex19.2 integrates editor/storefront; Codex19.3 verifies local Docker/API/browser roundtrips. Preserve products/variants/tags/images, backwards-compatible migration, tests and authorization. Owner confirms factual default copy before release; do not reuse blanket child-safe/testing/delivery promises without evidence. No push/deploy from this work without authorization.

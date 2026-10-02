# Work 010 — Seasonal Gift by Occasion

**Objective:** Make the homepage's Gift by Occasion section a database-driven, seasonal discovery feature that the owner can configure from admin, with each active occasion showing relevant products and its own clear artwork.

**Current state:** Gemini reports the Task 10.18 backend migration, database/seed image-key repair, admin toggle behavior, and backend tests complete. Codex is rebuilding and verifying the integrated local Docker app; owner review remains before any release. The ten additional occasion artworks are already in R2, so no copy or upload step remains.

**Scope:** Occasion records and admin controls; enable/disable and optional seasonal schedules; unique image assignment; mapping existing products to multiple occasions; homepage section resolution/order; shop filtering; migration/seed safety; tests and local Docker/browser verification.

**Architecture:** Occasion names, images, schedules, visibility, ordering, and product associations come from the database/API. Frontend uses a reusable `occasion_grid` template for presentation and navigates to `/shop?occasion=<occasion-id>`. A product remains one catalogue entity/SKU even when associated with multiple occasions. Never hardcode occasion cards or product membership in the frontend.

**Default enabled occasions:** Birthday, Just Because, Anniversary, Baby Shower, and Wedding. This is the initial seeded/admin state, not a frontend hardcoded list. Every occasion, including these five, remains admin-configurable. The stable Baby Shower record ID is `babyshower`; preserve existing IDs and product mappings.
**Other/admin-controlled occasions:** Valentine's Day, Decor, Diwali, Mother's Day, Father's Day, Christmas, Rakhi, Housewarming, and future occasions remain available in admin but are disabled by default. Admin can enable or schedule them when relevant.

**Grid ordering:** Return only enabled, currently in-season occasions. Keep backend/admin ordering; newly enabled occasions should not be forced into a separate seasonal/evergreen group. The frontend renders the API array as-is.

**Relevant contracts:** [Task 10.18](tasks/task-018-default-occasions-and-images.md); [storefront API](../../docs/api-storefront.md); [admin API](../../docs/api-admin.md); [catalogue API](../../docs/api-catalogue.md). Previous handoff reports remain in the [archive](../../docs/archive/handoffs-history.md).

**Definition of done:** Admin can prepare, enable, schedule, order, and hide occasions without a frontend release; only enabled/in-season occasions render; every card has distinct, relevant artwork; each occasion link returns the correctly tagged database products; repeat migrations/seeding are safe; meaningful backend/frontend tests pass; local Docker API, DB, and frontend plus desktop/mobile browser behavior are verified. Do not push or deploy until the owner reviews the local result.

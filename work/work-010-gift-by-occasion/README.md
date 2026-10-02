# Work 010 — Seasonal Gift by Occasion

**Objective:** Make the homepage's Gift by Occasion section a database-driven, seasonal discovery feature that the owner can configure from admin, with each active occasion showing relevant products and its own clear artwork.

**Current state:** Completed. Backend evergreen rules, seasonal-first ordering, and updated distinct artwork references (`-v2.png`) are implemented and active in the database. Frontend admin controls and occasion grid rendering are verified. Automated test suite (162 backend tests, 59 frontend tests) and live API automated verification (20 checks in Work 011) pass 100%. Owner review completed and approved.

**Scope:** Occasion records and admin controls; enable/disable and optional seasonal schedules; unique image assignment; mapping existing products to multiple occasions; homepage section resolution/order; shop filtering; migration/seed safety; tests and local Docker/browser verification.

**Architecture:** Occasion names, images, schedules, visibility, ordering, and product associations come from the database/API. Frontend uses a reusable `occasion_grid` template for presentation and navigates to `/shop?occasion=<occasion-id>`. A product remains one catalogue entity/SKU even when associated with multiple occasions. Never hardcode occasion cards or product membership in the frontend.

**Evergreen occasions:** Birthday, Anniversary, Wedding, and Baby Shower stay visible year-round and are not hidden by seasonal scheduling. The stable Baby Shower record ID is `babyshower`.  
**Seasonal/admin-controlled occasions:** Valentine's Day, Decor, Diwali, Mother's Day, Father's Day, Christmas, Rakhi, and future occasions can be enabled/disabled or scheduled by admin as appropriate. Rakhi stays hidden until explicitly enabled.

**Grid ordering:** Enabled, in-season seasonal occasions lead the homepage grid; evergreen occasions follow. Admin display order applies within each group, so activating a seasonal occasion moves it into the lead group without frontend content sorting.

**Relevant contracts:** [Occasion configuration and artwork handoff](../../docs/handoffs.md#2026-10-02--seasonal-gift-by-occasion-admin-configuration-and-distinct-artwork); [homepage section handoff](../../docs/handoffs.md#2026-10-02--restore-amigurumi-and-gift-by-occasion-homepage-sections); [storefront API](../../docs/api-storefront.md); [admin API](../../docs/api-admin.md); [catalogue API](../../docs/api-catalogue.md).

**Definition of done:** Admin can prepare, enable, schedule, order, and hide occasions without a frontend release; only enabled/in-season occasions render; every card has distinct, relevant artwork; each occasion link returns the correctly tagged database products; repeat migrations/seeding are safe; meaningful backend/frontend tests pass; local Docker API, DB, and frontend plus desktop/mobile browser behavior are verified. Do not push or deploy until the owner reviews the local result.

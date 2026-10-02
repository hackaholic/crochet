# Work 010 decisions

- **DEC-010-001 — Database is the source of truth.** Occasion content, visibility, schedule, ordering, image, and product associations come from backend/database responses; frontend contains only reusable presentation.
- **DEC-010-002 — Seasonal occasions are admin-controlled.** Only enabled seasonal occasions inside their optional `Asia/Kolkata` schedule appear. Hidden or out-of-season records remain manageable in admin but are omitted from the storefront; evergreen records ignore seasonal visibility/scheduling.
- **DEC-010-003 — Products can have multiple occasion associations.** Reuse product records and SKUs; do not duplicate products for each gift occasion.
- **DEC-010-004 — One distinct relevant image per visible occasion.** Reject duplicate assignments and inspect the actual imagery; different URLs alone do not satisfy uniqueness.
- **DEC-010-005 — No empty section.** Omit the homepage grid only when there are no eligible occasions. In normal operation the four evergreen cards keep it populated even when every seasonal item is off.
- **DEC-010-006 — Release gate.** Local Docker/API/database and browser verification plus owner review are required before push or VPS deployment.
- **DEC-010-007 — Evergreen core and first seasonal placement.** Birthday, Anniversary, Wedding, and Baby Shower remain visible year-round regardless of seasonal occasion scheduling. Other occasions can be enabled, disabled, or scheduled by admin. Active seasonal occasions lead the grid; admin ordering applies within seasonal and evergreen groups.
- **DEC-010-008 — Occasion art must tell the occasion story.** Birthday should feel like a joyful modern celebration with a Sulocraft handmade gift; Anniversary should show a husband meaningfully gifting his wife a handmade Sulocraft product; Wedding should feel like a bright contemporary wedding gift moment. A generic heart-only graphic or dark/dull scene is insufficient.
- **DEC-010-009 — Occasion business rules stay server-owned.** Admin UI consumes `isEvergreen` and API-returned ordering; it does not maintain its own list of evergreen occasion names or sort homepage cards.

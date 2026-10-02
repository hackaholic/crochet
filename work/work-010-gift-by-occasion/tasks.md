# Work 010 tasks

## In Progress

None.

## Pending

None.

## Completed (reported by implementation handoffs; revalidate as part of 10.11)

- [x] 10.1 Define the initial occasion list, seasonal visibility requirements, multi-occasion product behavior, distinct artwork, and homepage placement.
- [x] 10.2 Add database-backed occasion fields, product associations, admin CRUD, seed/migration support, and timezone-aware schedule resolution (Gemini reports migration `8b2c3d4e5f6a` and 134 backend tests passing).
- [x] 10.3 Add backend `occasion_grid` homepage data and omit the section when no occasions are eligible (Gemini handoff reports implementation and local API verification).
- [x] 10.4 Add reusable frontend occasion rendering and database-backed `/shop?occasion=` filtering (frontend implementation reported in coordination docs; current local homepage shows occasion links).
- [x] 10.9 Gemini: enforce year-round behavior for Birthday, Anniversary, Wedding, and Baby Shower; keep existing IDs and product associations; reject disabling, deletion, or seasonal dates for evergreen records; expose backend `isEvergreen`; repair DB image references to the new artwork and enable Baby Shower.
- [x] 10.10 Create modern, distinct Birthday, Anniversary, and Wedding gifting artwork and upload it to R2. Public URLs for all three objects return HTTP 200; database references are included in 10.9.
- [x] 10.11 Run integrated local acceptance: verify evergreen occasions remain visible all year and seasonal occasions follow admin enable/disable/schedule settings; ensure enabled, in-season seasonal cards lead the grid, followed by evergreen cards, with each group retaining admin display order. A zero-seasonal state still retains the four evergreen cards. Rebuild affected Docker services and inspect desktop and mobile rendering.
- [x] 10.12 Visually inspect all occasion images and URLs; confirm Birthday, Anniversary, and Wedding art is distinct, bright, current, and relevant.
- [x] 10.13 Verify product associations are sensible per occasion and one multi-occasion product appears in each relevant filter without duplicate catalogue rows/SKUs.
- [x] 10.14 Fix acceptance failures, add regression tests, and update the Gemini handoff and coordination status. Owner review completed and approved.
- [x] 10.15 Gemini: return enabled, in-season seasonal occasions before evergreen cards, preserving `displayOrder` within both groups; verify enable/disable and schedule transitions update the first position.
- [x] 10.16 Codex: add a database-driven admin page for occasion visibility and scheduling; show evergreen status from the API, lock evergreen controls, and fail closed if the backend has not supplied `isEvergreen`. Verified with four focused admin UI tests.
- [x] 10.17 Codex: preserve API order in the homepage occasion grid so backend-ranked active seasonal occasions appear first; verify the occasion link. Verified with one focused renderer test.

## Blocked

None. Owner review completed and approved.

# Frontend testing milestones

Tests protect existing customer flows before each new frontend feature is marked complete.

| Milestone | Scope | Status | Completion condition |
| --- | --- | --- | --- |
| QA-FE-01 | Test foundation | Complete | Vitest, Testing Library, `pnpm test`, and Docker execution work reliably. |
| QA-FE-02 | Shared logic | In progress | Route, product adapter, cart adapter, and currency-formatting tests cover contract transformations and failures. |
| QA-FE-03 | Component behavior | Planned | Header, search, basket controls, authentication dialog, and checkout validation have focused interaction tests. |
| QA-FE-04 | API integration | Planned | Mocked API tests cover loading, retry, unauthenticated, and server-error states for catalogue, cart, account, and checkout. |
| QA-FE-05 | End-to-end purchase path | Planned | Browser-level guest browse → cart → checkout → mock payment regression test runs in Docker. |
| QA-FE-06 | Cross-browser and mobile rendering | In progress | Every changed customer-facing view is checked in Chrome/Chromium, Firefox, and representative mobile widths before completion. |

## Required checks for frontend changes

1. Run `docker-compose -f docker/compose.yaml run --rm --no-deps frontend pnpm test`.
2. Run `pnpm typecheck` in the frontend container.
3. Run `docker-compose -f docker/compose.yaml exec -T frontend pnpm build`.
4. Add or update a focused test when a change affects a shared path, API adapter, or customer action.
5. Inspect the rendered result in the browser matrix below. Mobile is the primary storefront experience and must be checked first.

## Browser rendering matrix

| Target | Minimum viewport | Required checks |
| --- | --- | --- |
| Mobile browser | `390 × 844` | No horizontal overflow; copy remains readable; controls do not overlap; touch targets are at least 44px; key actions remain visible. |
| Large mobile | `430 × 932` | Images crop intentionally; sections retain sensible spacing; dialogs and drawers fit the viewport. |
| Chrome / Chromium desktop | `1280 × 720` | Navigation, grids, hero content, dialogs, and fixed controls align without layout shift. |
| Firefox desktop | `1280 × 720` | Font metrics do not cause overlap; flex/grid sizing matches intent; buttons and carousel controls remain separated. |

For dynamic content such as campaigns and product titles, verify the shortest and longest database records. A component is not complete when only its first/default item renders correctly.

## Current coverage

- Canonical product URLs and route matching.
- Catalogue response mapping, including backend field aliases.
- Catalogue API failure behavior.

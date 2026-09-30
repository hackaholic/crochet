# Frontend testing milestones

Tests protect existing customer flows before each new frontend feature is marked complete.

| Milestone | Scope | Status | Completion condition |
| --- | --- | --- | --- |
| QA-FE-01 | Test foundation | Complete | Vitest, Testing Library, `pnpm test`, and Docker execution work reliably. |
| QA-FE-02 | Shared logic | In progress | Route, product adapter, cart adapter, and currency-formatting tests cover contract transformations and failures. |
| QA-FE-03 | Component behavior | Planned | Header, search, basket controls, authentication dialog, and checkout validation have focused interaction tests. |
| QA-FE-04 | API integration | Planned | Mocked API tests cover loading, retry, unauthenticated, and server-error states for catalogue, cart, account, and checkout. |
| QA-FE-05 | End-to-end purchase path | Planned | Browser-level guest browse → cart → checkout → mock payment regression test runs in Docker. |

## Required checks for frontend changes

1. Run `docker-compose -f docker/compose.yaml run --rm --no-deps frontend pnpm test`.
2. Run `docker-compose -f docker/compose.yaml exec -T frontend pnpm build`.
3. Add or update a focused test when a change affects a shared path, API adapter, or customer action.

## Current coverage

- Canonical product URLs and route matching.
- Catalogue response mapping, including backend field aliases.
- Catalogue API failure behavior.

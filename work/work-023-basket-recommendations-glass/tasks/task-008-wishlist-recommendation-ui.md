# Work 023.8 — Layered product discovery on Wishlist

**Owner:** Codex
**Status:** Completed
**Work item:** Work 023

## Objective

Add the same database/API-driven discovery layers used at Checkout below the customer's saved products on Wishlist, including when the wishlist is empty.

## Context and contract

Wishlist currently renders only saved catalogue items (or an empty state). Checkout mounts the reusable `ProductRecommendations` component with the extended, paginated discovery feed. Reuse that feed and existing product cards; do not hardcode product names, image URLs, section titles, ordering, or recommendation content. Keep wishlist products distinct from recommendations and preserve wishlist actions.

## Scope

- In scope: render layered, paginated recommendations on Wishlist; responsive full-width layout; omit saved wishlist products from recommendation cards; failure/empty behavior; tests and local verification.
- Out of scope: new product data, personalized ranking claims, checkout changes, API/business rules, push/deployment.

## Dependencies and relevant files

- Depends on: [23.9](task-009-wishlist-discovery-context-api.md)
- Dependency context: the bounded discovery API must accept the `wishlist` context so its cursor is scoped correctly.
- Blocked by: 23.9
- Blocker reason: the existing discovery API accepts only `checkout` and `basket` contexts.
- Next action: implement after Gemini returns 23.9; filter out all current wishlist IDs and verify empty/populated states.
- Inspect/edit: `src/pages/WishlistPage.tsx`, `src/pages/WishlistPage.test.tsx`, `src/components/ProductRecommendations.tsx`, `src/lib/api/productDiscovery.ts`

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 23.8-TC01 | Populated wishlist includes discovery layers | Success | Render API-backed saved items and bounded discovery sections | Saved items remain; recommendations render below them using API section data | Wishlist page tests | Pass: retains saved item, renders API section, requests wishlist context |
| 23.8-TC02 | Empty wishlist remains useful | Boundary | Render no saved products with discovery results | Existing empty state remains and discovery layers are available | Wishlist page tests | Pass: empty state persists; shared component supplies API discovery |
| 23.8-TC03 | No duplicates | Regression | Discovery returns a saved wishlist product and repeated item across pages | Wishlist product is excluded from rec cards and feed remains deduplicated | component/integration test | Pass: saved IDs excluded; existing shared component test covers repeated IDs across pages |
| 23.8-TC04 | Discovery failure does not break saved items | Failure | Discovery API fails while wishlist API/data is available | Saved list still renders; failure has a safe retry/empty treatment | Wishlist page tests | Pass: empty state persists and safe retry appears without server detail |
| 23.8-TC05 | Responsive and accessible behavior | Accessibility/regression | Keyboard navigate and inspect desktop/mobile layout | Product links/actions work; sections have headings; no horizontal overflow | focused tests + local browser | Partial: shared semantic sections/ProductCard actions retained; CUA browser inventory unavailable, visual/mobile overflow unverified |
| 23.8-TC06 | Wishlist ownership remains enforced | Security | Request account wishlist while signed out / return to signed-in Wishlist | Existing API rejects unauthorized wishlist access; only public catalogue discovery data is shown | existing backend auth test + code review | Pass by unchanged control: account wishlist remains authenticated; 23.9-TC05 verifies public discovery never reads or exposes wishlist records |

## Security validation

- Changed assets/trust boundaries and plausible abuse: customer wishlist UI and public product discovery. Avoid leaking saved IDs to the discovery API or treating client filtering as authorization.
- Applicable controls and linked negative test IDs: wishlist contents remain sourced through existing authenticated wishlist API; discovery returns only public eligible catalogue products. 23.8-TC06.
- API/database work: none in Codex UI subtask; backend context contract is 23.9.
- Commands/target/results and evidence (redacted): `npm exec vitest -- run src/pages/WishlistPage.test.tsx src/components/ProductRecommendations.test.tsx` passed 7/7; `npm run typecheck` passed. Local storefront and `/api/v1/storefront/discovery?context=wishlist&limit=1` returned HTTP 200 after Docker frontend rebuild. Unauthenticated `/api/v1/wishlist` returned 401. CUA reported no browsers. No auth/API code changed.
- Disposition: Pass; browser visual/mobile check unverified.
- Findings, severity, remediation owner, and blockers: None known.

## Acceptance checks

- [x] Reuse the Checkout discovery layers and reusable product cards on Wishlist, including empty state.
- [x] Wishlist products are not duplicated in discovery; data and content stay API/database-driven.
- [x] Focused tests/typecheck pass; local Docker storefront/API endpoints respond. Browser visual/mobile check unavailable (no browser in CUA inventory).
- [x] Security disposition and self-review recorded; no push/deploy.

## Handoff back

Return to parent Codex: Wishlist mounts shared API-driven discovery below saved/empty state using wishlist context and excludes saved IDs. Focused tests 7/7, typecheck, Docker rebuild, storefront/API HTTP 200. Browser visual/mobile check unavailable because CUA had no browser surfaces. No push/deploy.

## Pickup checklist

- [x] Read Work023 context and the returned 23.9 contract.
- [x] Confirm 23.9 is Returned/Completed before starting.
- [x] Do not alter Checkout behavior or repeat completed basket work.

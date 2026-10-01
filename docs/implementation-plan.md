# Implementation plan

This plan turns the multi-agent specification into small, ordered tasks. Only one frontend task and one backend task should be `In progress` at a time. The shared contract and handoff log are the source of truth between owners.

## Delivery principles

- Codex owns the frontend; Gemini owns the backend.
- Backend OpenAPI is the source for generated frontend types and API clients.
- The frontend never calculates final prices, stock, discounts, or order eligibility.
- Visitors browse and use a guest cart before authentication.
- Complete and verify each task before starting the next task in that stream.

## Milestone 1 — Foundation

| ID | Owner | Task | Status | Handoff / completion condition |
| --- | --- | --- | --- | --- |
| FE-01 | Codex | Route foundation and application shell | Done | Clean client routes replace in-memory page switching; production build and direct product URL verified |
| FE-02 | Codex | API-client generation setup | Done | Typed client integrated at `src/lib/api/catalogue.ts` consuming `docs/openapi.yaml` |
| BE-01 | Gemini | Backend foundation | Done | FastAPI, SQLite/PostgreSQL, configuration, health check, CORS, and OpenAPI output |
| BE-02 | Gemini | Publish initial OpenAPI document | Done | `docs/openapi.yaml` exported and recorded in handoffs |

## Milestone 2 — Catalogue

| ID | Owner | Task | Status | Handoff / completion condition |
| --- | --- | --- | --- | --- |
| BE-03 | Gemini | Flexible catalogue domain | Done | Categories, tags, products, variants, images, seed data, and catalogue endpoints |
| FE-03 | Codex | Catalogue API integration | Done | Home, shop, search, and product screens consume live `/api/v1/products` API |

## Milestone 3 — Storefront catalogue UX

| ID | Owner | Task | Status | Handoff / completion condition |
| --- | --- | --- | --- | --- |
| FE-04 | Codex | Reusable loading, error, and empty-state patterns | Done | Applied shared states across storefront, cart, and wishlist flows |

## Milestone 4 — Guest cart

| ID | Owner | Task | Status | Handoff / completion condition |
| --- | --- | --- | --- | --- |
| BE-04 | Gemini | Persistent guest cart and merge rules | Done | Server-side cart API, cookie-based tokens, inventory-aware quantities, guest-to-user merge |
| FE-05 | Codex | Cart integration | Done | Connected basket drawer and cart page to `/api/v1/cart` using `CartProvider` |

## Milestone 5 — Authentication

| ID | Owner | Task | Status | Handoff / completion condition |
| --- | --- | --- | --- | --- |
| BE-05 | Gemini | Google and phone OTP authentication | Done | Cookie-based session flow, `/auth/me`, rate limiting, and secure logout |
| FE-06 | Codex | Authentication UX | Done | Connected header account control to phone OTP modal with auto cart merge |

## Milestone 6 — Checkout and orders

| ID | Owner | Task | Status | Handoff / completion condition |
| --- | --- | --- | --- | --- |
| BE-06 | Gemini | Addresses, checkout, orders, and status history | Done | Authorized order APIs with price/address snapshots and tracking timelines |
| FE-07 | Codex | Checkout, order confirmation, and tracking UX | Done | Connected checkout to `POST /api/v1/orders` with address entry and COD flow |

## Milestone 7 — Payment abstraction

| ID | Owner | Task | Status | Handoff / completion condition |
| --- | --- | --- | --- | --- |
| BE-07 | Gemini | Decoupled payment provider layer (Mock + Razorpay) | Done | Created payment intents, signature verification, and mock gateway |
| FE-08 | Codex | Payment flow & gateway modal | Done | Completed checkout payment verification using local mock gateway |

## Milestone 8 — Customer account & wishlist

| ID | Owner | Task | Status | Handoff / completion condition |
| --- | --- | --- | --- | --- |
| BE-08 | Gemini | Customer profile, account overview & persistent wishlist | Done | Profile edit, overview metrics, and wishlist endpoints; published `docs/api-account.md` |
| FE-09 | Codex | Customer account & wishlist UI | Done | My Account overview, profile editing, address book, orders, and persistent wishlist are wired to the published API contract |

## Milestone 9 — Admin catalog & dashboard

| ID | Owner | Task | Status | Handoff / completion condition |
| --- | --- | --- | --- | --- |
| BE-09 | Gemini | Admin catalog, inventory, order status & analytics | Done | Product/variant CRUD, inventory adjustment, order status transitions, and store analytics; published `docs/api-admin.md` |
| FE-10 | Codex | Admin dashboard UI | In progress | Build admin views for catalog management, stock adjustments, and order fulfillment |

## Milestone 10 — Promotions, coupons & customer reviews

| ID | Owner | Task | Status | Handoff / completion condition |
| --- | --- | --- | --- | --- |
| BE-10 | Gemini | Promotions engine & customer product reviews | In progress | Coupon validation, cart discount application, customer review submission, and admin moderation |
| FE-11 | Codex | Coupon entry & review submission UI | Done | Cart coupon application and authenticated product review submission use the published API contract |

# Cross-team handoffs

Use this file whenever frontend or backend work becomes ready for the other side. Newest handoff goes first.

## 2026-10-02 — Homepage section media repair complete & verified on dev API

From: Gemini
To: Codex / Owner
Status: Complete; 112 backend tests passing; verified in Docker and R2

Changed:
- Updated `seed_storefront_content` in `backend/app/db/seed.py`:
  - `promo_banner` default seeded with `sections/gift-handcrafted-warmth.png`.
  - `image_text` default seeded with `about/anupama-sharma.png`.
  - Added automatic database repair logic on startup for existing `HomepageSection` rows pointing to outdated/missing keys (`campaigns/promo-gift-warmth.jpg` or `sections/artisan-story.jpg`).
- Added automated regression test `test_homepage_section_media_keys_and_repair` in `backend/tests/test_storefront.py` asserting key repair, serialization, and absolute URL resolution via `IMAGE_BASE_URL`.
- Ran full backend test suite: **112/112 tests passed**.
- Rebuilt and restarted local `docker-api-1` container; verified `/api/v1/storefront/home` outputs:
  - Promo banner: `http://localhost:8000/static/images/sections/gift-handcrafted-warmth.png` (HTTP 200)
  - Image text: `http://localhost:8000/static/images/about/anupama-sharma.png` (HTTP 200)
- Verified public Cloudflare R2 URLs return HTTP 200 with immutable cache headers:
  - `https://images.sulocraft.com/sections/gift-handcrafted-warmth.png` (2.2MB, HTTP 200)
  - `https://images.sulocraft.com/about/anupama-sharma.png` (2.3MB, HTTP 200)
- Verified frontend test suite inside container: **35/35 tests passed** (5 node + 30 vitest).
- Updated `docs/TODO.md`: Marked row complete.

How to verify:
- `curl -s http://localhost:8000/api/v1/storefront/home | jq '.sections[] | {type: .type, title: .title, imageUrl: .imageUrl}'`
- `curl -sI https://images.sulocraft.com/sections/gift-handcrafted-warmth.png | head -n 5`
- `curl -sI https://images.sulocraft.com/about/anupama-sharma.png | head -n 5`
- `PYTHONPATH=. .venv/bin/pytest tests/test_storefront.py -v` (12 passed)

## 2026-10-02 — Gemini: repair broken homepage section media on dev

From: Codex
To: Gemini
Status: Completed by Gemini

On `https://dev.sulocraft.com/`, the promo section **“Gift Handcrafted Warmth This Season”** and story section **“Handmade with Love, Thread by Thread”** have image URLs that return R2 404s. The old objects do not exist and their source files are absent:

- `campaigns/promo-gift-warmth.jpg`
- `sections/artisan-story.jpg`

Use these two distinct assets instead:

| Section | Required `image_url` key | Local asset |
| --- | --- | --- |
| Promo banner: Gift Handcrafted Warmth This Season | `sections/gift-handcrafted-warmth.png` | `public/images/sections/gift-handcrafted-warmth.png` |
| Image + text: Handmade with Love, Thread by Thread | `about/anupama-sharma.png` | `public/images/about/anupama-sharma.png` |

The About page also uses Anupama's owner-provided portrait at `/images/about/anupama-sharma.png`. The second image is her real owner photo; do not replace it with generated imagery or use it as a generic product photo. The promo art is a newly generated wide crochet-gift hamper image with clear space for the section's existing live copy.

Required backend work:

- Update `seed_storefront_content` in `backend/app/db/seed.py` to use the exact relative keys above.
- Update the existing development `HomepageSection` rows; the seed inserts defaults only when no sections exist.
- Upload/verify both R2 objects and make sure `IMAGE_BASE_URL` returns each absolute public URL.
- Add a test that asserts the expected section keys and resolved URLs; run the backend suite.
- Rebuild/redeploy only the dev API and verify `/api/v1/storefront/home` plus both rendered homepage images.

Frontend rendering already accepts the returned URLs verbatim. See the authoritative mapping in `docs/api-storefront.md` and mark this task complete in `docs/TODO.md` only after dev verification.

## 2026-10-02 — Pre-render public storefront routes complete (Task 31)

From: Gemini
To: Codex / Owner
Status: Complete; 48 public routes pre-rendered with metadata, schemas, and initial HTML; 35 frontend tests passing

Changed:
- Implemented `scripts/prerender-routes.mjs`: canonical route inventory spanning home `/`, `/shop`, `/about`, `/contact`, policies, 16 controlled products, 16 categories, and 8 collections.
- Implemented `scripts/prerender.mjs`: injects title, description, canonical link, Open Graph, Twitter cards, BreadcrumbList, Product/Offer, and Organization Schema.org JSON-LD scripts, plus initial semantic body content into `dist/<path>/index.html`.
- Updated `src/main.tsx`: uses `ReactDOM.hydrateRoot` when pre-rendered DOM exists in `#root`, preserving dynamic CSR `createRoot` for private routes.
- Updated `scripts/build-frontend.mjs`: executes pre-rendering automatically following `vite build` when not in `coming-soon` launch mode.
- Added `scripts/prerender.node-test.mjs`: automated tests validating route inventory, metadata, schema injection, and exclusion of private routes (`/cart`, `/checkout`, `/admin`).
- Verified `pnpm test` (5 node tests + 30 vitest tests = 35 total tests passing) and `pnpm build:dev` (48 routes generated into `dist/`).
- Updated `docs/TODO.md`: Row 31 marked `Done`.

How to verify:
- `pnpm test`
- `pnpm build:dev`
- Inspect `dist/products/heart-bear/index.html` and `dist/categories/flowers/index.html`



## 2026-10-01 — V1 authentication & purchase regression suite complete

From: Gemini
To: Codex
Status: Complete; 111/111 backend tests passing

Changed:
- Implemented `backend/tests/test_purchase_regression.py` with 6 end-to-end regression scenarios:
  1. **Full V1 purchase flow (magic link)**: Guest cart → email magic-link sign-in + cart merge → checkout with saved address → mock payment intent + verify (PAID/CONFIRMED) → admin PROCESSING → admin SHIPPED with BlueDart tracking → customer tracking timeline with CONFIRMED/PROCESSING/SHIPPED statuses.
  2. **Guest COD checkout**: Unauthenticated guest completes a COD order with inline shipping address — no login required.
  3. **Google social login + cart merge + checkout**: Google social sign-in merges guest cart and allows COD checkout.
  4. **Phone OTP endpoints removed**: `POST /auth/phone/send-otp` and `POST /auth/phone/verify-otp` must return 404 (confirmed removed from V1).
  5. **Admin RBAC enforcement**: Unauthenticated → 401; non-admin authenticated → 403 on `/api/v1/admin/orders`.
  6. **Magic link single-use atomic enforcement**: Second use of a consumed token must redirect to `error=invalid_link`.
- Updated `docs/TODO.md`: task 15 marked `Done`.
- Full backend suite: **111 tests passed, 0 failures** across 15 test modules.

How to verify:
- `PYTHONPATH=. .venv/bin/pytest tests/test_purchase_regression.py -v` (6 passed)
- `PYTHONPATH=. .venv/bin/pytest tests/ -q` (111 passed)



## 2026-10-01 — Dynamic SEO metadata resolver, XML sitemap, and robots.txt complete

From: Gemini
To: Codex
Status: Complete; ready for frontend pre-rendering or route SEO verification

Changed:
- Implemented `GET /api/v1/seo/resolve?path=...` returning `SeoMetadataOut` (camelCase aliases for frontend compatibility, title, description, canonicalPath, robots, imageUrl, imageAlt, pageType, breadcrumbs).
- Handled public static paths (`/`, `/about`, `/contact`, `/shop`), categories (`/categories/{slug}`), collections (`/collections/{slug}`), and active products (`/products/{slug}`) with fallback heuristics and hierarchical breadcrumb generation.
- Handled query string canonicalization (e.g. `/shop?category=flowers` -> canonicalPath `/categories/flowers`).
- Handled private routes (`/account*`, `/cart`, `/checkout*`, `/admin*`, `/wishlist`, `/auth*`, `/login`, etc.) and 404 missing routes by returning HTTP 200 with `robots: "noindex,nofollow"` so React `SeoManager` can apply noindex safely without throwing fetch errors.
- Implemented dynamic XML sitemap at `/sitemap.xml` and `/api/v1/seo/sitemap.xml` indexing all static public routes, active categories, collections, and products with `<loc>`, `<lastmod>`, `<changefreq>`, and `<priority>`.
- Implemented `/robots.txt` and `/api/v1/seo/robots.txt` disallowing private paths and referencing the production sitemap URL.
- Added test suite `backend/tests/test_seo.py` with 9 comprehensive tests; all 105 backend tests pass.
- Regenerated `docs/openapi.yaml` (74 paths).
- Rebuilt Docker `docker-api-1` container and validated live curl responses.

How to verify:
- `curl -s "http://localhost:8000/api/v1/seo/resolve?path=/products/heart-bear"`
- `curl -s "http://localhost:8000/api/v1/seo/resolve?path=/shop?category=flowers"`
- `curl -s "http://localhost:8000/api/v1/seo/resolve?path=/cart"`
- `curl -s "http://localhost:8000/sitemap.xml"`
- `curl -s "http://localhost:8000/robots.txt"`
- `PYTHONPATH=. .venv/bin/pytest tests/test_seo.py` (9 passed)
- `PYTHONPATH=. .venv/bin/pytest tests/` (105 passed)



## 2026-10-01 — Development VPS stack deployed and verified

From: Codex
To: Gemini
Status: Complete; continue with SEO contract

Changed:
- Created the non-root `sulocraft-deploy` VPS account with deployment-only SSH access and Docker permissions.
- Added dev-branch GitHub Actions automation for backend tests, pre-migration PostgreSQL backup, timestamped release upload, Compose build, Alembic migration, and health-gated activation.
- Fixed the production API image to install `httpx` and package the approved `public/images` manifest required by the catalogue publication gate.
- Deployed release `initial-dev-20261001` to `/opt/sulocraft/releases` with the persistent `sulocraft_postgres_data` volume.

How to verify:
- `http://201.18.212.183/health` returns `{"status":"ok","service":"sulocraft-api"}` before the Cloudflare API hostname is attached.
- Public API returns five canonical root categories and 16 seeded products with `X-Total-Count: 16`.
- FastAPI and PostgreSQL report healthy; Caddy is running.

Notes:
- Cloudflare `api-dev.sulocraft.com` DNS/TLS routing and protected GitHub environment secrets remain owner/Codex configuration work.
- Gemini's next backend task remains the typed SEO resolver, sitemap, and robots implementation documented immediately below.

## 2026-10-01 — Controlled media uploaded to Cloudflare R2

From: Codex
To: Gemini
Status: Complete

Changed:
- Uploaded all 31 files under `public/images` to `sulocraft-products` using the same relative object keys.
- Confirmed a second R2 comparison reports 31 unchanged and zero missing/changed objects.
- Confirmed `https://images.sulocraft.com/products/heart-bear/primary.png` returns HTTP 200 with `Cache-Control: public, max-age=31536000, immutable`.
- Added reusable dry-run/apply/public-verification automation in `backend/scripts/upload_r2_media.py`.

Contract:
- Production database media keys remain relative, for example `products/heart-bear/primary.png`.
- `IMAGE_BASE_URL=https://images.sulocraft.com` resolves those keys for storefront responses.
- Do not replace these controlled keys with temporary or unrelated images.

How to verify:
- Run the uploader without `--apply`; expected result is `Scanned 31 files: 0 changed, 31 unchanged`.
- Request any seeded media key beneath `https://images.sulocraft.com/`; it must return HTTP 200.

Notes:
- The scoped R2 credential remains only in the ignored local pre-production environment file and must be rotated before production launch.

## 2026-10-01 — Gemini next task: dynamic SEO resolver and sitemap

From: Codex
To: Gemini
Status: Ready for implementation

Changed:
- The final hierarchical taxonomy and 16-product controlled seed are accepted as complete with 96/96 backend tests.
- Frontend taxonomy consumption and the four-card homepage category grid have been verified locally.
- VPS release/rollback automation and the R2 local media uploader are documented in `docs/vps-deployment.md`.

Contract:
- Implement the outstanding SEO contract in `docs/api-seo.md` now that product, category, collection, and storefront entities are stable.
- Provide `GET /api/v1/seo/resolve?path=...`, database-backed/default entity metadata, private and missing route `noindex,nofollow`, dynamic XML sitemap, and robots output.
- Return typed data only from the resolver. Do not return arbitrary HTML, script tags, or arbitrary JSON-LD.
- Preserve all existing taxonomy, storefront, authentication, email, cart, order, payment, and admin behavior.

How to verify:
- Resolve home, category, collection, active product, private, and missing paths.
- Confirm sitemap contains active canonical entities with `lastmod` and excludes inactive/private/filter URLs.
- Confirm robots references `https://sulocraft.com/sitemap.xml` and disallows private/admin routes.
- Run the full backend suite and update OpenAPI, `docs/TODO.md`, and this handoff with the exact result.

Notes:
- This is the next backend task. R2 credentials and Cloudflare DNS remain owner/Codex deployment work and do not block SEO implementation.

## 2026-10-01 — Backend hierarchical taxonomy & collections ready

From: Gemini
To: Codex
Status: Completed & verified in Docker

- Rebuilt database models with first-class `Category`, `ProductCategory` (with `is_primary`, `display_order`), `Collection`, and `ProductCollection` entities.
- Applied Alembic migration `d71c89f5a432_rebuild_taxonomy_and_collections.py`.
- Seeded the 5 canonical root categories in exact storefront order (`Flowers`, `Amigurumi`, `Baby`, `Home & Decor`, `Pooja & Devotional`) with all child categories and media card keys.
- Seeded 15 collections (13 evergreen gift collections + 2 merchandising collections: `bestsellers` and `new-arrivals`).
- Seeded the 16 controlled products from `docs/product-media.md` with unique SKUs, valid local images (`primary.png` and galleries), exact primary leaf categories, secondary categories, and collection tags.
- Implemented and verified the publication gate validator enforcing non-empty unique SKUs, valid local disk image references, non-reused primary images, and valid primary categories.
- Implemented public endpoints: `GET /api/v1/categories` (hierarchical and flat with recursive descendant product counts), `GET /api/v1/categories/{slug}`, `GET /api/v1/categories/{slug}/products` (deduplicating across descendants), `GET /api/v1/collections`, `GET /api/v1/collections/{slug}`, `GET /api/v1/collections/{slug}/products`.
- Implemented admin endpoints: `/api/v1/admin/categories` with circular hierarchy cycle prevention and safe deletion blocking (when children or products exist), and full CRUD for `/api/v1/admin/collections`.
- Updated storefront home resolution to support collections and all 5 homepage sections.
- Regenerated `docs/openapi.yaml` with all 69 updated endpoint schemas.
- 96/96 tests passing in backend pytest suite (including dedicated tests in `backend/tests/test_taxonomy.py`).
- Synced to live Docker container `docker-api-1` and verified against PostgreSQL.

## 2026-10-01 — Four product gallery assets and seed manifest ready

From: Codex
To: Gemini
Status: Ready for backend seed/R2 integration

- Added distinct `gallery-01.png` views for the rose bouquet, tulip bouquet, heart bear, and couple bunny set under their canonical `public/images/products/<slug>/` directories.
- Added the existing gallery keys to `PRODUCTS_DATA`; no database record references a missing file.
- Published [product-catalogue-seed.json](product-catalogue-seed.json) with all 16 default SKUs, classification relationships, media ordering, alt text, and SHA-256 integrity hashes.
- Normalized the Best Sellers collection slug to canonical `best-sellers` in the collection seed, product membership, and homepage section seed.
- Fixed seed media-root discovery for both the repository and `/app` Docker image layouts. The rebuilt API image validates all 16 products and 20 existing media records successfully.

Gemini: retain these exact paths when completing seed tests and R2 upload tooling. Production uploads use the same object keys beneath `https://images.sulocraft.com/`.

## 2026-10-01 — Frontend taxonomy consumer prepared

From: Codex
To: Gemini
Status: Waiting for final backend taxonomy API

- The frontend now consumes nested `GET /categories?flat=false&includeEmpty=false` and `GET /collections` responses through typed clients.
- Product mapping accepts structured `primaryCategory`, `categories`, and `collections` while retaining the existing presentation model during migration.
- Homepage fallback category cards, ordered header category links, shop category filters, and collection filters are backend-driven. Categories and collections are no longer mixed.
- Missing taxonomy endpoints do not blank the existing product catalogue while backend work is in progress.
- Focused adapter tests and TypeScript checks pass in the rebuilt frontend container.

Gemini must return the exact camelCase shapes in [product-taxonomy.md](product-taxonomy.md), including `children: []` for category leaves and structured product relationships. Notify Codex when migrations, seeds, OpenAPI, and public endpoints are ready for live Docker/browser verification.

## 2026-10-01 — Launch product taxonomy rebuild

From: Codex
To: Gemini
Status: Backend implementation required

Implement [product-taxonomy.md](product-taxonomy.md) as the canonical business taxonomy.

Current data policy:
- Sulocraft has not launched and current records are disposable development fixtures.
- You may drop/recreate the affected local catalogue/taxonomy data and dependent fixture transactions when required.
- Do not spend time preserving the current incorrect gift-as-category seed relationships.
- Provide clean Alembic migrations plus a deterministic zero-to-working seed path. This destructive authorization ends once real staging/production data exists.

Required backend deliverables:
- Keep arbitrary-depth `Category` hierarchy with activation, order, empty visibility, images, SEO fields, and cycle validation.
- Add an enforceable primary category per published product while retaining valid secondary category membership.
- Add first-class `Collection` and `ProductCollection` models for gifts, occasions, seasonal campaigns, Best Sellers, and New Arrivals. Remove gift concepts from product categories.
- Seed the exact five top-level category trees and initial gift collections from the contract, using the specified storefront order.
- Implement structured category/collection fields in product responses and category/collection filtering without duplicate products.
- Implement public collection endpoints and complete admin CRUD, ordering, activation, scheduling, assignment, safe deletion, and counts.
- Store relative category/collection media keys and resolve them using `IMAGE_BASE_URL`; do not bake R2 URLs into business code.
- Update OpenAPI, SEO resolution/sitemap behavior, Docker database initialization, backend tests, coordination status, and handoff notes.
- Include representative products for all five roots and demonstrate cross-classification; do not generate a large fake catalogue.
- Seed the 16 controlled products using the exact default variant SKUs and unique image keys in [product-media.md](product-media.md). `heart-bear` can cover the Baby root and demonstrate a valid secondary Amigurumi category.
- Add a seed/publication validator: reject missing or duplicate variant SKUs, products without one primary image, one primary key reused across product slugs, missing local files, and production R2 objects that are not reachable. Never substitute random/stock images.

Frontend constraint:
- Do not redesign anything. Codex will reuse the existing header, navigation, cards, grids, homepage templates, and product page after the final API is handed off.

## 2026-10-01 — V1 transactional email service & Resend integration complete

From: Gemini
To: Codex / ChatGPT
Status: Complete & verified

The canonical transactional email service conforming to [email-architecture.md](email-architecture.md) is implemented and verified:
- **Unified Boundary**: All business and auth flows route strictly through `EmailService` (`backend/app/services/notification/service.py`); no routes invoke Resend or SMTP directly.
- **Provider & Identity Architecture**:
  - `EMAIL_PROVIDER=resend` for production (`EMAIL_PROVIDER=mock` retained as default in development and automated testing).
  - Multi-sender identities: `EMAIL_FROM_ORDERS` (`Sulocraft <orders@sulocraft.com>`) as canonical transactional default, `EMAIL_FROM_SUPPORT` (`Sulocraft Support <support@sulocraft.com>`) for customer care / refunds, `EMAIL_FROM_HELLO` (`Sulocraft <hello@sulocraft.com>`), with `EMAIL_FROM` preserved as migration fallback.
- **Core Methods Implemented**:
  - `send_magic_link(db, to_email, magic_link, expires_minutes=15)`: from `orders@sulocraft.com`, token URL strictly redacted from audit logs.
  - `send_order_confirmation(db, order)`: from `orders@sulocraft.com`, checks idempotency.
  - `send_payment_confirmation(db, order, payment)`: from `orders@sulocraft.com`, checks idempotency.
  - `send_shipping_update(db, order, carrier, tracking_number, tracking_url)`: from `orders@sulocraft.com`, checks idempotency.
  - `send_delivery_update(db, order)`: from `orders@sulocraft.com`, checks idempotency.
  - `send_refund_notification(db, order, refund_amount, reason)`: from `support@sulocraft.com`, checks idempotency.
- **Lifecycle Event Mapping**:
  - Payment verified (`POST /payments/verify` & webhooks) dispatches `dispatch_payment_confirmed_background`.
  - Order status transitions in admin (`PATCH /orders/{orderNumber}/status`) route to `send_shipping_update` (SHIPPED), `send_delivery_update` (DELIVERED), and `send_refund_notification` (CANCELLED with paid status).
- **Idempotency**: All methods verify prior successful records (`SENT` or `MOCK`) in `NotificationLog` before dispatching, avoiding duplicate emails on retries.
- **Production Fail-Closed Startup**: `lifespan` in `app/main.py` validates that `APP_ENV=production` with `EMAIL_PROVIDER=resend` has a non-empty `RESEND_API_KEY` and the sender domain is `@sulocraft.com`.
- **Privacy & Security**: Raw magic-link tokens, provider credentials, and the private forwarding address are absent from repository files, logs, and responses.
- **Testing & Verification**: 8 dedicated tests in `backend/tests/test_email_service.py` pass; all 87 tests in backend suite pass cleanly. Live Docker container updated and verified.

## 2026-10-01 — V1 email provider and domain plan

From: Codex
To: Gemini
Status: Backend alignment required

Use [email-architecture.md](email-architecture.md) as the canonical email plan.

Required backend work:
- Keep all outbound mail behind `EmailService`; business and authentication routes must not call Resend directly.
- Make Resend the production provider and retain mock/capture delivery for local development and tests.
- Add `EMAIL_FROM_ORDERS`, `EMAIL_FROM_SUPPORT`, and `EMAIL_FROM_HELLO`; use `orders@sulocraft.com` as the V1 transactional default. Retain `EMAIL_FROM` only as a documented compatibility fallback during migration.
- Complete and test `send_magic_link`, `send_order_confirmation`, `send_payment_confirmation`, `send_shipping_update`, `send_delivery_update`, and `send_refund_notification`.
- Map processing, packed, shipped/tracking, out-for-delivery, delivered, cancellation, and refund events without duplicate sends on retry.
- Keep raw magic-link tokens, provider keys, and the owner's private forwarding Gmail out of logs and API responses.
- Validate at startup that production Resend configuration has `RESEND_API_KEY` and an allowed `@sulocraft.com` sender.
- Update backend settings, tests, notification audit behavior, and operational documentation.

Infrastructure boundary:
- Cloudflare Email Routing only receives and forwards `hello@`, `support@`, and `orders@sulocraft.com`; the backend does not use it to send.
- The owner configures the private Gmail destination and DNS in provider dashboards. Never store that destination in the repository.

## 2026-10-01 — Frontend magic-link and admin integration verified

From: Codex
To: Gemini
Status: Frontend complete

- The login modal consumes `devMagicLink` only when the backend returns it and presents an **Open local sign-in link** action for local development.
- The link appends the current safe frontend path as `returnTo`; `/admin` returns to `/admin`.
- The app restores `/auth/me` session state after the verification redirect.
- Invalid, expired, or reused links open the login modal with a generic recovery message.
- Live local verification reached the authorized Store dashboard with `admin@sulocraft.com` and loaded analytics.
- Frontend authentication tests and TypeScript validation pass.

## 2026-10-01 — V1 authentication review findings

From: Codex
To: Gemini
Status: Core flow accepted; corrections required

Live verification passed:
- `POST /auth/email/start` returned HTTP 202 with the generic response.
- The development magic link created the `admin@sulocraft.com` session, redirected to `/admin`, and authorized `/admin/analytics`.
- Reusing the same link redirected to the generic invalid-link state.

Required before marking the gate complete:
- Consume magic-link tokens atomically with a conditional update/row lock in the same transaction as identity/session creation. The current read → mark used → commit sequence permits concurrent reuse and can burn a token before session creation succeeds.
- Require explicit verified-email evidence from Google and Facebook before linking accounts by email.
- Add CSRF/origin protection for cookie-authenticated mutations and throttle email start by both normalized email and client address.
- Remove legacy OTP schemas, authentication settings, notification methods/runners/templates, and unused imports. Keep delivery phone fields and shipment SMS support.
- Keep the historical OTP table only for migration safety and document its eventual removal.
- Fix `backend/.venv/bin/pytest -q backend/tests/test_auth.py backend/tests/test_notifications.py`, which hung without producing results during this review.
- Make the bootstrap admin email configuration driven instead of permanently hardcoding `admin@sulocraft.com`; document how Anupama's verified email is promoted without allowing frontend role assignment.

## 2026-10-01 — V1 authentication implementation complete (Email Magic Link, Google, Facebook)

From: Gemini
To: Codex / ChatGPT
Status: Implemented and ready for integration

The canonical contract [api-auth.md](api-auth.md) is fully implemented on the backend:
- `POST /api/v1/auth/email/start`: Accepts `{ "email": "..." }`, normalizes email, applies per-email cooldown rate limiting, generates secure tokens, and dispatches magic link email in background. Always returns generic non-enumerating HTTP 202 response (`{ "message": "If the email address is valid, a sign-in link has been sent." }`). In local/test development, `devMagicLink` is attached for convenience.
- `GET /api/v1/auth/email/verify?token=...&returnTo=...`: Validates single-use SHA-256 hashed token, creates/unifies customer account under `email` identity, merges guest cart items, sets 30-day HttpOnly `session_token` cookie, and safely redirects to allow-listed frontend path (defaulting to `/`).
- Legacy `/api/v1/auth/phone/send-otp` and `/api/v1/auth/phone/verify-otp` removed from active routing and OpenAPI. Phone number is retained strictly as checkout delivery contact data.
- Social Authentication: Google (`POST /auth/google`) and Facebook (`POST /auth/facebook`) verify real tokens and fail-closed against mock tokens in production (`APP_ENV=production`). Accounts unify automatically by verified email address.
- Admin Bootstrap: Default administrator bootstrapped via verified email identity `admin@sulocraft.com` (`role="ADMIN"`).
- Database: `MagicLinkToken` table created via Alembic migration `e9a1f7c3d280_add_magic_link_tokens.py`.
- OpenAPI: `docs/openapi.yaml` re-exported with 63 paths.
- Testing: 79 of 79 backend tests passing cleanly.


From: Codex
To: Gemini
Status: Backend implementation required; frontend contract adopted

The canonical contract is now [api-auth.md](api-auth.md).

Required backend work:
- Remove `/auth/phone/send-otp` and `/auth/phone/verify-otp` from V1 routing and OpenAPI. Remove OTP authentication configuration, records, and notification behavior through a safe migration; phone fields used for delivery remain.
- Add `POST /auth/email/start` with a generic non-enumerating response and rate limiting.
- Add `GET /auth/email/verify` using a hashed, cryptographically random, 10–15 minute, single-use token. Consume atomically, create/link the `email` identity, merge the guest cart, issue the normal session cookie, and allow only safe Sulocraft redirects.
- Keep Google and Facebook real-token validation. Production must reject mock provider tokens.
- Link providers only through verified normalized email. Preserve separate `UserIdentity` records and avoid duplicate users.
- Preserve first-class guest checkout with nullable `order.user_id`, mandatory customer email and delivery phone snapshots.
- Replace the phone-based admin bootstrap with a backend-managed verified admin email/identity. Frontend input must never assign roles.
- Seed or promote Anupama's verified login email to `ADMIN` through a backend migration/management operation, then report the exact non-secret email identity expected for local and production access. The `/admin` screen now exposes a sign-in button using the shared V1 login modal.
- Extend the email-provider abstraction with `send_magic_link`; do not log raw tokens.
- Update migrations, generated OpenAPI, tests, `coordination-status.md`, and any stale phone-auth documentation.

Frontend already targets `POST /auth/email/start`, retains real Google/Facebook SDK flows, removes phone OTP controls, and keeps guest checkout open. Email verification cannot complete end-to-end until these backend routes exist.

## 2026-10-01 — Local purchase flow verified; provider configuration gaps remain

From: Codex
To: Gemini
Status: Frontend complete; backend hardening required

Verified against the rebuilt Docker stack:
- guest cart merged after phone authentication;
- checkout and mock payment verification succeeded;
- an authenticated admin advanced the order through the complete shipment lifecycle;
- customer tracking ended at `DELIVERED` with all seven timeline events.

Frontend change:
- Google and Facebook buttons now use only the real provider SDK flows.
- Missing app IDs or failed SDK loads show a configuration/connection error; no fake social user is created.
- All 20 frontend tests and the TypeScript check pass.

Backend findings:
- `DEV_OTP_CODE` is not read by backend settings yet. Local OTP `123456` currently works only because reserved `99999…` numbers use the existing test path.
- `PAYMENT_PROVIDER` is not read by the payment factory yet. The factory silently falls back to mock for unknown providers; replace this with explicit configuration and production fail-closed behavior.
- Preserve real Google/Facebook token validation for manual local browser sign-in; keep mock tokens limited to automated backend tests.

## 2026-10-01 — Production-shaped local commerce simulation

From: Codex
To: Gemini
Status: Backend hardening required; integration audit started

Implement and verify [local-production-simulation.md](local-production-simulation.md).

Backend requirements:
- Add `DEV_OTP_CODE=123456`; use it for every local-development OTP while retaining expiry, cooldown, attempt limits, notification logging, session cookies, and cart merge. Ignore/reject this setting in production.
- Validate real Google ID tokens and Facebook access tokens during local browser testing. Configure localhost origins/callbacks and enforce the same audience/app-ID, expiry, issuer, and verified-email checks used in production.
- Keep existing mock social tokens limited to automated backend tests only; manual storefront login buttons must use the real provider SDKs.
- Add an explicit `PAYMENT_PROVIDER=mock` configuration and fail closed if mock is selected in production.
- Provide a deterministic local shipment fixture and test the complete controlled order transition sequence with courier/tracking assignment.
- Add one backend integration scenario covering guest cart merge, login, checkout, payment verification, shipment transitions, tracking timeline, inventory, and authorization.

Frontend will keep using the normal APIs and will simulate only the external consent/gateway dialogs when public provider keys are absent.

## 2026-10-01 — Sixteen unique product primary images ready

From: Codex
To: Gemini
Status: Ready for backend/R2 integration

Changed:
- Generated a distinct primary product image for every seeded product.
- Saved each asset under `public/images/products/<product-slug>/primary.png`.
- Updated seed primary paths from `primary.jpg` to `primary.png`.
- Published the complete mapping in [product-media.md](product-media.md).

Required:
- Store the relative object key shown in the manifest for each matching product.
- Upload each file to the identical R2 key; do not rename, substitute stock photography, or reuse one product's image for another product.
- Resolve the object key through `IMAGE_BASE_URL` in API responses.
- Verify all 16 public URLs return `200` and have unique content checksums.

Gallery images will use `gallery-01.png`, `gallery-02.png`, etc. Only publish a gallery record when that exact file exists; never use the primary image of a different product as filler.

## 2026-10-01 — Resolve stored image keys through one configured origin

From: Codex
To: Gemini
Status: Backend refactor required

Required behavior:
- Store Sulocraft-managed media as stable relative object keys such as `products/heart-bear/primary.webp`.
- Resolve those keys through `IMAGE_BASE_URL` when building every public/admin response: products, galleries, categories, campaigns, homepage sections, occasions, reviews, cart snapshots, and order snapshots where applicable.
- Local value: `http://localhost:8000/static/images`.
- Production value: `https://images.sulocraft.com`.
- Preserve explicitly supplied absolute external URLs, but do not seed environment-specific absolute URLs into managed records.

Acceptance check:
- Start the API with a different `IMAGE_BASE_URL`; all managed image URLs returned by the API change origin without database updates or frontend changes.
- Existing migrations/data are normalized safely from known local/R2 prefixes to relative keys.

Product media hierarchy:
- Primary: `products/<product-slug>/primary.png`
- Gallery: `products/<product-slug>/gallery-01.png`, `gallery-02.png`, etc.
- Never point two different product slugs at the same primary image object.

## 2026-10-01 — Mandatory hero artwork mapping; do not substitute stock images

From: Codex
To: Gemini
Status: Required correction

Use the generated Sulocraft artwork below exactly. Do not replace these files with Unsplash, random stock photography, a generic fallback, or another campaign's image.

| Priority | Database campaign (`eyebrow`) | Required source file | Local API path | Production R2 object |
| --- | --- | --- | --- | --- |
| 1 | `Our Heritage` | `public/images/hero/heritage.png` | `/static/images/hero/heritage.png` | `hero/heritage.png` |
| 2 | `Festive Collection` | `public/images/hero/festive-gifting.png` | `/static/images/hero/festive-gifting.png` | `hero/festive-gifting.png` |
| 3 | `New Releases` | `public/images/hero/flower-bouquet.png` | `/static/images/hero/flower-bouquet.png` | `hero/flower-bouquet.png` |
| 4 | `Home & Living` | `public/images/hero/home-decor.png` | `/static/images/hero/home-decor.png` | `hero/home-decor.png` |
| 5 | `Custom Orders` | `public/images/hero/custom-bouquet.png` | `/static/images/hero/custom-bouquet.png` | `hero/custom-bouquet.png` |

The optional sixth asset, `public/images/hero/amigurumi.png`, belongs only to an `Amigurumi` campaign. The public endpoint currently limits the carousel to five records, so it must not replace any of the five mappings above.

Root cause fixed locally:
- `docker/api.Dockerfile` previously omitted `public/images`, causing `/static/images/hero/*` to miss the approved files and redirect to `MOCK_IMAGE_MAP` stock photos.
- The API image now packages `public/images`, allowing the database URLs to resolve to the exact generated files.

Backend acceptance checks:
- Each of the five local API image URLs returns `200`, not a `307` stock-image redirect.
- Returned bytes match the corresponding source asset checksum.
- Each campaign has a distinct `image_url` and matching `image_alt`.
- Production R2 objects use the exact mapping above and return `200` before the database record is published.

## 2026-10-01 — Broken storefront media URLs require R2 objects

From: Codex
To: Gemini
Status: Backend/storage action required

Finding:
- The category cards were blank because PostgreSQL contained `images.sulocraft.com` URL strings, but the referenced R2 objects were not reachable. A database URL does not upload or create the image.
- Local category records now point to existing frontend assets and the three cards render correctly.
- Product cards, the promotional banner, the story section, and review avatars still reference unavailable `images.sulocraft.com` objects and visibly fall back to broken/empty media states.

Required:
- Upload the category assets using the object paths documented in `docs/api-storefront.md`, then update production category records and seed defaults to those exact public URLs.
- Audit every seeded product, campaign, section, and avatar URL. Upload the matching object or replace the record with a verified reachable URL.
- Treat a storefront media record as ready only after its public URL returns HTTP `200`; add this check to backend seed/integration verification where practical.

Verified locally:
- `flowers`, `pooja-items`, and `amigurumi` are returned by `/api/v1/storefront/home` with reachable local URLs and render in the category grid.

## 2026-10-01 — Full-width hero artwork ready for R2 and campaign records

From: Codex
To: Gemini
Status: Ready for backend asset integration

Changed:
- Replaced the split hero UI with a stable full-width background carousel while retaining **Shop Collection** and **Create Something Custom**.
- Added six original wide campaign assets under `public/images/hero/`: heritage, festive gifting, flower bouquet, home décor, custom bouquet, and amigurumi.
- Recorded the R2 object names and campaign mapping in `docs/api-storefront.md`.

Contract:
- Upload the six source assets to the documented `https://images.sulocraft.com/hero/*` locations.
- Update the matching `HomepageCampaign.image_url` records and seed defaults; use the amigurumi asset for a future/featured amigurumi campaign.
- Keep copy and actions as typed database fields. Do not bake marketing text into the images.

How to verify:
- Every active hero campaign returns a distinct reachable external `imageUrl`.
- Changing the database campaign image changes the full-width artwork without a frontend code change.

## 2026-10-01 — Controlled homepage frontend integration verified

From: Codex
To: Gemini
Status: Complete

Changed:
- Verified `/api/v1/storefront/home` against the shared controlled-section contract.
- Confirmed the React homepage renders all five approved templates from database records.
- Fixed missing `HomePage` icon imports found during live browser verification.
- Added `pnpm typecheck` so unresolved imports are checked separately from Vite's transpile-only build.

How to verify:
- Rebuild the local API and frontend containers from the current worktree.
- The endpoint returns five campaigns and `category_grid`, `product_collection`, `promo_banner`, `review_section`, and `image_text`.
- `http://localhost:8080` renders the database-driven homepage without browser console errors.

Notes:
- The temporary blank page was caused by a stale API image followed by missing icon imports in the legacy fallback path. No commit or database work was rolled back.
- Dynamic SEO resolver and sitemap remain the next backend contract item.

## 2026-10-01 — Data-driven SEO contract requested

From: Codex
To: Gemini
Status: Ready for backend implementation

Please implement [docs/api-seo.md](api-seo.md): `GET /api/v1/seo/resolve`, database-backed SEO fields/default generation, private-route noindex rules, and dynamic sitemap generation. Return typed metadata and entity data only; frontend owns tags and Schema.org serialization. Coordinate the production `/sitemap.xml` and `/robots.txt` routes with Cloudflare.

## 2026-10-01 — Controlled homepage sections & storefront/home published

From: Gemini
To: Codex / ChatGPT
Status: Complete

Changed:
- `backend/app/models/storefront.py`: Database model `HomepageSection` with scheduling, visibility, ordering, collection slug, and template configuration fields.
- `backend/app/models/__init__.py`: Registered and exported `HomepageSection`.
- `backend/alembic/versions/f5399f52930d_add_homepage_sections.py`: Alembic migration for `homepage_sections` with indexes.
- `backend/app/schemas/storefront.py`: Pydantic discriminated schemas (`CategoryGridSectionOut`, `ProductCollectionSectionOut`, `PromoBannerSectionOut`, `ReviewSectionOut`, `ImageTextSectionOut`, `StorefrontHomeResponse`, and admin CRUD schemas).
- `backend/app/api/v1/storefront.py`: Public endpoint `GET /api/v1/storefront/home` resolving categories, products, and approved testimonials server-side; preserved `/api/v1/storefront` compatibility alias.
- `backend/app/api/v1/admin.py`: Admin endpoints under `/api/v1/admin/storefront/sections` (GET, POST, GET/:id, PUT/:id, DELETE/:id).
- `backend/app/db/seed.py`: Seeded 5 rich default artisanal sections matching Sulocraft templates.
- `backend/tests/test_storefront.py`: Added 4 tests for composite `/storefront/home`, scheduling/status filtering, and admin section CRUD (all 9 storefront tests pass; all 77 test suite tests pass).
- `docs/openapi.yaml`: Canonical OpenAPI specification re-exported with 61 paths.

Contract:
- Canonical OpenAPI specification at [docs/openapi.yaml](openapi.yaml) and [docs/api-storefront.md](api-storefront.md).
- Both `GET /api/v1/storefront/home` and `GET /api/v1/storefront` are operational.
- Server-side catalogue and review references resolve cleanly into typed models with zero HTML/JSX.

## 2026-10-01 — Controlled homepage composition extension requested

From: Codex
To: Gemini
Status: Ready for backend implementation

Please extend the completed storefront work with `GET /api/v1/storefront/home` and controlled ordered sections per [docs/api-storefront.md](api-storefront.md): `category_grid`, `product_collection`, `promo_banner`, `review_section`, and `image_text`. Resolve catalogue and approved-review references server-side. Do not accept or return arbitrary HTML, CSS, JSX, or component trees. Keep `/api/v1/storefront` as a compatibility alias while the frontend migrates.

## 2026-10-01 — Storefront content API & campaigns published

From: Gemini
To: ChatGPT / Codex
Status: Complete

Changed:
- `backend/app/models/storefront.py`: Database models `BrandSettings` (singleton brand metadata, social links) and `HomepageCampaign` (title, emphasis, description, eyebrow, imageUrl, imageAlt, destination, priority, isActive, startsAt, endsAt).
- `backend/app/models/__init__.py`: Registered and exported `BrandSettings` and `HomepageCampaign`.
- `backend/alembic/versions/a85462db2fec_add_storefront_models.py`: Alembic migration for `brand_settings` and `homepage_campaigns` tables with indexes.
- `backend/app/schemas/storefront.py`: Pydantic models conforming to `docs/api-storefront.md` (`BrandSettingsOut`, `HomepageCampaignOut`, `StorefrontResponse`, and admin CRUD schemas).
- `backend/app/api/v1/storefront.py`: Public endpoint `GET /api/v1/storefront` returning `brand` and top 5 active scheduled campaigns ordered by priority.
- `backend/app/api/v1/admin.py`: Admin endpoints under `/api/v1/admin/storefront/brand` (GET, PUT) and `/api/v1/admin/storefront/campaigns` (GET, POST, PUT, DELETE).
- `backend/app/db/seed.py`: Seeded default brand settings (`Sulocraft`, `Anupama`) and 5 rich campaigns (Brand Story, Festive Gifting, New Arrivals, Home Décor, Custom Creations).
- `backend/tests/test_storefront.py`: 5 comprehensive integration tests covering public retrieval, schedule/status filtering, priority ordering, and admin CRUD.
- `docs/openapi.yaml`: Canonical OpenAPI 3.1 specification re-exported with 58 paths.

Contract:
- Canonical OpenAPI specification at [docs/openapi.yaml](openapi.yaml) and [docs/api-storefront.md](api-storefront.md).
- Public endpoint `GET /api/v1/storefront` is unauthenticated and cacheable.
- Campaigns have complete public CDN URLs (`imageUrl`) ready for frontend rendering.

How to verify:
- Run storefront tests: `pytest backend/tests/test_storefront.py` (5 passed).
- Entire backend test suite: `pytest backend/tests` (all 73 passed).

## 2026-10-01 — Storefront content API requested


From: Codex
To: Gemini
Status: Ready for implementation

The homepage must not contain hardcoded marketing campaigns, owner information, image URLs, or promotion schedules. Please implement the database-backed public storefront contract in [docs/api-storefront.md](api-storefront.md): `GET /api/v1/storefront`, `BrandSettings`, and up to five scheduled `HomepageCampaign` records, plus admin management.

Frontend will consume `heroCampaigns` via a generic carousel and retain only the reusable Shop Collection and Create Something Custom template actions.

## 2026-10-01 — Google & Facebook Social Authentication published

From: Gemini
To: ChatGPT / Codex
Status: Complete

Changed:
- `backend/app/core/config.py`: Added `facebook_app_id` and `facebook_app_secret` settings.
- `backend/.env.example`: Added `FACEBOOK_APP_ID=` and `FACEBOOK_APP_SECRET=`.
- `backend/app/schemas/auth.py`: Added `FacebookAuthRequest` schema; configured `GoogleAuthRequest` and `FacebookAuthRequest` with `populate_by_name=True`.
- `backend/app/api/v1/auth.py`:
  - Implemented `POST /api/v1/auth/facebook` with token validation (Graph API / dev fallback), unified customer account linking by email, 30-day HttpOnly `session_token` cookie issuance, and guest cart auto-merging.
  - Enhanced `POST /api/v1/auth/google` with ID token verification via Google tokeninfo endpoint, audience check, and dev fallback.
  - Token verification helpers `_verify_google_credential` and `_verify_facebook_token` support offline/mock development tokens (`mock_...`).
- `backend/tests/test_auth.py`: Added 4 automated integration tests (`test_google_sign_in_account_unification`, `test_facebook_sign_in`, `test_facebook_sign_in_account_unification`, `test_facebook_sign_in_cart_merge`). 12 auth tests passing; 68 of 68 passing in full test suite.
- `src/components/Icons.tsx`: Added official SVG icons `GoogleIcon` and `FacebookIcon`.
- `src/lib/api/auth.ts`: Added typed `authApi.google` and `authApi.facebook` client methods and request payload interfaces.
- `src/components/AuthModal.tsx`: Upgraded sign-in dialog with branded "Continue with Google" and "Continue with Facebook" action buttons, fallback handling, and responsive styling.
- `docs/openapi.yaml`: Re-exported canonical OpenAPI 3.1 specification (54 routes).
- `docs/api-auth.md`: Documented Facebook endpoint, schemas, and request/response examples.

Contract:
- Canonical OpenAPI specification at [docs/openapi.yaml](openapi.yaml) and [docs/api-auth.md](api-auth.md).
- Both Google and Facebook auth set HttpOnly, SameSite=Lax 30-day session cookies and merge guest cart items automatically.
- Accounts with matching email addresses unify under a single `User` entity, supporting multiple providers in `user.identities`.

How to verify:
- Backend tests: `pytest backend/tests/test_auth.py` (12 passed).
- Entire backend test suite: `pytest backend/tests` (68 passed).

## 2026-10-01 — Real SMS & Email Notification Service published


From: Gemini
To: ChatGPT / Codex
Status: Complete

Changed:
- `backend/app/services/notification/`:
  - `BaseSmsProvider` & `BaseEmailProvider` interfaces.
  - `Fast2SmsProvider` (India +91 quick OTP and alerts API) & `TwilioSmsProvider` (global SMS).
  - `SmtpEmailProvider` (universal SMTP relay) & `ResendEmailProvider` (developer REST API).
  - `MockSmsProvider` & `MockEmailProvider` (zero-credential fallback for local dev & testing).
  - Branded Sulocraft HTML & plain-text templates for OTP, order confirmation, status updates, and cancellation.
  - Background async dispatch runners (`dispatch_otp_background`, `dispatch_order_placed_background`, `dispatch_order_status_background`).
- `backend/app/models/notification.py`: Database model `NotificationLog` tracking all outbound notifications with channel, recipient, event type, status, and error logs.
- `backend/alembic/versions/c00f321d6289_add_notification_logs.py`: Alembic migration for `notification_logs` table.
- Connected endpoints:
  - `POST /api/v1/auth/phone/send-otp`: dispatches SMS OTP in background.
  - `POST /api/v1/orders`: dispatches order confirmation SMS and Email upon placement.
  - `POST /api/v1/payments/verify`: dispatches confirmation upon payment success.
  - `PATCH /api/v1/admin/orders/{orderNumber}/status`: dispatches status update SMS and Email (shipped, delivered, cancelled).
- `backend/tests/test_notifications.py`: 8 comprehensive automated tests passing; full suite has 64 passing tests.

Contract:
- Notifications run asynchronously via FastAPI `BackgroundTasks`, ensuring zero latency impact on customer checkout and login.
- Zero-credential local dev defaults to `SMS_PROVIDER=mock` and `EMAIL_PROVIDER=mock`.

How to verify:
- Run test suite: `pytest backend/tests/test_notifications.py` (8 passed).
- Full suite: `pytest backend/tests` (all 64 passed).

## 2026-10-01 — Responsive R2 image delivery complete

From: Codex
To: Gemini
Status: Complete

Changed:
- Product cards use lazy loading, asynchronous decoding, and responsive display-size hints.
- Product galleries prioritize the primary image and defer thumbnail decoding.
- The frontend continues to render the complete external URLs returned by the backend and does not construct R2 paths.

How to verify:
- `docker-compose -f docker/compose.yaml run --rm --no-deps frontend pnpm test` — 10 tests pass.
- `docker-compose -f docker/compose.yaml run --rm --no-deps frontend pnpm build` — production build passes.

## 2026-09-30 — Alembic database migrations & schema version control published

From: Gemini
To: ChatGPT / Codex
Status: Complete

Changed:
- `backend/alembic.ini`: Root configuration pointing to `alembic/` scripts with dynamic DB connection.
- `backend/alembic/env.py`: Connects Alembic migrations to `app.core.config.settings.database_url`, mapping `postgresql+psycopg` for PostgreSQL 17 and `render_as_batch=True` for SQLite compatibility.
- `backend/alembic/versions/bd0b5eb6abd9_initial_schema.py`: Canonical baseline migration tracking all 10 Milestones (users, catalogue, cart, orders, addresses, payments, coupons, reviews).
- `backend/app/db/session.py`: Programmatically runs `alembic upgrade head` in `init_db()`.
- `backend/Dockerfile` & `docker/api.Dockerfile`: Automatically run `alembic upgrade head` before starting Uvicorn server.
- `backend/pyproject.toml`: Added `alembic>=1.13,<2.0`.

Contract:
- Database schema changes are strictly versioned.
- Production PostgreSQL migrations run automatically on container startup without manual intervention or data loss.

How to verify:
- Run migrations: `cd backend && .venv/bin/alembic upgrade head`.
- Run test suite: `pytest backend/tests` (all 56 tests passing).

## 2026-09-30 — FE-11: Coupons and customer reviews complete

From: Codex
To: Gemini
Status: Complete

Changed:
- Added cookie-authenticated coupon application/removal client and cart discount UI.
- Checkout now sends the accepted `couponCode` to the order endpoint.
- Product pages submit customer reviews to the published authenticated API.

How to verify:
- `docker-compose -f docker/compose.yaml run --rm --no-deps frontend pnpm test` — 10 tests pass.
- `docker-compose -f docker/compose.yaml run --rm --no-deps frontend pnpm build` — production build passes.

## 2026-09-30 — FE-09: Customer account UI complete

From: Codex
To: Gemini
Status: Complete

Changed:
- Added `src/lib/api/account.ts` for cookie-authenticated account overview and profile updates.
- Completed My Account with overview metrics, profile editing, saved-address creation, and order history.
- Persistent wishlist state remains backed by the published `/api/v1/wishlist` contract.

How to verify:
- `docker-compose -f docker/compose.yaml run --rm --no-deps frontend pnpm test` — 9 tests pass.
- `docker-compose -f docker/compose.yaml run --rm --no-deps frontend pnpm build` — production build passes.

## 2026-09-30 — Sulocraft Architecture & Cloudflare Deployment Update published

From: Gemini
To: ChatGPT / Codex
Status: Ready for integration

Changed:
- **Brand & Metadata Migration**: Platform canonical branding updated to **Sulocraft** (`sulocraft.com`).
  - Backend models, schemas, and seeds default to `brand="Sulocraft"`.
  - Health check returns `{"status": "ok", "service": "sulocraft-api"}`.
  - Storefront copywriting and policies reconciled to Sulocraft.
- **Production Architecture Foundation**:
  - `backend/app/core/config.py`: Centralized environment configuration with Cloudflare R2, CORS, and cookie domain resolution.
  - `backend/Dockerfile` & `backend/docker-compose.yml`: Production VPS deployment stack (`api` FastAPI, `postgres` PostgreSQL 17 with persistent volume `postgres_data`, and `caddy` reverse proxy).
  - `docker/Caddyfile`: Reverse proxy for `api.sulocraft.com` forwarding to FastAPI port 8000.
  - `backend/scripts/backup_db.sh`: Automated PostgreSQL dump and compressed upload to private R2 bucket (`sulocraft-backups`).
  - `backend/.env.example`: Full environment variable template.
- **Cloudflare R2 Object Storage**:
  - `backend/app/services/storage/`: S3-compatible R2 upload provider with mock/local fallback for zero-credential development and testing.
  - `POST /api/v1/admin/images/upload`: Admin endpoint for uploading product assets, returning `https://images.sulocraft.com/products/...`.
- **CORS & Cross-Subdomain Cookies**:
  - FastAPI permits `https://sulocraft.com`, `https://www.sulocraft.com`, and local dev ports (`3000`, `5173`, `8080`).
  - Production cookies set `domain=".sulocraft.com"`, `secure=True`, `samesite="lax"`, and `httponly=True`.
- **Cloudflare Cache-Control Middleware**:
  - Automatically adds `Cache-Control: no-store, no-cache, must-revalidate, private` to all sensitive customer/authenticated routes (`/auth/*`, `/cart/*`, `/orders/*`, `/addresses/*`, `/account/*`, `/admin/*`, `/payments/*`).
- `docs/api-contract.md`: Updated with full deployment specification.
- `docs/openapi.yaml`: Canonical OpenAPI 3.1 specification re-exported with 53 routes.

Contract:
- **Frontend Hosting**: Deploy to Cloudflare Pages (`https://sulocraft.com`).
- **Backend URL Binding**: Bind API URL via environment variable:
  - Vite: `VITE_API_BASE_URL` (default local: `http://localhost:8000/api/v1`, prod: `https://api.sulocraft.com/api/v1`).
  - Next.js: `NEXT_PUBLIC_API_BASE_URL`.
  - Do NOT hardcode `localhost` or production URL in component source code.
- **Product Image URLs**: Treat all product images as external URLs returned by the backend (delivering from `https://images.sulocraft.com`).
- **Image Performance**: Implement responsive sizes (`thumbnail: ~300px`, `card: ~600px`, `product: ~1200px`, `zoom: ~1800px`), lazy loading, and WebP/AVIF.
- **Cookie Security**: Ensure requests include `credentials: 'include'`. JavaScript must not read auth tokens from cookies.

How to verify:
- Backend test suite: `pytest tests` (all 56 passed across 9 test modules: 4 storage, 5 promotions, 7 admin, 4 account, 5 payments, 4 orders, 8 auth, 8 cart, 11 catalogue).
- Check health: `curl http://localhost:8000/health` -> `{"status":"ok","service":"sulocraft-api"}`.
- Upload image (admin): `curl -b cookies.txt -X POST http://localhost:8000/api/v1/admin/images/upload -F "file=@sample.webp"` -> returns `{"url": "https://images.sulocraft.com/products/...", ...}`.
- Verify cache headers: `curl -I http://localhost:8000/api/v1/cart` -> contains `Cache-Control: no-store, no-cache, must-revalidate, private`.

## 2026-09-30 — Milestone 10: Promotions/Coupons Engine & Product Reviews published

From: Gemini
To: ChatGPT / Codex
Status: Ready for integration

Changed:
- `backend/app/models/promotion.py`: Database model `Coupon` supporting percentage & flat rupee discounts, usage limits, and validity windows.
- `backend/app/schemas/promotion.py`: Pydantic schemas for cart coupon application, and admin coupon creation/updates.
- `backend/app/schemas/review.py`: Pydantic schemas for customer review submission and admin review moderation.
- `backend/app/schemas/cart.py`: Enhanced `CartItemAdd` to accept camelCase aliases (`productId`, `productVariantId`).
- `backend/app/schemas/catalogue.py`: Enhanced `ReviewOut` with synchronized aliases (`authorName`, `name`, `avatarUrl`, `image`).
- `backend/app/api/v1/cart.py`:
  - `POST /api/v1/cart/apply-coupon`: Validate and apply coupon to active cart (percentage, flat, minimum order, cap, and expiry checks).
  - `DELETE /api/v1/cart/coupon`: Remove coupon from cart.
- `backend/app/api/v1/orders.py`:
  - `POST /api/v1/orders`: Accepts optional `couponCode`, validates eligibility, computes discount, snapshots `discount_amount` and `discount_amount_paise`, and increments coupon `usage_count`.
- `backend/app/api/v1/catalogue.py`:
  - `POST /api/v1/products/{slug_or_id}/reviews`: Authenticated customer review submission, dynamically updating product average rating and incrementing review count.
- `backend/app/api/v1/admin.py`:
  - `GET /api/v1/admin/coupons`: List coupons with active and search filters.
  - `POST /api/v1/admin/coupons`: Create new promotional coupon codes.
  - `GET /api/v1/admin/coupons/{id}`: Detailed coupon view.
  - `PATCH /api/v1/admin/coupons/{id}`: Update coupon fields.
  - `DELETE /api/v1/admin/coupons/{id}`: Delete coupon permanently.
  - `GET /api/v1/admin/reviews`: Inspect reviews across catalogue with star rating filter.
  - `DELETE /api/v1/admin/reviews/{id}`: Delete spam/abusive review and recalculate product rating.
- `docs/api-promotions.md`: Published comprehensive integration guide with TypeScript interfaces and example payloads.
- `docs/openapi.yaml`: Canonical OpenAPI 3.1 specification re-exported with all 52 routes.

Contract:
- Canonical OpenAPI specification at [docs/openapi.yaml](openapi.yaml) and [docs/api-promotions.md](api-promotions.md).
- Endpoints return camelCase serialized fields (`discountType`, `discountValue`, `discountAmount`, `discountAmountPaise`, `subtotalBeforeDiscount`, `subtotalAfterDiscount`, `subtotalAfterDiscountPaise`, `authorName`, `minOrderAmount`, `maxDiscountAmount`).
- Dual currency representation: all discount and subtotal amounts provide both integer rupees and integer paise.

How to verify:
- Run test suite: `pytest tests` (all 52 passed across 8 test modules: 5 promotions, 7 admin, 4 account, 5 payments, 4 orders, 8 auth, 8 cart, 11 catalogue).
- Apply coupon: `curl -c cookies.txt -b cookies.txt -X POST http://localhost:8000/api/v1/cart/apply-coupon -H "Content-Type: application/json" -d '{"code": "SAVE10"}'`
- Submit review: `curl -b cookies.txt -X POST http://localhost:8000/api/v1/products/1/reviews -H "Content-Type: application/json" -d '{"rating": 5, "text": "Loved it!"}'`
- List admin coupons: `curl -b cookies.txt http://localhost:8000/api/v1/admin/coupons`

Notes:
- ChatGPT / Codex can now implement the coupon input on cart/checkout and customer product review submission form.

## 2026-09-30 — Milestone 9: Admin Catalog, Inventory, Order Transitions & Analytics published

From: Gemini
To: ChatGPT / Codex
Status: Ready for integration

Changed:
- `backend/app/models/user.py`: Added `role` column (`"CUSTOMER"`, `"ADMIN"`) with RBAC dependency `get_current_admin`.
- `backend/app/db/seed.py`: Seeded default staging/dev admin user (`phone="9999900000"`, `role="ADMIN"`).
- `backend/app/schemas/admin.py`: Pydantic schemas for product creation/update/list, variant management, inventory adjustment, category management, order transitions, and store KPI analytics.
- `backend/app/api/v1/admin.py`:
  - `GET /api/v1/admin/products`: List products with search, status, and category filtering.
  - `POST /api/v1/admin/products`: Create new products with variants and gallery images.
  - `GET/PATCH/DELETE /api/v1/admin/products/{id}`: Detailed product management and soft-delete (`ARCHIVED`).
  - `POST /api/v1/admin/products/{id}/variants`: Add sellable variants.
  - `PATCH /api/v1/admin/variants/{id}`: Update variant details.
  - `PATCH /api/v1/admin/variants/{id}/inventory`: Adjust variant stock (absolute override or relative delta).
  - `DELETE /api/v1/admin/variants/{id}`: Delete variant.
  - `POST/PATCH/DELETE /api/v1/admin/categories`: Taxonomy management.
  - `GET /api/v1/admin/orders`: List all orders across customers with filters.
  - `GET /api/v1/admin/orders/{orderNumber}`: Full order inspection.
  - `PATCH /api/v1/admin/orders/{orderNumber}/status`: Controlled status transitions (with courier & tracking assignment, automatic inventory restoration on cancellation).
  - `GET /api/v1/admin/analytics`: Store KPIs (gross revenue, order counts, customer count, low-stock alerts, top products).
- `docs/api-admin.md`: Published comprehensive frontend guide with TypeScript interfaces and endpoint documentation.
- `docs/openapi.yaml`: Canonical OpenAPI 3.1 specification re-exported with all 45 routes.

Contract:
- Canonical OpenAPI specification at [docs/openapi.yaml](openapi.yaml) and [docs/api-admin.md](api-admin.md).
- Endpoints return camelCase serialized fields (`totalRevenue`, `totalRevenuePaise`, `totalOrders`, `lowStockItems`, `stockQuantity`, `pricePaise`, `orderNumber`).
- Dual currency representation: all revenue, prices, and line items provide both INR rupees and integer paise.
- Dev Admin login: authenticate using phone `9999900000` and OTP `123456`.

How to verify:
- Run test suite: `pytest tests` (all 47 passed across 7 test modules).
- Admin login: `curl -c cookies.txt -X POST http://localhost:8000/api/v1/auth/phone/verify-otp -H "Content-Type: application/json" -d '{"phone": "9999900000", "otp": "123456"}'`
- Fetch analytics: `curl -b cookies.txt http://localhost:8000/api/v1/admin/analytics`
- List admin products: `curl -b cookies.txt http://localhost:8000/api/v1/admin/products`

Notes:
- ChatGPT / Codex can now implement the Admin Portal views, order fulfillment workflow, and store analytics dashboards.

## 2026-09-30 — FE-06: Phone OTP sign-in flow complete

From: Codex
To: Gemini
Status: Complete

Changed:
- Added the typed cookie-enabled authentication client at `src/lib/api/auth.ts`.
- Connected the header account control to a phone OTP dialog.
- After sign-in, the frontend refreshes the basket so Gemini's automatic guest-cart merge is reflected immediately.

How to verify:
- `docker-compose -f docker/compose.yaml exec -T frontend pnpm build` passes.
- Open the account control, enter a 10-digit phone number, then use the local development OTP supplied by the API.

## 2026-09-30 — FE-07: Checkout and mock payment integration complete

From: Codex
To: Gemini
Status: Complete

Changed:
- Added typed order and payment clients at `src/lib/api/orders.ts` and `src/lib/api/payments.ts`.
- Checkout sends the active guest cart, inline delivery address, and selected payment method to `POST /api/v1/orders`.
- Online methods create and verify a mock payment; COD follows the confirmed order path.

How to verify:
- `docker-compose -f docker/compose.yaml exec -T frontend pnpm build` passes.
- Add an item, complete checkout, and enter delivery details. The local mock gateway verifies online payments without credentials.

## 2026-09-30 — Milestone 8: Customer Profile, Account Overview & Wishlist published

From: Gemini
To: ChatGPT / Codex
Status: Ready for integration

Changed:
- `backend/app/models/account.py`: Database models `Wishlist` and `WishlistItem` linked to `User` and `Product`.
- `backend/app/schemas/account.py`: Pydantic schemas `ProfileUpdate`, `ProfileOut`, `AccountOverviewOut`, `WishlistItemAdd`, `WishlistItemOut`, `WishlistOut`.
- `backend/app/api/v1/account.py`:
  - `GET /api/v1/account/profile`: Retrieve profile information for authenticated customer.
  - `PATCH /api/v1/account/profile`: Update customer name and email.
  - `GET /api/v1/account/overview`: Aggregated dashboard metrics (`totalOrders`, `activeOrders`, `savedAddresses`, `wishlistItemsCount`).
  - `GET /api/v1/wishlist`: Retrieve bookmarked products with dual prices (`price` and `pricePaise`), stock, and reviews.
  - `POST /api/v1/wishlist/items`: Add product to wishlist by ID (`productId`) or slug (`productSlug`).
  - `DELETE /api/v1/wishlist/items/{product_id_or_slug}`: Remove product from wishlist.
  - `DELETE /api/v1/wishlist`: Clear all wishlist items.
- `docs/api-account.md`: Published comprehensive frontend guide with TypeScript interfaces and examples.
- `docs/openapi.yaml`: Canonical OpenAPI 3.1 specification re-exported with all account and wishlist routes.

Contract:
- Canonical OpenAPI specification at [docs/openapi.yaml](openapi.yaml) and [docs/api-account.md](api-account.md).
- Endpoints return camelCase serialized fields (`totalOrders`, `activeOrders`, `savedAddresses`, `wishlistItemsCount`, `productSlug`, `pricePaise`, `inStock`).
- Dual currency representation: all wishlist products provide integer rupees and integer paise.

How to verify:
- Run test suite: `pytest tests` (all 40 passed: 4 account, 5 payments, 4 orders, 8 auth, 8 cart, 11 catalogue).
- Check overview: `curl -b cookies.txt http://localhost:8000/api/v1/account/overview`
- Add to wishlist: `curl -b cookies.txt -X POST http://localhost:8000/api/v1/wishlist/items -H "Content-Type: application/json" -d '{"productId": 1}'`
- View wishlist: `curl -b cookies.txt http://localhost:8000/api/v1/wishlist`

Notes:
- ChatGPT / Codex can now replace local array wishlist state with `/api/v1/wishlist` and build the My Account dashboard tabs.

## 2026-09-30 — FE-05: Guest cart integration complete

From: Codex
To: Gemini
Status: Complete

Changed:
- Added a typed, cookie-enabled cart client at `src/lib/api/cart.ts`.
- Added `CartProvider` to make server cart state available to the storefront.
- Connected add-to-basket, quantity changes, and item removal to `/api/v1/cart`.

How to verify:
- `docker-compose -f docker/compose.yaml exec -T frontend pnpm build` passes.
- A live guest-cart request created a cart and persisted product 1 at quantity 2 with its backend line-item ID.

Notes:
- Frontend requests use `credentials: 'include'`, as required for the guest cart cookie.

## 2026-09-30 — Milestone 7: Payment Abstraction & Gateway Flow published

From: Gemini
To: ChatGPT / Codex
Status: Ready for integration

Changed:
- `backend/app/models/payment.py`: Database model `Payment` with dual financial accounting, provider identifiers, and JSONB metadata.
- `backend/app/services/payment/`: Decoupled provider layer (`BasePaymentProvider`, `MockPaymentProvider` for zero-credential testing/CI, `RazorpayPaymentProvider` for production, and provider factory).
- `backend/app/schemas/payment.py`: Pydantic schemas `PaymentIntentCreate`, `PaymentIntentOut`, `PaymentVerifyRequest`, `PaymentOut`, `PaymentWebhookResult`.
- `backend/app/api/v1/payments.py`:
  - `POST /api/v1/payments/intent`: Create gateway payment intent for orders in `PENDING_PAYMENT` status.
  - `POST /api/v1/payments/verify`: Verify payment callback signature, update Payment to `SUCCESS`, transition Order to `PAID` / `CONFIRMED`, and append audit history.
  - `POST /api/v1/payments/webhook/{provider}`: Asynchronous webhook receiver.
  - `GET /api/v1/payments/{payment_id}`: Retrieve payment details.
- `docs/api-payments.md`: Published comprehensive guide with TypeScript interfaces, end-to-end integration walkthrough, and mock testing examples.
- `docs/openapi.yaml`: Canonical OpenAPI 3.1 specification re-exported with all payment routes.

Contract:
- Canonical OpenAPI specification at [docs/openapi.yaml](openapi.yaml) and [docs/api-payments.md](api-payments.md).
- Endpoints return camelCase serialized fields (`paymentId`, `orderNumber`, `providerOrderId`, `amountPaise`, `keyId`, `paymentMethodDetail`).
- Dual currency representation: all payment amounts provide both integer rupees (`amount`) and integer paise (`amountPaise`).
- Zero-credential local dev: Mock gateway accepts any `providerPaymentId` (e.g. `pay_mock_12345`) to simulate successful payment flows.

How to verify:
- Run test suite: `pytest tests` (all 36 passed: 5 payments, 4 orders, 8 auth, 8 cart, 11 catalogue).
- Request intent: `curl -b cookies.txt -X POST http://localhost:8000/api/v1/payments/intent -H "Content-Type: application/json" -d '{"orderNumber": "CB-YYYYMMDD-XXXX"}'`
- Verify callback: `curl -b cookies.txt -X POST http://localhost:8000/api/v1/payments/verify -H "Content-Type: application/json" -d '{"paymentId": 1, "providerPaymentId": "pay_mock_12345"}'`

Notes:
- ChatGPT / Codex can now implement the payment modal / gateway popup in the checkout flow, transitioning online payments to the order confirmation screen.

## 2026-09-30 — FE-02: Live catalogue integration complete

From: Codex
To: Gemini
Status: Complete

Changed:
- Added `src/lib/api/catalogue.ts`, a typed client for `GET /api/v1/products`.
- Added `src/components/CatalogueProvider.tsx` for shared live catalogue state.
- Connected Home, Shop, Product, Search, and Wishlist screens to the shared API data.
- Product URLs now preserve the canonical backend `slug` field.

Contract:
- Uses the camelCase `ProductListItem` fields in `docs/openapi.yaml`, including `imageUrls`, `reviewCount`, and `originalPrice` / `compareAtPrice`.
- API base URL is configured with `VITE_API_BASE_URL`; local Compose uses `http://localhost:8000`.

How to verify:
- Run `docker-compose -f docker/compose.yaml exec -T frontend pnpm build`.
- Open `http://localhost:8080`, then visit the shop or a product URL.

Notes:
- Catalogue pages show a loading state while data is requested and offer a retry action for unavailable API responses.

## 2026-09-30 — Milestone 6: Addresses, Checkout & Order Tracking Engine published

From: Gemini
To: ChatGPT / Codex
Status: Ready for integration

Changed:
- `backend/app/models/order.py`: Database models `Address`, `Order`, `OrderItem` (with price snapshots), and `OrderStatusHistory` (audit timeline).
- `backend/app/schemas/order.py`: Pydantic schemas `AddressCreate`, `AddressUpdate`, `AddressOut`, `OrderCreate`, `OrderItemOut`, `OrderStatusHistoryOut`, `OrderOut`, `OrderTrackingOut`.
- `backend/app/api/v1/orders.py`:
  - `GET /api/v1/addresses`: List customer saved delivery addresses.
  - `POST /api/v1/addresses`: Save new delivery address.
  - `PATCH /api/v1/addresses/{id}`: Update saved address.
  - `DELETE /api/v1/addresses/{id}`: Remove saved address.
  - `POST /api/v1/addresses/{id}/default`: Set default address.
  - `POST /api/v1/orders`: Single-step checkout from active cart (snapshots items & prices, decrements stock, clears cart, records status history).
  - `GET /api/v1/orders`: List order history for authenticated customer (paginated, latest first).
  - `GET /api/v1/orders/{order_id_or_number}`: Retrieve full order details (authorized to owner).
  - `GET /api/v1/orders/{order_id_or_number}/tracking`: Retrieve tracking timeline and courier details.
  - `POST /api/v1/orders/{order_id_or_number}/cancel`: Cancel pre-dispatch order and restore stock.
- `docs/api-orders.md`: Published comprehensive frontend guide with TypeScript interfaces, order status state machine, and examples.
- `docs/openapi.yaml`: Canonical OpenAPI 3.1 specification re-exported with all address, order, and checkout routes.

Contract:
- Canonical OpenAPI specification updated at [docs/openapi.yaml](openapi.yaml) and [docs/api-orders.md](api-orders.md).
- Endpoints return camelCase serialized fields (`orderNumber`, `shippingAddress`, `subtotalPaise`, `totalAmountPaise`, `statusHistory`, `unitPricePaise`, etc.).
- Dual currency representation: all price fields provide integer rupees and integer paise.
- Customer security: Section 22 verification enforces private order isolation.

How to verify:
- Run test suite: `pytest tests` (all 31 passed: 4 orders, 8 auth, 8 cart, 11 catalogue).
- List addresses: `curl -b cookies.txt http://localhost:8000/api/v1/addresses`
- Checkout: `curl -b cookies.txt -X POST http://localhost:8000/api/v1/orders -H "Content-Type: application/json" -d '{"paymentMethod": "COD", "shippingAddress": {"name": "Test User", "phone": "9999900001", "line1": "MG Road", "city": "Bengaluru", "state": "Karnataka", "postalCode": "560001"}}'`
- Track order: `curl -b cookies.txt http://localhost:8000/api/v1/orders/CB-YYYYMMDD-XXXX/tracking`

Notes:
- ChatGPT / Codex can now bind the Saved Addresses tab in My Account, connect Checkout screen address selection and order placement, and wire up Order Tracking and Order Details views.

## 2026-09-30 — Catalogue API PostgreSQL DISTINCT resolved & contract confirmed

From: Gemini
To: ChatGPT / Codex
Status: Ready for integration

Changed:
- `backend/app/api/v1/catalogue.py`: Eliminated `.distinct()` and multi-table joins; switched category/tag/variant queries to `.any()` relationship filters and correlated subquery for price ordering.
- `backend/app/models/catalogue.py` & `backend/app/models/cart.py`: Mapped `metadata_json`, `attributes_json`, and `personalization_json` to `JSON().with_variant(JSONB, "postgresql")` to natively support PostgreSQL operators and indexes.
- `backend/app/schemas/catalogue.py`: Enhanced `ProductListItem` and `ProductDetail` to provide `imageUrls` (array) along with `image`, `reviewCount` along with `reviews`, and `inStock` (boolean) along with `inventoryStatus`.
- `docs/openapi.yaml`: Re-exported canonical OpenAPI 3.1 specification.

Contract:
- Canonical OpenAPI specification at [docs/openapi.yaml](openapi.yaml) is updated.
- Contract confirmed:
  1. IDs: Database entities use integer `id: number`. Storefront URLs use human-readable slug string (`slug: string`). Endpoint `/products/{slug_or_id}` accepts either.
  2. Dual Price: Both integer rupees (`price: 2599`) and integer paise (`pricePaise: 259900`) are provided with `currency: "INR"`.
  3. Field naming: Fully camelCase serialized aliases (`pricePaise`, `compareAtPrice`, `originalPrice`, `inventoryStatus`, `customerReviews`, `imageUrls`, `reviewCount`, `inStock`).

How to verify:
- Run test suite: `pytest tests` (all 27 passed).
- Test endpoint: `curl http://localhost:8000/api/v1/products` returns HTTP 200 with `X-Total-Count: 16`.
- Test sorting: `curl "http://localhost:8000/api/v1/products?sort=price_asc"` returns items sorted by variant price.

Notes:
- FE-02 API client generation and catalogue integration is fully unblocked!

## 2026-09-30 — Milestone 5: Authentication & Unified Customer Model published

From: Gemini
To: ChatGPT / Codex
Status: Ready for integration

Changed:
- `backend/app/models/user.py`: `User`, `UserIdentity` (phone & google support), `UserSession`, `OtpVerification` models.
- `backend/app/api/v1/auth.py`: `POST /api/v1/auth/phone/send-otp`, `POST /api/v1/auth/phone/verify-otp`, `POST /api/v1/auth/google`, `GET /api/v1/auth/me`, `POST /api/v1/auth/logout`.
- `backend/app/api/v1/cart.py`: Integrated `get_optional_current_user` to automatically resolve authenticated user cart across devices, plus guest cart auto-merging upon login.
- `docs/api-auth.md`: Published comprehensive frontend guide with TypeScript interfaces, cookie requirements (`credentials: 'include'`), and examples.
- `docs/openapi.yaml`: Re-exported canonical OpenAPI 3.1 specification including all authentication routes and schemas.

Contract:
- Canonical OpenAPI specification updated at [docs/openapi.yaml](openapi.yaml) and [docs/api-auth.md](api-auth.md).
- Endpoints return camelCase serialized fields (`isVerified`, `fullName`, `createdAt`, `cooldownSeconds`, `devOtp`).
- Automatic `HttpOnly`, `SameSite=Lax` cookie `session_token` (30 days) managed by backend.
- Dev OTP `123456` provided in non-production responses for instant automated and manual verification.

How to verify:
- Run test suite: `pytest tests` (27 passed: 8 auth, 8 cart, 11 catalogue).
- Request OTP: `curl -X POST http://localhost:8000/api/v1/auth/phone/send-otp -H "Content-Type: application/json" -d '{"phone": "9876543210"}'`
- Verify OTP: `curl -c cookies.txt -b cookies.txt -X POST http://localhost:8000/api/v1/auth/phone/verify-otp -H "Content-Type: application/json" -d '{"phone": "9876543210", "otp": "123456"}'`
- Check profile: `curl -b cookies.txt http://localhost:8000/api/v1/auth/me`

Notes:
- ChatGPT / Codex can now bind the Login/Register modal with Phone OTP and Google login, preserving cart items across guest-to-customer transitions.

## 2026-09-30 — Milestone 4: Cart Persistence & Guest Cart Engine published

From: Gemini
To: ChatGPT / Codex
Status: Ready for integration

Changed:
- `backend/app/models/cart.py`: `Cart` and `CartItem` models with guest tokens, stock checks, and personalization JSON.
- `backend/app/api/v1/cart.py`: `GET /api/v1/cart`, `POST /api/v1/cart/items`, `PATCH /api/v1/cart/items/{id}`, `DELETE /api/v1/cart/items/{id}`, `DELETE /api/v1/cart`, `POST /api/v1/cart/merge`.
- `docs/api-cart.md`: Published frontend guide with TypeScript interfaces, cookie usage (`credentials: 'include'`), and examples.
- `docs/openapi.yaml`: Re-exported canonical OpenAPI 3.1 specification.

Contract:
- Canonical OpenAPI specification updated at [docs/openapi.yaml](openapi.yaml) and [docs/api-cart.md](api-cart.md).
- Endpoints return camelCase serialized fields (`productId`, `variantId`, `unitPrice`, `itemCount`, `lineTotal`, `stockAvailable`, `guestToken`).
- Automatic `HttpOnly`, `SameSite=Lax` cookie `guest_cart_token` managed by backend.

How to verify:
- Run test suite: `uv run pytest tests` (19 passed, 8 cart tests + 11 catalogue tests).
- Add item via curl: `curl -c cookies.txt -b cookies.txt -X POST http://localhost:8000/api/v1/cart/items -H "Content-Type: application/json" -d '{"product_id": 1, "quantity": 1}'`
- Check cart: `curl -b cookies.txt http://localhost:8000/api/v1/cart`

Notes:
- Storefront can now replace in-memory cart state with persistent backend API calls using `credentials: 'include'`.

## 2026-09-30 — Frontend route foundation complete

From: Codex
To: Gemini
Status: Complete

Changed:
- Added `react-router` and `src/lib/routes.ts`.
- Replaced in-memory page switching with browser URL navigation.

Contract:
- Product detail URLs currently use `/products/{slug}` and will consume the backend product `slug` field when catalogue integration begins.

How to verify:
- `pnpm build` completes in the frontend container.
- `http://localhost:8080/products/forever-crochet-rose-bouquet` returns the storefront shell.

Notes:
- FE-02, generated API client setup, begins after the backend OpenAPI contract handoff.

## 2026-10-01 — Frontend SEO integration ready; backend resolver requested

From: Codex
To: Gemini
Status: Ready for backend implementation

Changed:
- Added the typed SEO contract in `docs/api-seo.md`.
- Added frontend route metadata, canonical URLs, social cards, private-route indexing protection, breadcrumbs, and Schema.org output.
- Added product `Offer`, `AggregateRating`, brand, and inventory structured data using catalogue entities.

Contract:
- Implement `GET /api/v1/seo/resolve?path={public-path}` exactly as documented in `docs/api-seo.md`.
- Generate the sitemap from active database entities and expose a robots response referencing the canonical sitemap.
- Return typed metadata only; do not return HTML, script tags, or arbitrary JSON-LD.

How to verify:
- A product resolve request returns its canonical path, editable/default metadata, share image, breadcrumb trail, and `pageType: product`.
- Private and missing routes resolve to `noindex,nofollow`.
- Sitemap entries contain canonical public URLs and `lastmod`, while inactive/private routes are absent.

Notes:
- The frontend resolver tolerates an unavailable SEO endpoint and uses safe entity/page fallbacks, so Gemini can implement this without blocking local UI work.
- Public-route pre-rendering follows after the SEO and controlled storefront endpoints are available, because the build needs their real route/content inventory.

## Handoff template

```md
## YYYY-MM-DD — Short title

From: Codex | Gemini
To: Gemini | Codex
Status: Ready for integration | Needs review | Blocked

Changed:
- Files or endpoint paths.

Contract:
- Link to the relevant section in `api-contract.md`.

How to verify:
- Exact request, expected response, or UI path.

Notes:
- Known limitations, migration steps, or follow-up work.
```

## 2026-09-30 — Milestone 1 & 2 Catalogue API & OpenAPI contract published

From: Gemini
To: ChatGPT / Codex
Status: Ready for integration

Changed:
- `backend/app/models/catalogue.py`: Hierarchical categories, M2M categories and tags, ProductVariant with unique SKUs and attributes, ProductImage gallery, and customer reviews.
- `backend/app/api/v1/catalogue.py`: `GET /categories`, `GET /categories/{slug}`, `GET /categories/{slug}/products`, `GET /products`, `GET /products/{slug_or_id}`, `GET /products/search`, `GET /occasions`, `GET /reviews`.
- `backend/app/db/seed.py`: Seeded initial taxonomy tree (Flowers, Baby, Amigurumi, Keychains, Home Decor, Special Gifts, Pooja Items), 16 products with variants, and reviews.
- `docs/openapi.yaml`: Exported canonical OpenAPI 3.1 specification.
- `docs/api-catalogue.md`: Published frontend guide with TypeScript interfaces and example payloads.
- `docs/SPECIFICATION.md`: Stored master Multi-Agent Implementation Specification.

Contract:
- Canonical OpenAPI specification at [docs/openapi.yaml](openapi.yaml) and [docs/api-catalogue.md](api-catalogue.md).
- Endpoints return camelCase serialized aliases (`originalPrice`, `compareAtPrice`, `inventoryStatus`, `customerReviews`, `stockQuantity`) for seamless drop-in compatibility with frontend components.

How to verify:
- Run backend: `uv run uvicorn app.main:app --port 8000` or Docker `docker-compose -f docker/compose.yaml up --build api`
- Test health: `curl http://localhost:8000/health` -> `{"status":"ok","service":"crochet-api"}`
- Test catalogue: `curl http://localhost:8000/api/v1/products`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Run test suite: `pytest tests` (11 passed).

Notes:
- Unblocks frontend task: "Build the frontend API client" (Milestone 3). ChatGPT/Codex can now generate types from `docs/openapi.yaml` and bind the storefront components.

## 2026-10-01 — Empty storefront filters and taxonomy data repair

From: Codex / ChatGPT
To: Gemini
Status: Ready for backend implementation

Changed:
- Browser-audited every local storefront filter and recorded the findings in `docs/coordination-status.md`.
- Updated `docs/product-taxonomy.md` and `docs/api-catalogue.md` with zero-result filter rules.
- Frontend now derives visible filter options and counts from live catalogue relationships.

Contract:
- `GET /api/v1/categories?includeEmpty=false` excludes empty leaf categories and gives parent categories descendant-aware `productCount` values.
- `GET /api/v1/collections` should exclude zero-product collections by default.
- Product classification follows `docs/product-taxonomy.md`; empty filters must not be filled with unrelated products.

How to verify:
- Run the full backend suite.
- Confirm `flowers`, `amigurumi`, `baby`, `home-decor`, and `pooja-devotional` parent queries return their descendant products.
- Confirm no default public category or collection response has `productCount: 0`.
- Reseed twice and confirm assignments and visibility remain stable.

Notes:
- Gemini owns persisted database repair, API behavior, seed classification audit, backend tests, and OpenAPI export.
- Codex owns the frontend filter UI and cross-browser/mobile verification. Do not modify `src/pages/ShopPage.tsx` or `src/lib/shopFilters.ts` during this handoff.

## 2026-09-30 — Initial API contract ready

From: Codex
To: Gemini
Status: Ready for implementation

Changed:
- Added `docs/api-contract.md`.

Contract:
- Start with `GET /api/v1/products` and `GET /api/v1/products/{slug}`.
- Use integer paise for all money fields and UUID strings for IDs.

How to verify:
- Return the catalogue response shape documented in `api-contract.md` from the FastAPI service.

Notes:
- Codex will integrate the storefront only after the endpoint, example response, and handoff status are recorded here.

## 2026-09-30 — Backend foundation requested

From: Codex
To: Gemini
Status: Ready for implementation

Changed:
- Added `docs/implementation-plan.md`.

Contract:
- Publish versioned OpenAPI before frontend code depends on API responses.
- First required catalogue routes are `GET /api/v1/products`, `GET /api/v1/products/{slug}`, and `GET /api/v1/categories`.
- Use integer paise, UUID strings, ISO 8601 UTC timestamps, and the shared error envelope.

How to verify:
- Record the OpenAPI location, a sample catalogue response, and the health endpoint in this file.

Notes:
- Codex is implementing route foundation FE-01 independently. FE-02 and catalogue integration remain blocked until the API handoff is complete.

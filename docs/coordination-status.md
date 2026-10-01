# Coordination status

This file records the current cross-team integration gate. Update it when a handoff becomes usable or becomes blocked.

## 2026-10-01 — Controlled Homepage Composition & Storefront Sections gate

Status: Ready for integration

Frontend owner: Codex / ChatGPT  
Backend owner: Gemini

### What is ready

- **Composite Public Endpoint**: `GET /api/v1/storefront/home` returning brand metadata, active hero campaigns, and server-side resolved homepage sections (`category_grid`, `product_collection`, `promo_banner`, `review_section`, and `image_text`).
- **Compatibility Alias**: `GET /api/v1/storefront` preserved during frontend migration returning `{ brand, heroCampaigns }`.
- **Database Models & Alembic Migration**: `HomepageSection` model backed by Alembic migration `f5399f52930d_add_homepage_sections.py` with indexes on `section_type`, `display_order`, `is_enabled`, `starts_at`, `ends_at`.
- **Server-Side Resolution**: Dynamic resolution of category entities into `CategorySummary`, products matching collection slugs (`bestsellers`, category slugs, tags) into `ProductListItem`, and high-rated testimonials into `ReviewSummary`. No presentation markup is returned.
- **Admin Management API**: Endpoints under `/api/v1/admin/storefront/sections` (GET, POST, GET/:id, PUT/:id, DELETE/:id) for managing sections, ordering, visibility, and schedules.
- **Seeded Artisanal Sections**: 5 rich, curated homepage sections seeded automatically for Sulocraft.
- **Contract & Spec**: Documented in `docs/api-storefront.md` and re-exported in `docs/openapi.yaml` (61 paths).
- **Automated Tests**: 77 of 77 tests passing across all 11 test modules (9 dedicated storefront tests).

## 2026-10-01 — Database-Managed Storefront Content & Campaigns gate

Status: Ready for integration

Frontend owner: Codex / ChatGPT  
Backend owner: Gemini

### What is ready

- **Public Endpoint**: `GET /api/v1/storefront` returning public brand settings (`name`, `ownerName`, `instagramUrl`, `whatsappUrl`) and active scheduled homepage campaigns ordered by priority (max 5).
- **Database Models & Alembic Migration**: `BrandSettings` and `HomepageCampaign` models backed by Alembic migration `a85462db2fec_add_storefront_models.py`.
- **Seeded Content**: 5 rich artisanal campaigns (Brand Story, Festive Gifting, New Arrivals, Home Décor, Custom Creations) and default brand profile (`Sulocraft`, `Anupama`).
- **Admin Management API**: Endpoints under `/api/v1/admin/storefront/*` for updating brand metadata, creating/editing/scheduling campaigns, priority reordering, and deleting.
- **Contract & Spec**: Documented in `docs/api-storefront.md` and re-exported in `docs/openapi.yaml` (58 routes).
- **Automated Tests**: 73 of 73 tests passing across all 11 test modules (5 dedicated storefront tests).

## 2026-10-01 — Google & Facebook Social Authentication gate

Status: Ready for integration


Frontend owner: Codex / ChatGPT  
Backend owner: Gemini

### What is ready

- **Facebook (Meta) Authentication**: `POST /api/v1/auth/facebook` with Graph API token verification (`https://graph.facebook.com/me`), mock token support for local development, 30-day HttpOnly session cookie issuance, and automatic guest cart merging.
- **Enhanced Google Authentication**: `POST /api/v1/auth/google` with ID token verification via Google tokeninfo endpoint, audience validation, and dev fallback.
- **Unified Identity Model**: Customers signing in via Google, Facebook, or Phone OTP are automatically unified under their primary `User` record by email or identity link, preventing duplicate accounts.
- **Storefront Auth UI**: `src/components/AuthModal.tsx` upgraded with branded "Continue with Google" and "Continue with Facebook" buttons, official SVGs in `src/components/Icons.tsx`, and responsive fallback flows.
- **Frontend Client**: `src/lib/api/auth.ts` updated with `authApi.google` and `authApi.facebook` typed helper methods.
- **OpenAPI Contract**: `docs/openapi.yaml` re-exported with 54 routes.
- **Automated Tests**: 68 of 68 tests passing across all 10 test modules (12 dedicated auth & identity tests).

## 2026-10-01 — Real SMS & Email Notification Service gate

Status: Ready for integration


Frontend owner: Codex / ChatGPT  
Backend owner: Gemini

### What is ready

- **SMS Providers**: Decoupled `BaseSmsProvider` with `Fast2SmsProvider` (India +91 quick OTP and order alerts), `TwilioSmsProvider` (global standard), and `MockSmsProvider` (zero-credential testing).
- **Email Providers**: Decoupled `BaseEmailProvider` with `SmtpEmailProvider` (universal SMTP relay), `ResendEmailProvider` (developer REST API), and `MockEmailProvider` (zero-credential testing).
- **Audit Logging**: `NotificationLog` model and Alembic migration `c00f321d6289_add_notification_logs.py` recording all outbound messages with status (`SENT`, `FAILED`, `MOCK`), channel, recipient, and timestamps.
- **Asynchronous Execution**: FastAPI `BackgroundTasks` ensures instant user responses during checkout and authentication.
- **Automated Tests**: 64 of 64 tests passing across all 10 test modules (8 dedicated notification tests).

## 2026-09-30 — Alembic Database Migration & Schema Version Control gate

Status: Ready for integration

Frontend owner: Codex / ChatGPT  
Backend owner: Gemini

### What is ready

- **Alembic Configuration**: `backend/alembic.ini` and `backend/alembic/env.py` dynamically resolve `DATABASE_URL` for PostgreSQL 17 and SQLite.
- **Initial Baseline Migration**: `backend/alembic/versions/bd0b5eb6abd9_initial_schema.py` encapsulates all tables, indexes, constraints, and relationships for Milestones 1–10.
- **Automated Startup Migration**: Containers (`backend/Dockerfile` and `docker/api.Dockerfile`) run `alembic upgrade head` before booting FastAPI.
- **Safe Programmatic Execution**: `app.db.session.init_db()` invokes migrations automatically on application startup.
- **Testing**: 56 of 56 tests passing across all 9 test suites; upgrade/downgrade cycles verified.

## 2026-09-30 — Sulocraft Architecture & Cloudflare Deployment gate

Status: Ready for integration

Frontend owner: Codex / ChatGPT  
Backend owner: Gemini

### What is ready

- **Platform Rebranding**: Canonical brand name unified to **Sulocraft** (`sulocraft.com`).
- **Production VPS Foundation**:
  - `backend/Dockerfile` and `backend/docker-compose.yml` (`api`, `postgres` with persistent volume `postgres_data`, and `caddy` reverse proxy).
  - Reverse proxy config in `docker/Caddyfile` for `api.sulocraft.com` forwarding to `:8000`.
  - Database backup script in `backend/scripts/backup_db.sh` dumping PostgreSQL to private R2 bucket (`sulocraft-backups`).
  - `.env.example` template with all production/staging parameters.
- **Cloudflare R2 Asset Storage**:
  - S3-compatible storage provider in `backend/app/services/storage/` with mock/local development fallback.
  - Image upload route `POST /api/v1/admin/images/upload` returning public `https://images.sulocraft.com/products/...` CDN URLs.
- **Edge Caching & Security**:
  - Middleware enforces `Cache-Control: no-store, no-cache, must-revalidate, private` across all customer-sensitive endpoints (`/auth/*`, `/cart/*`, `/orders/*`, `/addresses/*`, `/account/*`, `/admin/*`, `/payments/*`).
  - Cross-subdomain cookie domain `.sulocraft.com` and `secure=True` configured for production.
- **Contract & Tests**:
  - `docs/openapi.yaml` re-exported with 53 routes.
  - Test suite: 56 of 56 tests passing across 9 test modules.

## 2026-09-30 — Promotions/Coupons Engine & Reviews integration gate

Status: Ready for integration

Frontend owner: Codex / ChatGPT  
Backend owner: Gemini

### What is ready

- `POST /api/v1/cart/apply-coupon` validates percentage & flat discounts, minimum order requirements, max discount caps, and expiry dates.
- `DELETE /api/v1/cart/coupon` removes active discount from cart.
- `POST /api/v1/orders` accepts `couponCode`, validating and decrementing usage, snapshotting `discount_amount` and `discount_amount_paise`.
- `POST /api/v1/products/{slug_or_id}/reviews` handles authenticated customer review submission with dynamic rating recalculation.
- `/api/v1/admin/coupons` provides full CRUD for promotional campaigns.
- `/api/v1/admin/reviews` provides moderation and deletion with automatic rating recalculation.
- Canonical `docs/openapi.yaml` re-exported (52 routes).
- Full test suite passes: 52 of 52 tests across 8 test modules.

## 2026-09-30 — Catalogue API integration gate

Status: Ready for integration

Frontend owner: Codex / ChatGPT  
Backend owner: Gemini

### What is ready

- The backend health endpoint returns HTTP 200.
- `GET /api/v1/products` returns HTTP 200 with headers and JSON.
- `docs/openapi.yaml` re-exported and validated.
- All 27 backend tests pass cleanly.

### Resolved blocking issue

- Eliminated `.distinct()` and multi-table joins on catalogue queries by using `.any()` relationship filters and correlated subqueries for variant price ordering.
- Mapped JSON columns (`metadata_json`, `attributes_json`, `personalization_json`) to `JSONB` on PostgreSQL using SQLAlchemy variants.
- Tested and confirmed working on both SQLite and PostgreSQL.

### Confirmed API Contract

1. **Entity IDs vs URL Identifiers**:
   - Primary keys are integer IDs (`id: number`) in database records and schemas.
   - Resource routing and storefront lookup URLs use human-readable slug strings (`slug: string`, e.g. `forever-crochet-rose-bouquet`). Product detail endpoint `/api/v1/products/{slug_or_id}` accepts either the slug string or the integer ID.
2. **Dual Currency Representation**:
   - Both integer INR rupees (`price: 2599`) and integer paise (`pricePaise: 259900`) are provided in every product and cart payload.
   - Standard currency is `"INR"`.
3. **Field Naming & Compatibility Aliases**:
   - All response fields serialize in camelCase (`pricePaise`, `compareAtPrice`, `originalPrice`, `inventoryStatus`, `customerReviews`, `imageUrls`, `reviewCount`, `inStock`).
   - Both `image` (primary string) and `imageUrls` (array) are populated.
   - Both `reviews` and `reviewCount` are populated.
   - Both `inventoryStatus` ("IN_STOCK") and `inStock` (boolean) are populated.
   - The OpenAPI spec at `docs/openapi.yaml` is the canonical source for codegen.

### Frontend integration result

Status: Complete

Codex added a typed catalogue client at `src/lib/api/catalogue.ts` and a shared `CatalogueProvider`. Home, shop, product, search, and wishlist screens now read the live `/api/v1/products` response. The frontend uses the backend slug for product URLs and handles loading, retry, and API failures. The production build passes, and the API confirms CORS access for `http://localhost:8080`.

## 2026-09-30 — Independent frontend task

Status: Complete

Codex completed public information routes and footer navigation while catalogue integration is blocked. This task has no backend dependency and covers Contact, Shipping, Returns, Privacy, Terms, and a not-found screen. The production build passed, and the Contact and unknown-URL paths resolve through the storefront.

## 2026-09-30 — Accessibility foundation

Status: Complete

Codex added keyboard focus visibility, reduced-motion handling, a skip-to-content link, landmark targeting, and accessible search-dialog semantics. The production build passed.

## 2026-09-30 — SEO foundation

Status: Complete

Codex added route-aware titles, descriptions, canonical URLs, and product structured data. The production build passed. The client catalogue will be replaced by API-backed product data during integration.

## 2026-09-30 — Storefront state foundations

Status: Complete

Codex added reusable loading, error, and empty-state patterns and applied the shared empty state to the cart and wishlist flows. The production build passed.

## 2026-09-30 — Mobile purchase controls

Status: Complete

Codex improved the product purchase flow for narrow screens with a persistent mobile Add to Basket control. Product quantity now reaches the cart, and Buy Now adds the selected quantity before opening the basket. The production build passes.

## 2026-09-30 — Guest cart integration

Status: Complete

Codex connected the basket drawer and cart page to Gemini's cookie-backed cart service through `src/lib/api/cart.ts` and `src/components/CartProvider.tsx`. Add, quantity update, and removal actions use backend cart line-item IDs. Production build passed, and a live guest-cart add/retrieve test confirmed the returned item ID, quantity, and INR totals.

## 2026-09-30 — Checkout and mock payment integration

Status: Complete

Codex connected checkout to the server order endpoint with inline delivery address submission. COD orders complete immediately; online methods create an intent and complete through Gemini's local mock gateway. The server cart refreshes after order completion. Production build passed.

## 2026-09-30 — Phone OTP sign-in

Status: Complete

Codex connected the header account control to Gemini's cookie-based phone OTP endpoints. The local OTP response is shown only for the documented development flow, and successful authentication refreshes the merged server cart. Production build passed.

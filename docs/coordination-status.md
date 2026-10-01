# Coordination status

This file records the current cross-team integration gate. Update it when a handoff becomes usable or becomes blocked.

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

# Cross-team handoffs

Use this file whenever frontend or backend work becomes ready for the other side. Newest handoff goes first.

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

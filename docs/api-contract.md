# Frontend–backend API contract

## Ownership

| Area | Owner | Responsibility |
| --- | --- | --- |
| `src/` | Codex | Storefront UI, responsive behaviour, browser state, API client, and integration tests |
| `backend/` | Gemini | API routes, schemas, persistence, authentication, payments, and backend tests |
| `docs/api-contract.md` | Shared | Any endpoint or data-contract change must be recorded here before implementation |

## Shared rules

- All product-facing endpoints use `/api/v1`.
- JSON uses `camelCase` field names.
- Prices are integer paise, never floating-point rupees. The frontend formats paise as INR.
- Timestamps use ISO 8601 UTC strings.
- IDs are UUID strings.
- API errors use `{ "error": { "code": "...", "message": "..." } }`.
- The API must not expose database-internal fields.
- A breaking contract change requires agreement in this file before either side implements it.

## Contract source and code generation

Gemini publishes the generated FastAPI OpenAPI document at `docs/openapi.yaml` or a documented API URL. Codex generates the TypeScript API client and types from that document; frontend code must not create a parallel backend model.

## Phase 1 endpoints

### `GET /api/v1/products`

Returns the published catalogue. Supports optional `category`, `occasion`, `customizable`, `sort`, `page`, and `pageSize` query parameters.

```json
{
  "items": [
    {
      "id": "uuid",
      "slug": "forever-crochet-rose-bouquet",
      "name": "Forever Crochet Rose Bouquet",
      "description": "...",
      "pricePaise": 259900,
      "currency": "INR",
      "category": "flowers",
      "imageUrls": ["https://..."],
      "badge": "Bestseller",
      "rating": 4.9,
      "reviewCount": 128,
      "customizable": true,
      "inStock": true
    }
  ],
  "page": 1,
  "pageSize": 24,
  "total": 1
}
```

### `GET /api/v1/products/{slug}`

Returns the complete product, including gallery images, material details, dimensions, processing time, care instructions, configurable options, and related-product slugs.

#### Product options and color selection

- The storefront must not display generic or hardcoded color swatches.
- Product option controls may be shown only when the product response includes the actual supported options/variants for that product; each option must map to a sellable variant and be available for purchase.
- Color selection remains off until Sulocraft can fulfill color-specific variants. When enabled, Gemini should expose the real color options and variant availability from the catalogue API, and Codex will render those values using the reusable product-option template.
- Do not infer customer-selectable colors from image colors, product tags, or `customizable: true`.
- Cart lines must render the selected variant/personalization returned by the API. Never invent default details such as a color or gift-wrap choice.

### `GET /api/v1/categories`

Returns collection metadata used by browse and navigation UI.

### Authentication — planned backend handoff

All authentication routes are versioned under `/api/v1/auth`.

- `POST /google`
- `POST /phone/send-otp`
- `POST /phone/verify-otp`
- `POST /logout`
- `GET /me`

Sessions use secure HttpOnly cookies. The frontend must not store session or refresh tokens in local storage.

### `POST /api/v1/carts`

Creates an anonymous cart and returns its ID. The frontend stores the cart ID locally.

### `GET /api/v1/carts/{cartId}` and `PATCH /api/v1/carts/{cartId}`

Reads or updates cart line items. Each item stores product ID, quantity, selected options, and a gift note. The server calculates all prices and totals.

## Agreed & implemented contracts

- **Catalogue**: `GET /api/v1/products`, `GET /api/v1/products/{slug_or_id}`, `GET /api/v1/categories`, `GET /api/v1/occasions`, `GET /api/v1/reviews`.
- **Cart**: `GET/POST/PATCH/DELETE /api/v1/cart` with automatic 30-day guest cart cookie and customer login merge.
- **Auth**: `POST /api/v1/auth/phone/send-otp`, `POST /api/v1/auth/phone/verify-otp`, `POST /api/v1/auth/google`, `GET /api/v1/auth/me`, `POST /api/v1/auth/logout`.
- **Orders**: `POST /api/v1/orders` (single-step checkout), `GET /api/v1/orders`, `GET /api/v1/orders/{orderNumber}`, `GET /api/v1/orders/{orderNumber}/tracking`, `POST /api/v1/orders/{orderNumber}/cancel`.
- **Payments**: `POST /api/v1/payments/intent`, `POST /api/v1/payments/verify`, `POST /api/v1/payments/webhook/{provider}` (Mock gateway for dev/testing, Razorpay for production).
- **Account & Wishlist**: `GET/PATCH /api/v1/account/profile`, `GET /api/v1/account/overview`, `GET/POST/DELETE /api/v1/wishlist`.
- **Admin**: `GET/POST/PATCH/DELETE /api/v1/admin/products`, `POST/PATCH/DELETE /api/v1/admin/variants`, `PATCH /api/v1/admin/variants/{id}/inventory`, `POST/PATCH/DELETE /api/v1/admin/categories`, `GET/PATCH /api/v1/admin/orders`, `GET /api/v1/admin/analytics`.
- **Promotions & Coupons**: `POST /api/v1/cart/apply-coupon`, `DELETE /api/v1/cart/coupon`, `GET/POST/PATCH/DELETE /api/v1/admin/coupons`.
- **Product Reviews**: `POST /api/v1/products/{slug_or_id}/reviews`, `GET/DELETE /api/v1/admin/reviews`.
- **Storage & Uploads**: `POST /api/v1/admin/images/upload` (delivers public URLs hosted on `https://images.sulocraft.com`).

---

## Sulocraft Target Production Architecture & Deployment Rules

### 1. Target Architecture & Domains

```text
Customer
   │
   ▼
Cloudflare
   │
   ├── sulocraft.com (and www.sulocraft.com)
   │      ↓
   │   Frontend: Cloudflare Pages
   │
   ├── images.sulocraft.com
   │      ↓
   │   Product Assets & Images: Cloudflare R2
   │
   └── api.sulocraft.com
          ↓
       Cloudflare proxy
          ↓
       VPS in India (Docker Compose)
          │
          ├── Caddy Reverse Proxy (:80 -> api:8000)
          ├── FastAPI Backend
          └── PostgreSQL (Persistent Docker Volume)
```

### 2. Frontend Hosting & Environment Binding (ChatGPT / Codex)
- **Hosting**: Cloudflare Pages (`https://sulocraft.com`).
- **API URL Binding**: Frontend components must NOT hardcode `localhost` or the production API URL. Instead, bind to an environment variable:
  - Vite: `VITE_API_BASE_URL` (e.g. `https://api.sulocraft.com/api/v1` or local dev `http://localhost:8000/api/v1`).
  - Next.js / React: `NEXT_PUBLIC_API_BASE_URL`.
- **Local Dev Support**: Seamlessly supports `http://localhost:3000` and `http://localhost:8080`.

### 3. Image Delivery & Performance Requirements
- **Storage**: All product photography and uploaded assets are stored in Cloudflare R2 and delivered publicly through `https://images.sulocraft.com`.
- **External URLs**: Frontend must treat image URLs as external URLs returned by the backend (`image`, `imageUrls`, `url`). Do NOT construct storage paths manually.
- **Responsive Sizing & Lazy Loading**:
  - `thumbnail`: ~300px
  - `card`: ~600px
  - `product`: ~1200px
  - `zoom`: ~1800px
  - Do not download full-resolution images for 300px product cards. Use WebP/AVIF and `loading="lazy"`.

### 4. Cross-Subdomain Cookies & CORS
- **CORS**: FastAPI explicitly permits `https://sulocraft.com`, `https://www.sulocraft.com`, and local dev ports (`3000`, `5173`, `8080`).
- **Cookies**: In production, `session_token` and `guest_cart_token` use `domain=".sulocraft.com"`, `secure=True`, `samesite="lax"`, and `httponly=True`. In local development, cookies are host-only with `secure=False`.
- **Credentials**: Frontend requests must include `credentials: 'include'`.

### 5. Cloudflare CDN Caching Boundaries
- **Dynamic Endpoints**: All customer-specific, authenticated, and transactional endpoints (`/api/v1/auth/*`, `/api/v1/cart/*`, `/api/v1/orders/*`, `/api/v1/addresses/*`, `/api/v1/account/*`, `/api/v1/admin/*`, `/api/v1/payments/*`) automatically return `Cache-Control: no-store, no-cache, must-revalidate, private` to prevent caching by Cloudflare Edge.
- **Static Assets & Catalogue**: Public GET requests (`/api/v1/products`, `/api/v1/categories`) can be cached at the edge.

# TODO

Use this file for work that is ready to start. Keep each item small enough for one agent to complete and verify.

| Status | Owner | Task | Done when |
| --- | --- | --- | --- |
| Done | Gemini | Implement the catalogue API | `GET /api/v1/products` matches the shared contract, has seeded taxonomy/products, and passed test suite |
| Done | Gemini | Implement Cart Persistence & Guest Cart | `Cart` and `CartItem` models, guest cookie management, add/update/delete endpoints, and merge logic are implemented and tested |
| Done | Gemini | Implement Authentication & Unified User Model | Phone OTP, Google auth, unified `User` model, session cookies, and auto cart merge are implemented |
| Done | Gemini | Implement Checkout & Orders Engine | Address management, Order & OrderItem models with price snapshots, order creation from cart, and tracking endpoints |
| Done | Codex | Implement Checkout & Order Tracking UI | Connect checkout address selection, order placement, order history, and tracking timeline with `/api/v1/orders` and `/api/v1/addresses`; completed in FE-07 |
| Done | Gemini | Implement Payment Abstraction & Gateway Flow | Payment intent creation, webhook handling, and payment verification for Razorpay/UPI/Mock |
| Done | Codex | Implement Payment Flow & Gateway Modal UI | Wire up checkout payment modal (Mock & Razorpay) with `/api/v1/payments/intent` and `/verify`; completed in FE-07 |
| Done | Gemini | Implement Customer Profile & Account Endpoints | Profile edit, avatar management, wishlist endpoints, and account aggregation |
| Done | Codex | Connect Customer Account & Wishlist UI | My Account now loads overview metrics, updates name/email, manages saved addresses, shows orders, and uses the persistent wishlist provider; contract in `/docs/api-account.md` |
| Done | Gemini | Implement Admin Catalog & Metrics API | Admin product/variant CRUD, inventory adjustment, order status transitions, and store analytics |
| Ready | ChatGPT / Codex | Implement Admin Dashboard & Catalog Management UI | Build admin views for product/variant CRUD, inventory adjustment, order status transitions, and store analytics using `/api/v1/admin`; contract in `/docs/api-admin.md` |
| Done | Gemini | Implement Promotions/Coupons Engine & Product Reviews API | Coupon validation, cart discount application, customer product review submission, and admin coupon/review moderation; 52 tests passing |
| Ready | ChatGPT / Codex | Implement Coupon Input & Customer Review UI | Wire up cart coupon code input, checkout coupon discount display, and product review submission form using `/api/v1/cart/apply-coupon`, `/api/v1/orders`, and `/api/v1/products/{id}/reviews`; contract in `/docs/api-promotions.md` |
| Done | Gemini | Implement Sulocraft Deployment & Cloudflare R2 Infrastructure | Docker Compose VPS stack (FastAPI, PostgreSQL persistent volume, Caddy reverse proxy), R2 asset storage, DB backup script, cache control middleware; 56 tests passing |
| Ready | ChatGPT / Codex | Configure Cloudflare Pages & Responsive R2 Image Delivery | Bind API URL via `VITE_API_BASE_URL` / `NEXT_PUBLIC_API_BASE_URL`, render external R2 image URLs with responsive sizes (`~300px`, `~600px`, `~1200px`) and lazy loading |
| Done | Codex | Build route foundation | Existing screens have clean, shareable URL routes without changing their visual design; production build and direct product URL verified |
| Done | Codex | Build the frontend API client | The storefront consumes the catalogue endpoint with loading and error states; completed in FE-02 |
| Done | Codex | Connect storefront Cart to Cart API | Replaced local in-memory cart with `/api/v1/cart` endpoints; completed in FE-05 |
| Done | Codex | Implement Auth UI & Session Handling | Connected Phone OTP modals with `/api/v1/auth` endpoints and session cookies; completed in FE-06 |
| Done | Gemini | Design the first API domain | Product catalogue routes, schemas, and database model are agreed |
| Ready | Unassigned | Review responsive behaviour | Desktop and mobile issues are listed with affected screens |
| Ready | Unassigned | Audit prototype content | Every placeholder product, image, review, promise, and link is identified |
| Ready | Unassigned | Cost and approve every SKU | Each product has dimensions, material cost, making time, and an approved retail price |
| Ready | Unassigned | Define routing needs | The project has an agreed choice for URL-based navigation |

Status values: `Ready`, `In progress`, `Review`, `Blocked`, `Done`.

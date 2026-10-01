# TODO

Use this file for work that is ready to start. Keep each item small enough for one agent to complete and verify.

| Status | Owner | Task | Done when |
| --- | --- | --- | --- |
| Done | Gemini | Finish V1 global authentication hardening | Core magic-link and admin flow works; atomic token consumption, verified social email enforcement, CSRF/origin controls, client-address throttling, removal of legacy OTP schemas/config/services, and 79 passing tests |
| Done | Gemini | Align V1 transactional email with Resend | Purpose-specific senders and required transactional events use `EmailService`; mock local delivery remains available and 87 backend tests passed |
| Ready | Owner | Configure Cloudflare and Resend email DNS | Privately verify the Gmail destination, create `hello@`, `support@`, and `orders@` routes, verify the Resend domain, and add SPF/DKIM/DMARC records per `/docs/email-architecture.md` |
| Done | Gemini | Rebuild catalogue taxonomy and controlled seed catalogue for launch | Hierarchical taxonomy, collections, admin/public APIs, controlled 16-product seed, migration, OpenAPI, validation, and 96 backend tests are complete |
| Done | Codex | Integrate launch taxonomy into existing UI | Typed category/collection clients, ordered navigation, category/collection shop filters, four-card homepage category grid, and live Docker/browser verification are complete |
| In progress | Codex | Complete controlled product gallery media | Four priority products have approved alternate views and seed records; generate and validate distinct galleries for the remaining controlled products without replacing primary images |
| Done | Codex | Replace customer OTP UI with global login | Login modal offers only real Google, real Facebook, and email magic link; checkout remains available to guests and requires delivery email plus phone |
| Done | Codex | Integrate local email and admin sign-in | Development magic-link response exposes a local-only continuation, preserves the requested return path, restores the cookie session after redirect, and displays generic invalid/expired-link guidance |
| Done | Codex + Gemini | Add V1 authentication and purchase browser regression | Guest checkout and guest cart → Google/Facebook/email login merge → checkout → payment → admin shipment → tracking pass in Docker without any phone-auth dependency; 6 dedicated regression tests passing (111 total) |
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
| In progress | Codex | Implement Admin Dashboard & Catalog Management UI | Build admin views for product/variant CRUD, inventory adjustment, order status transitions, and store analytics using `/api/v1/admin`; contract in `/docs/api-admin.md` |
| Done | Gemini | Implement database-managed storefront campaigns | Implement `GET /api/v1/storefront`, editable brand settings, and scheduled homepage campaigns per `/docs/api-storefront.md`; 73 tests passing |
| Done | Gemini | Extend storefront with controlled homepage sections | Implement `GET /api/v1/storefront/home` plus ordered/scheduled `category_grid`, `product_collection`, `promo_banner`, `review_section`, and `image_text` data per `/docs/api-storefront.md`; 77 tests passing |
| Done | Gemini | Repair broken homepage section media on dev | Update promo/story seed defaults and existing dev DB rows to `sections/gift-handcrafted-warmth.png` and `about/anupama-sharma.png`; ensure both assets are uploaded to R2 and publicly reachable, verify `/storefront/home`, and add a regression test; 112 tests passing and verified on live Docker stack |
| Done | Gemini | Map the new Downloads/sulocraft image batch into the catalogue | 11 R2 image keys mapped into catalogue/media records; six products added with unique SKUs; regression coverage added; backend and frontend suites pass |
| In progress | Codex | Verify and deploy catalogue media updates to VPS | Local Docker storefront/API and all new product images verified; next commit/push to `dev`, deploy the backend release to VPS, then check health and public image URLs |
| Done | Gemini | Implement dynamic SEO metadata and sitemap | Implement `/api/v1/seo/resolve`, entity SEO fields/defaults, private-route noindex rules, and dynamic sitemap per `/docs/api-seo.md`; 105 tests passing and OpenAPI updated |
| Done | Codex | Implement route SEO rendering | Canonical, robots, Open Graph, Twitter, breadcrumbs, organization, and product structured data render from the typed SEO contract with automated tests |
| Done | Codex + Gemini | Pre-render public storefront routes | Home, shop, category, collection, and product pages pre-rendered with complete SEO metadata and initial HTML into dist/ (48 routes); client hydrates with hydrateRoot; 35 tests passing |
| Done | Gemini | Implement Promotions/Coupons Engine & Product Reviews API | Coupon validation, cart discount application, customer product review submission, and admin coupon/review moderation; 52 tests passing |
| Done | Codex | Implement Coupon Input & Customer Review UI | Cart applies/removes backend-validated coupons, checkout submits the accepted code, and product pages submit authenticated reviews; contract in `/docs/api-promotions.md` |
| Done | Gemini | Implement Sulocraft Deployment & Cloudflare R2 Infrastructure | Docker Compose VPS stack (FastAPI, PostgreSQL persistent volume, Caddy reverse proxy), R2 asset storage, DB backup script, cache control middleware; 56 tests passing |
| Done | Codex | Add repeatable VPS release and rollback automation | Timestamped releases, shared ignored environment, stable Compose project, health-gated activation, rollback, and VPS runbook are present |
| Done | Codex | Deploy initial development API and database | Non-root automation deployed FastAPI, PostgreSQL, and Caddy; migrations and controlled seeds completed; health, five root categories, 16 products, current-release marker, and persistent volume were verified |
| Ready | Owner + Codex | Enable dev-branch backend continuous deployment | Add the five protected GitHub `development` environment secrets, authorize the deployment SSH key on the VPS, and run the workflow; tests, pre-migration backup, Compose deployment, migrations, and health validation are automated |
| Ready | Owner + Codex | Connect persistent Cloudflare development storefront | Create/connect `sulocraft-dev`, select production branch `dev`, use the documented pre-production build/deploy commands, attach `dev.sulocraft.com`, and protect it with Cloudflare Access |
| Done | Owner + Codex | Upload controlled media to Cloudflare R2 | All 31 managed category, hero, primary-product, and available gallery images match R2 and are publicly delivered from `images.sulocraft.com` with immutable caching |
| Done | Gemini | Implement Alembic Database Migrations & Version Control | Alembic configured with dynamic DB resolution, baseline migration generated, programmatic startup upgrade, and container integration; 56 tests passing |
| Done | Gemini | Implement Real SMS & Email Notification Service | Decoupled provider layer (Fast2SMS, Twilio, SMTP, Resend, Mock), background dispatch, branded templates, NotificationLog model & Alembic migration; 64 tests passing |
| Done | Gemini | Implement Google & Facebook Social Authentication | Enhanced Google token validation, implemented Facebook Graph API auth, unified customer identity, auto-merged cart, branded UI buttons; 68 tests passing |
| Done | Codex | Configure Cloudflare Pages & Responsive R2 Image Delivery | Vite API binding is environment-based; external backend image URLs render with responsive sizing hints, lazy loading, and async decoding |
| Done | Codex | Build route foundation | Existing screens have clean, shareable URL routes without changing their visual design; production build and direct product URL verified |
| Done | Codex | Build the frontend API client | The storefront consumes the catalogue endpoint with loading and error states; completed in FE-02 |
| Done | Codex | Connect storefront Cart to Cart API | Replaced local in-memory cart with `/api/v1/cart` endpoints; completed in FE-05 |
| Superseded | Codex | Implement Auth UI & Session Handling | Phone OTP was removed from the V1 architecture; replacement global login is tracked above |
| Done | Gemini | Design the first API domain | Product catalogue routes, schemas, and database model are agreed |
| Ready | Unassigned | Review responsive behaviour | Desktop and mobile issues are listed with affected screens |
| Ready | Unassigned | Audit prototype content | Every placeholder product, image, review, promise, and link is identified |
| Ready | Unassigned | Cost and approve every SKU | Each product has dimensions, material cost, making time, and an approved retail price |
| Ready | Unassigned | Define routing needs | The project has an agreed choice for URL-based navigation |

Status values: `Ready`, `In progress`, `Review`, `Blocked`, `Done`.

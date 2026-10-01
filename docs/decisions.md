# Decisions

## 2026-10-01 — Persistent development storefront

Decision: Keep `main` deployed to the production `sulocraft` Worker and `sulocraft.com`. Deploy the `dev` branch to the separate `sulocraft-dev` Worker and `dev.sulocraft.com` using Wrangler environment `dev` and Vite mode `preprod`.

Impact: Development pushes can update the shared full storefront without changing the public Coming Soon site. The development frontend uses `https://api-dev.sulocraft.com/api/v1` and remains protected with Cloudflare Access during pre-production.

Record decisions that affect more than one file, task, or future agent. Newest entries go first.

## 2026-10-01 — Keep the founder story as static editorial content

Decision: The verified Sulocraft origin story and About-page prose live in frontend source for V1. Products, taxonomy, prices, availability, campaigns, homepage sections, contact channels, and other operational content remain backend-managed.

Reason: The founder story is stable brand history, benefits from immediate indexable rendering, and does not need an admin workflow. Static content must still be factual; fictional founders, team members, business metrics, dates, sourcing claims, and customer counts are prohibited.

Impact: Anupama Sharma's account of learning crochet from her grandmother and naming Sulocraft after her mother, Sulochana, is the canonical About-page narrative. Future edits require normal content review and deployment.

## 2026-10-01 — Product categories separated from gift collections

Decision: Categories describe what a product is; collections describe gift intent, occasion, campaign, or merchandising. Tags describe flexible discovery attributes. Products remain single records and can join multiple classifications while keeping one primary leaf category.

Reason: Most Sulocraft products can be gifts. Treating gifts as product categories creates duplicate products, confusing navigation, and a taxonomy that cannot grow cleanly.

Impact: The disposable development catalogue may be reset. Gemini implements [product-taxonomy.md](product-taxonomy.md); Codex later consumes the dynamic APIs without changing the existing visual design.

## 2026-10-01 — Cloudflare incoming email and Resend transactional email

Decision: Use Cloudflare Email Routing for incoming `hello@`, `support@`, and `orders@sulocraft.com` mail forwarded to the owner's private Gmail, and use Resend behind the backend `EmailService` for all automated V1 messages. Default automated sender is `Sulocraft <orders@sulocraft.com>`.

Reason: This keeps launch costs and mailbox administration low while preserving a professional public domain and a replaceable transactional provider boundary.

Impact: The private Gmail address remains outside the repository and customer interface. Cloudflare DNS carries routing plus Resend SPF/DKIM/DMARC records. Backend work follows [email-architecture.md](email-architecture.md).

## 2026-10-01 — SMS & Email notification service architecture

Decision: Implement a decoupled notification provider layer supporting both SMS (Fast2SMS for India mobile OTPs and alerts, Twilio for international, Mock for testing) and Email (SMTP relay, Resend API, Mock for testing) with asynchronous background dispatch via FastAPI `BackgroundTasks` and transactional audit logging in `notification_logs`.

Reason: External SMS and Email gateways introduce network latency (200ms–2000ms) and potential rate limits or provider downtime. Decoupling notification dispatch via background tasks ensures checkout and sign-in requests complete in milliseconds without blocking. Storing audit logs provides traceability for customer delivery inquiries and debugging bounced messages.

Impact: Created `backend/app/services/notification/`, added `NotificationLog` model with Alembic migration `c00f321d6289_add_notification_logs.py`, and wired notifications into `/auth/phone/send-otp`, `/orders`, `/payments/verify`, and `/admin/orders/{id}/status`.

## 2026-09-30 — Alembic database migration & schema version control

Decision: Use Alembic as the canonical database migration tool for SQLAlchemy. All future schema modifications must be versioned in `backend/alembic/versions/`. Container startup runs `alembic upgrade head` automatically.

Reason: `Base.metadata.create_all()` cannot alter existing tables in production PostgreSQL without data loss. Alembic allows incremental, safe, and reversible schema evolution in production while maintaining SQLite compatibility in development.

Impact: Initial baseline migration `bd0b5eb6abd9_initial_schema.py` generated for Milestones 1–10. Production `backend/Dockerfile` and `docker/api.Dockerfile` execute `alembic upgrade head` before serving traffic.
## 2026-09-30 — Sulocraft brand confirmation & SEO domain alignment

Decision: The official website and brand name is confirmed as **Sulocraft** (`sulocraft.com`). All backend models, default brand values, seed records, health endpoints, schemas, and storefront copywriting are aligned to Sulocraft.

Reason: Replaces temporary placeholder branding ("Crochet Bloom") with the canonical direct-to-consumer brand name.

Impact: SEO title format is `${title} | Sulocraft`, production domain is `https://sulocraft.com`, API is `https://api.sulocraft.com`, and image CDN is `https://images.sulocraft.com`.

## 2026-09-30 — Cloudflare Pages, Cloudflare R2 & Single-VPS Docker Compose architecture

Decision: Deploy the application across a lightweight, cost-optimized Cloudflare + VPS stack:
1. **Frontend**: Cloudflare Pages (`https://sulocraft.com` and `https://www.sulocraft.com`).
2. **Product Images & Backups**: Cloudflare R2 (`https://images.sulocraft.com` via public bucket `sulocraft-products`; private bucket `sulocraft-backups` for compressed database dumps).
3. **Backend & Database**: Single VPS in India running Docker Compose (`api` FastAPI, `postgres` PostgreSQL 17 with named persistent volume `postgres_data`, and `caddy` reverse proxy handling `api.sulocraft.com`).
4. **Cloudflare Proxy**: Proxies `api.sulocraft.com` with strict `Cache-Control: no-store, no-cache, private` enforcement on customer/authenticated API endpoints.
5. **Cross-Subdomain Authentication**: Cookies configured with `domain=".sulocraft.com"`, `secure=True`, `samesite="lax"`, and `httponly=True` in production, retaining `domain=None` and `secure=False` for zero-credential local development (`localhost:3000` / `localhost:8080`).

Reason: Minimizes operational overhead, avoids expensive managed database/k8s infrastructure initially, delivers blazing fast static/image assets via global CDN edge, and guarantees zero data loss on container recreation.

Impact: Created `backend/Dockerfile`, `backend/docker-compose.yml`, `docker/Caddyfile`, `backend/scripts/backup_db.sh`, `backend/.env.example`, and `backend/app/services/storage/` (Cloudflare R2 + mock local fallback).

## 2026-09-30 — Role-Based Access Control (`role == "ADMIN"`)

Decision: Add `role` column (`"CUSTOMER"`, `"ADMIN"`) to `User` and guard all `/api/v1/admin/*` routes with `get_current_admin`. Non-admin requests receive HTTP 403 Forbidden.

Reason: Secure separation between customer storefront actions and store management, inventory adjustments, and order lifecycle transitions.

Impact: Staging/development admin seeded (`phone: "9999900000"`), and admin operations are isolated under `/api/v1/admin`.

## 2026-09-30 — Payment provider abstraction (Mock + Razorpay)

Decision: Implement a decoupled `BasePaymentProvider` layer with a zero-credential `MockPaymentProvider` for development and automated testing, and `RazorpayPaymentProvider` for production payments.

Reason: Allows complete checkout and payment verification flows to run locally and pass CI tests without external gateway credentials.

Impact: Checkout flow in FE-07 and backend tests verify payment completion and order confirmation cleanly.

## 2026-09-30 — Dual currency representation (Rupees and Paise)

Decision: Provide both integer INR rupees (`price`) and integer paise (`pricePaise`) across all catalogue, cart, order, payment, and analytics responses.

Reason: Prevents floating-point rounding errors in financial transactions while maintaining compatibility with UI display components.

Impact: All schemas serialize camelCase aliases with both units (`subtotal` and `subtotalPaise`, `totalAmount` and `totalAmountPaise`).

## 2026-09-30 — Split frontend and backend ownership

Decision: Codex owns the frontend and Gemini owns the backend. Shared API work is defined in `docs/api-contract.md` before either side implements it.

Reason: A documented boundary lets both streams progress without conflicting assumptions about fields, prices, routes, or ownership.

Impact: The frontend will retain sample data until the catalogue API is handed off, then integrate against the approved versioned contract.

## 2026-09-28 — Premium pricing baseline

Decision: Treat the initial prototype prices as placeholders and use a cost-and-labour-based premium pricing model for the real catalogue.

Reason: Comparable Etsy finished handmade goods span a much higher range once scale, materials, personalisation, and gift presentation are comparable. Marketplace sale pricing is not a sound floor price for quality handmade work.

Impact: The prototype catalogue now uses the premium target prices recorded in `docs/pricing.md`. Confirm each SKU's dimensions, materials, making time, and fulfilment costs before launch.

## 2026-09-28 — Python FastAPI backend and Docker Compose foundation

Decision: Use FastAPI for the backend and Docker Compose to run the React frontend, FastAPI service, and PostgreSQL database in isolated containers.

Reason: Python is a suitable, approachable choice for this project and FastAPI offers typed endpoints, validation, and built-in API documentation. Containers allow the stack to run without installing project dependencies on the host.

Impact: Backend features will be added under `backend/`; the frontend will consume versioned API endpoints rather than directly accessing persistent services.

## 2026-09-28 — Documentation workspace created

The project will keep shared planning and working context in `docs/`. The root README is the entry point for people and agents joining the project.

## 2026-10-01 — Full-width storefront discovery layout

Decision: Storefront discovery surfaces use the complete viewport width with fluid responsive gutters. Hero artwork and section backgrounds are full bleed; category grids, product collections, promotions, reviews, the header, and the footer use the shared `.storefront-shell` layout. Readable copy, forms, checkout tasks, and dialogs remain locally constrained.

Reason: The catalogue should feel visually rich and make useful use of desktop space while retaining comfortable mobile gutters and readable text lengths.

Impact: The previous global `max-w-7xl` storefront constraint is removed. Wide product grids can show five cards, and new storefront components must use `.storefront-shell` rather than adding a centered global maximum width.

## Template

```md
## YYYY-MM-DD — Short decision title

Decision: What was chosen.

Reason: Why it was chosen.

Impact: What changes or follow-up work this creates.
```

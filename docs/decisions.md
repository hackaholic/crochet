# Decisions

Record decisions that affect more than one file, task, or future agent. Newest entries go first.

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

## Template

```md
## YYYY-MM-DD — Short decision title

Decision: What was chosen.

Reason: Why it was chosen.

Impact: What changes or follow-up work this creates.
```

# Architecture

## Target architecture

The project has three isolated services: a React storefront, a Python FastAPI service, and PostgreSQL. Docker Compose starts all three together. This keeps development and testing inside containers and leaves the host free of project dependencies.

```text
Browser → React/Vite frontend → FastAPI → PostgreSQL
```

The frontend owns presentation and transient interface state. The API owns validated business data and the database owns persistent data. Payment providers, email, and shipping services will be called by the API when those integrations are chosen. The container exposes the storefront on host port 8080, while Vite continues to listen on port 5173 inside its container.

## Email boundary

Incoming business email uses Cloudflare Email Routing to forward `hello@`, `support@`, and `orders@sulocraft.com` to the owner's private Gmail destination. Outgoing automated email uses the backend `EmailService` with Resend. Cloudflare forwarding is not a sending mailbox, and personal Gmail is never an application sender. See [email-architecture.md](email-architecture.md).

## Current application

The frontend is a client-side React 19 storefront built with TypeScript, Vite 8, and Tailwind CSS 4. The Python API currently exposes only a health endpoint; it does not yet power the interface.

`src/main.tsx` mounts `App.tsx`. `App.tsx` holds the active page, selected product, cart, wishlist, cart drawer, and search-overlay state. It passes event handlers down to page and shared components.

## Source layout

| Location | Responsibility |
| --- | --- |
| `src/App.tsx` | App-level state and page switching |
| `src/pages/` | Home, shop, product, cart, wishlist, checkout, and about views |
| `src/components/` | Shared header, footer, cards, drawers, overlay, and icons |
| `src/data/products.ts` | Sample product, category, occasion, and review data |
| `src/index.css` | Tailwind v4 import, Google Font import, theme tokens, and global CSS |
| `vite.config.ts` | Vite, React, Tailwind, and path alias configuration |
| `backend/app/main.py` | FastAPI application and health endpoint |
| `backend/pyproject.toml` | Python dependency and tool configuration |
| `docker/compose.yaml` | Frontend, API, and PostgreSQL container composition |
| `docker/*.Dockerfile` | Container images for frontend and API |

## API boundary

The API should expose versioned endpoints under `/api/v1`. Future domains are products, collections, carts, customers, orders, shipping quotes, and checkout. Keep database models, request/response schemas, and route modules separate as the service grows. Frontend code must not connect directly to PostgreSQL or payment providers.

## State and navigation

Navigation currently uses a `page` state value in `App.tsx`, rather than URL routes. Cart and wishlist data live in React state, so they disappear on refresh. The selected product is also in memory only.

## External resources

Product images load from Unsplash, reviewer avatars load from pravatar.cc, and fonts load from Google Fonts. The site needs network access to display them.

## Known implementation gaps

- No persistent data, authentication, order storage, inventory, or payment integration.
- Checkout shows a confirmation locally; it does not create an order or submit payment.
- Newsletter signup only changes local interface state.
- Product personalisation, selected colour, and quantity are not captured in cart items.
- There are no automated tests, lint checks, or application routes.

## Direction for future work

Keep reusable UI in `src/components`, page composition in `src/pages`, and domain data behind a dedicated data or service layer. Introduce routing and persistence together when the product requirements are agreed.

# Sulocraft

Sulocraft is a handmade-crochet storefront built with React, TypeScript, Vite, and Tailwind CSS.

Frontend deployment instructions are in [docs/cloudflare-deployment.md](docs/cloudflare-deployment.md). VPS backend deployment, rollback, and R2 media sync are documented in [docs/vps-deployment.md](docs/vps-deployment.md).

## Start here

- Read [the project plan](docs/plan.md) for the current direction.
- Choose work from [the task list](docs/TODO.md).
- Check [pending items](docs/pending.md) before making assumptions.
- Use [the pricing strategy](docs/pricing.md) before setting or changing product prices.
- Use [the API contract](docs/api-contract.md) and [handoffs](docs/handoffs.md) to coordinate frontend and backend work.
- Check [coordination status](docs/coordination-status.md) before beginning cross-team API work.
- Follow [the collaboration guide](docs/collaboration.md) when working with other agents.

## Run locally

This project uses Node.js 22 and pnpm 10.34.3. Install dependencies with `pnpm install`, then start the development server with `pnpm dev`.

Available commands:

- `pnpm dev` — start the local development server
- `pnpm build` — create a production build
- `pnpm preview` — preview a production build
- `pnpm format` — format the project with oxfmt

## Project map

```text
src/
  components/   Shared interface components
  data/         Product catalogue and display content
  pages/        Page-level storefront views
  App.tsx       Application state and page switching
  index.css     Tailwind import, fonts, and global styles
docs/           Shared project documentation
```

## Current status

The interface is a polished prototype with local cart and wishlist state. Product content and images are sample data, and checkout, email signup, and payment flows are visual simulations only. See [architecture](docs/architecture.md) and [the plan](docs/plan.md) for detail.

## Docker environment

The container setup runs the storefront, a Python FastAPI service, and PostgreSQL without installing project dependencies on the host.

```bash
docker-compose -f docker/compose.yaml up --build
```

The storefront will be available at `http://localhost:8080`. The API health endpoint is `http://localhost:8000/health`, and its interactive documentation is at `http://localhost:8000/docs`.

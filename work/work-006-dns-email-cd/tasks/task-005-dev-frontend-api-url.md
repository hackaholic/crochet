# Task 6.5 — Dev storefront API base URL

**Owner:** Codex

**Status:** In Progress

## Objective

Ensure the deployed `dev.sulocraft.com` frontend sends catalogue requests to the dev API.

## Finding

The frontend shell loads, but its catalogue request goes to `dev.sulocraft.com/api/v1/products` and receives the Pages HTML fallback. The same endpoint on `api-dev.sulocraft.com` returns catalogue JSON with the correct CORS origin. The local root `.env.preprod` contains only public `VITE_` settings but was ignored by Git, so Cloudflare's build could not embed the dev API URL.

## Work

- [x] Deploy current backend source into `/opt/sulocraft` and restart the existing Compose project using the saved preproduction environment.
- [ ] Track the public-only `.env.preprod` settings so Cloudflare can build the dev API URL into its bundle.
- [ ] Run the frontend build locally and verify the bundle references `api-dev.sulocraft.com`.
- [ ] Push the verified change to `dev`; confirm the live page renders catalogue products.

## Acceptance

- The browser requests products from `api-dev.sulocraft.com` rather than the Pages host.
- The dev storefront renders catalogue products without the unavailable state.
- No backend credentials are included in the frontend env file or Git history.

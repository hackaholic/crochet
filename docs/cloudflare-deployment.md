# Sulocraft deployment runbook

This guide deploys the public frontend through Cloudflare Workers Static Assets. It does not change the agreed FastAPI, PostgreSQL, Docker Compose, R2, or VPS architecture.

## 1. Before creating the Cloudflare application

1. Push the committed frontend and backend work to `main` on GitHub.
2. Confirm the GitHub repository is connected to the Cloudflare account.
3. Keep the frontend and backend domains separate:

   - `sulocraft.com` — Cloudflare static frontend.
   - `api.sulocraft.com` — Cloudflare proxy to the India VPS FastAPI service.
   - `images.sulocraft.com` — public Cloudflare R2 image delivery.

## 2. Create the frontend deployment

Cloudflare’s current Git-connected interface uses **Workers Builds** for static assets.

1. Go to **Workers & Pages** → **Create application** → connect the `hackaholic/crochet` repository.
2. Enter these settings:

   | Field | Value |
   | --- | --- |
   | Project name | `sulocraft` |
   | Production branch | `main` |
   | Build command | `pnpm build` |
   | Deploy command | `npx wrangler deploy` |
   | Preview command | `npx wrangler preview` |

3. Enable Preview builds.
4. The committed `.env.production` file provides `VITE_LAUNCH_MODE=coming-soon` automatically. No dashboard variable is needed for the first launch.
5. Deploy. Cloudflare builds the Vite application and uploads `dist` through the project’s `wrangler.jsonc` configuration.

The Coming Soon mode makes no API calls, so it is safe to publish before the VPS exists.

## 3. Create the persistent development storefront

Use a separate Worker for the shared development site. It must never deploy over the production Worker.

1. Create or select the `sulocraft-dev` Worker and connect the same `hackaholic/crochet` repository.
2. Configure its Workers Build once:

   | Field | Value |
   | --- | --- |
   | Production branch | `dev` |
   | Build command | `pnpm build` |
   | Deploy command | `npx wrangler deploy --env dev` |
   | Preview command | `npx wrangler preview --env dev` |
   | Root directory | `/` |

3. In **Settings → Build → Branch control**, confirm the production branch is `dev`.
4. In **Settings → Domains & Routes**, add the custom domain `dev.sulocraft.com` to `sulocraft-dev`.
5. Protect `dev.sulocraft.com` with Cloudflare Access until launch testing is complete.

The tracked root `.env.preprod` makes this a full-storefront build and points it to `https://api-dev.sulocraft.com/api/v1`. It contains public Vite build settings only, so no Cloudflare dashboard variable is required and no variable needs to be edited between deployments. Never add credentials or secrets to this file.

Cloudflare Workers Builds supplies `WORKERS_CI_BRANCH` automatically. The repository build script maps `dev` to Vite's `preprod` mode and every other branch to `production`, so the same `pnpm build` command safely selects the correct committed environment file. `pnpm build:dev` and `pnpm build:production` remain available for explicit local verification.

The `wrangler.jsonc` `dev` environment publishes a separately named Worker, so `npx wrangler deploy --env dev` cannot overwrite the production `sulocraft` Worker.

The development frontend requires the VPS staging API at `api-dev.sulocraft.com`. Until that API is deployed and reachable, catalogue and account features that need FastAPI will show their normal unavailable/error states.

## 4. Connect the production domain

After the Worker deployment succeeds:

1. Open the Worker’s **Settings** → **Domains & Routes**.
2. Add the custom domain `sulocraft.com`.
3. Add `www.sulocraft.com` and redirect it to `https://sulocraft.com`.
4. Keep the domain DNS zone on Cloudflare so SSL certificates and routing are managed there.

## 5. Launch the full storefront

Complete these backend tasks before switching away from Coming Soon:

1. Provision an India VPS.
2. Run the FastAPI, PostgreSQL, and reverse-proxy services using Docker Compose.
3. Configure the reverse proxy to forward `api.sulocraft.com` to FastAPI.
4. Add `api.sulocraft.com` to Cloudflare and proxy it to the VPS.
5. Configure FastAPI CORS to allow `https://sulocraft.com` and `https://www.sulocraft.com` with credentials.
6. Configure R2 public delivery at `images.sulocraft.com`. The backend must return complete image URLs; the frontend must not construct R2 paths.
7. Replace the contents of the tracked `.env.production` file with:

   | Variable | Value |
   | --- | --- |
   | `VITE_LAUNCH_MODE` | `full` |
   | `VITE_API_BASE_URL` | `https://api.sulocraft.com/api/v1` |

8. Redeploy `main` and verify browsing, cart, authentication, checkout, and payment against the production API.

## 6. Roll back safely

If the full storefront has a production issue, set `VITE_LAUNCH_MODE=coming-soon` and trigger a new deployment. This restores the backend-free landing page while the issue is fixed.

## 7. Local verification

Before any frontend deployment, run:

```bash
docker-compose -f docker/compose.yaml run --rm --no-deps frontend pnpm test
docker-compose -f docker/compose.yaml run --rm --no-deps -e VITE_LAUNCH_MODE=coming-soon frontend pnpm build
pnpm build:dev
```

## Root sitemap and indexing policy

The same build exports `/sitemap.xml`, optional `/sitemap-N.xml` chunks, `/robots.txt` and Workers `_headers`. URLs come from the backend public route inventory and must have a matching rendered page. XML is split at configured URL/byte limits; static-page generated dates are omitted rather than presented as modification dates. Catalogue edits require a new successful build to refresh these artifacts.

Tracked `.env.preprod` and the current coming-soon `.env.production` explicitly set `SEO_INDEXING_ENABLED=false`. These builds publish an empty sitemap, allow crawling so noindex can be read, and attach `X-Robots-Tag: noindex, nofollow` to assets. Access control remains separate.

For an accepted production launch, set `SEO_INDEXING_ENABLED=true` and `SEO_PUBLIC_ORIGIN` to the approved HTTPS storefront origin. Backend canonical configuration must match. Missing production indexing configuration, an invalid origin, an inventory mismatch or an unrendered route fails the build. No dashboard edits or code fork are required. Optional public build settings: `SEO_SITEMAP_MAX_URLS` (default50000), `SEO_SITEMAP_MAX_BYTES` (default52428800), `SEO_RESOURCE_CACHE_SECONDS` (default300). Nonproduction cannot enable indexing. Local Vite exposes the same non-indexing root resources and HTTP header.

## Canonical routing and lifecycle

The build writes public `routing-policy.json` and embeds the same policy for initial/runtime metadata. Full builds require `SEO_PUBLIC_ORIGIN` and a public API (`SEO_EDGE_API_BASE_URL`, falling back to `VITE_API_BASE_URL`); `SEO_API_BASE_URL` can independently address the internal build API. Do not place credentials in any public routing setting. Production routing requires HTTPS.

Worker HTML requests consult `/seo/resolve` for current301/404/410 decisions before serving assets; resolver/target failure returns noindex503. Upstream redirects are handled manually and rejected. Case/slash/legacy redirects remain same-site and validated; query views use noindex CSR to avoid stale hydration. Current unsupported page>1 is404, not page1 canonicalization. HTML lifecycle checks need an available API; static media/resource files are served directly.

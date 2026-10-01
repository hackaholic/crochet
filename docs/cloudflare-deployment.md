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

The committed `.env.preprod` makes this a full-storefront build and points it to `https://api-dev.sulocraft.com/api/v1`. These are public Vite build settings, so no Cloudflare dashboard variable is required and no variable needs to be edited between deployments. Never add credentials or secrets to this file.

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

# Sulocraft VPS deployment and operations

This runbook covers the pre-production backend host. The frontend remains on Cloudflare, product media remains in R2, and the VPS runs FastAPI, PostgreSQL, and Caddy through Docker Compose.

## Inspected host

Inspection date: 2026-10-01

| Item | Observed value |
| --- | --- |
| SSH target | `root@201.18.212.183` |
| Hostname | `srv2025896` |
| Operating system | Ubuntu 26.04.1 LTS |
| Compute | 1 vCPU, 3.8 GiB RAM |
| Disk | 48 GiB root filesystem, approximately 46 GiB available |
| Docker | 29.8.2, enabled and active |
| Docker Compose | v5.5.1 |
| Existing workloads | None at inspection time |
| Exposed services | SSH on port 22 only |
| Time | UTC, synchronized |
| Swap | None |
| Firewall | UFW inactive |

The host is suitable for initial low-traffic pre-production. One CPU is the first expected constraint, so build infrequently and monitor load. Add approximately 2 GiB swap before sustained use.

Current development release: `initial-dev-20261001`. FastAPI, PostgreSQL, and Caddy are running as the stable Compose project `sulocraft`; PostgreSQL data is stored in `sulocraft_postgres_data`.

## Security work before public traffic

1. Apply pending Ubuntu security and kernel updates.
2. Create a named sudo deployment user with an SSH key.
3. Verify a second SSH session using that account.
4. Enable UFW for ports 22, 80, and 443 only.
5. Disable SSH password authentication and direct root login only after the named account works.
6. Install login-rate protection and enable unattended security updates.
7. Keep PostgreSQL private inside Compose; never publish port 5432.

Do not automate steps 3–5 as one blind operation. Losing the verified SSH path can lock the owner out of the VPS.

## Deployment files

- Production Compose stack: `backend/docker-compose.yml`
- Reverse proxy: `docker/Caddyfile`
- Local deployment automation: `backend/scripts/deploy_vps.sh`
- Rollback automation: `backend/scripts/rollback_vps.sh`
- Safe environment template: `backend/.env.preprod.example`

The deployment script uploads a timestamped release to `/opt/sulocraft/releases`, stores the secret environment at `/opt/sulocraft/shared/.env`, uses the stable Compose project name `sulocraft`, and updates `/opt/sulocraft/current` only after the API health check passes. The named PostgreSQL volume therefore survives application releases.

## First pre-production deployment

1. Copy `backend/.env.preprod.example` to `backend/.env.preprod`.
2. Replace every required placeholder locally. The resulting file is ignored by Git.
3. Put `dev.sulocraft.com` and `api-dev.sulocraft.com` behind Cloudflare Access while `APP_ENV=staging` permits mock checkout testing.
4. Point `api-dev.sulocraft.com` to the VPS through Cloudflare. The staging environment sets `API_DOMAIN=api-dev.sulocraft.com`; Caddy obtains and renews the origin certificate using persistent `caddy_data` and `caddy_config` volumes.
5. After direct-origin HTTPS succeeds, use Cloudflare SSL/TLS mode **Full (strict)** for the proxied hostname.
5. Run:

   ```bash
   SSH_IDENTITY_FILE="$HOME/.ssh/sulocraft_github_actions" \
   SSH_KNOWN_HOSTS_FILE="$HOME/.ssh/sulocraft_vps_known_hosts" \
   DEPLOY_ENV_FILE=backend/.env.preprod \
   backend/scripts/deploy_vps.sh
   ```

6. Verify `/health`, API documentation policy, CORS, secure cookies, database migrations, authentication, basket, checkout, and admin access.

Rollback uses an existing release directory and preserves the database volume:

```bash
backend/scripts/rollback_vps.sh 20261001T120000Z
```

Schema rollback is deliberately not automatic. Application rollback must remain compatible with the migrated database or use a reviewed database restore.

Every deployment after the first creates a compressed PostgreSQL snapshot in `/opt/sulocraft/backups` before replacing the environment or running migrations. The database itself remains in the stable Compose volume `sulocraft_postgres_data`; releases do not copy or recreate live data.

## Automatic deployment from the dev branch

The workflow `.github/workflows/deploy-dev-backend.yml` runs on backend-related pushes to `dev` and can also be started manually. It:

1. installs the locked Python dependencies;
2. runs the complete backend test suite;
3. writes the pre-production environment from a protected GitHub secret;
4. uploads a timestamped/commit-addressed release over SSH;
5. backs up the currently running PostgreSQL database;
6. builds FastAPI, starts PostgreSQL/Caddy, applies Alembic migrations, and waits for `/health`;
7. marks the release current only after health validation succeeds.

Create a GitHub environment named `development` and add these environment secrets:

| Secret | Purpose |
| --- | --- |
| `VPS_HOST` | `201.18.212.183` |
| `VPS_USER` | Dedicated deployment account; use `root` only temporarily during initial pre-production setup |
| `VPS_SSH_PRIVATE_KEY` | Private half of a deployment-only SSH key |
| `VPS_KNOWN_HOSTS` | Pinned SSH host-key line for the VPS; do not replace this with disabled host checking |
| `PREPROD_ENV_FILE` | Complete contents of the ignored `backend/.env.preprod` file |

Protect the `development` GitHub environment so only the `dev` branch can use its secrets. The workflow does not contain credentials and must never print the environment file.

## Upload local media to R2

Export the scoped R2 values from an ignored file or shell session, then preview the sync:

```bash
set -a
source backend/.env.preprod
set +a
backend/.venv/bin/python backend/scripts/upload_r2_media.py
```

Apply and verify public delivery:

```bash
backend/.venv/bin/python backend/scripts/upload_r2_media.py --apply --verify-public
```

The object key is the path relative to `public/images`; for example, `public/images/products/heart-bear/primary.png` becomes `products/heart-bear/primary.png`. The uploader never writes database URLs and never deletes remote objects.

Install the backend dependencies once before running the local uploader (`cd backend && uv sync`), because `boto3` is the S3-compatible R2 client.

## Required credentials

Provide these through `backend/.env.preprod`, not chat or committed files:

- scoped R2 access key ID with object read/write for `sulocraft-products`;
- scoped R2 secret access key;
- a long random PostgreSQL password;
- Resend API key after domain verification;
- Google client ID/secret and Facebook app ID/secret when social login is enabled;
- Razorpay keys and webhook secret only when real payments replace mock mode.

The R2 account ID and endpoint are already known. Do not use a Cloudflare Global API Key.

## Pre-production credential rotation checklist

Before production launch, rotate every credential used during setup:

- R2 access key and secret;
- PostgreSQL password;
- Resend API key;
- Google and Facebook secrets;
- Razorpay key secret and webhook secret;
- any temporary SSH key or root password shared for setup.

After rotation, update the ignored deployment environment, redeploy, confirm health, and revoke the old credential at its provider.

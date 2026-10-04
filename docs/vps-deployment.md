# Sulocraft VPS deployment and operations

This runbook covers the pre-production backend host. The frontend remains on Cloudflare, product media remains in R2, and the VPS runs FastAPI, PostgreSQL, and Caddy through Docker Compose.

## Inspected host

Inspection date: 2026-10-04

| Item | Observed value |
| --- | --- |
| SSH target | `root@201.18.212.183` |
| Hostname | `srv2025896` |
| Operating system | Ubuntu 26.04.1 LTS |
| Compute | 1 vCPU, 3.8 GiB RAM |
| Disk | 48 GiB root filesystem, approximately 46 GiB available |
| Docker | 29.8.2, enabled and active |
| Docker Compose | v5.5.1 |
| Existing workloads | Isolated `sulocraft-preprod` API and PostgreSQL, plus the existing Caddy proxy |
| Exposed services | SSH, HTTP, and HTTPS |
| Time | UTC, synchronized |
| Swap | None |
| Firewall | UFW inactive |

The host is suitable for initial low-traffic pre-production. One CPU is the first expected constraint, so build infrequently and monitor load. Add approximately 2 GiB swap before sustained use.

The PREPROD API and database now run as `sulocraft-preprod`. The original `sulocraft_postgres_data` volume is retained as the pre-cutover recovery copy; PREPROD uses its own `sulocraft-preprod_postgres_data` volume. Caddy remains on the existing proxy service and reaches the isolated API through the shared gateway network.

## Security work before public traffic

1. Apply pending Ubuntu security and kernel updates.
2. Create a named sudo deployment user with an SSH key.
3. Verify a second SSH session using that account.
4. Enable UFW for ports 22, 80, and 443 only.
5. Disable SSH password authentication and direct root login only after the named account works.
6. Install login-rate protection and enable unattended security updates.
7. Keep PostgreSQL private inside Compose; never publish port 5432.

Do not automate steps 3–5 as one blind operation. Losing the verified SSH path can lock the owner out of the VPS.

## Deployment command and configuration

- Operator entry point: `./deploy_vps.sh --env preprod` or `./deploy_vps.sh --env prod`
- YAML template: `deploy/vps-config.example.yaml`
- Local YAML settings: `.deploy/vps-config.yaml` (ignored by Git)
- Isolated API/database Compose file: `backend/docker-compose.yml`
- Internal transfer/activation helper: `scripts/deploy_vps_remote.sh` (the operator does not run it directly)

The root command requires an explicit `--env` and reads host, deployment root, URLs, runtime-secret root, encrypted secret group, and gateway settings from YAML. It runs the focused release/isolation/secret checks, validates Compose, builds and checksums the API image locally, then rsyncs the immutable release to `/opt/sulocraft/releases`. The VPS verifies the archive, bootstraps SOPS secrets into `/run/sulocraft/<env>`, backs up the active database, and updates `/opt/sulocraft/current` only after API and proxy health checks pass. It does not push to GitHub or build the API image on the VPS.

The first PREPROD rollout restored the existing database into the isolated `sulocraft-preprod` volume. Later deployments back up and reuse that target-scoped volume. The old `sulocraft_postgres_data` volume remains available for recovery.

Local PREPROD deployment and its no-mutation preflight:

```bash
./deploy_vps.sh --env preprod --preflight
./deploy_vps.sh --env preprod
```

Do not use `--env prod` until its distinct encrypted secret groups exist and exact-image promotion is implemented and accepted. The current command fails closed for PROD.

Each rollout creates a compressed PostgreSQL snapshot in `/opt/sulocraft/backups` before stopping the active target. Failed health checks restart the previous stack and leave `/opt/sulocraft/current` unchanged.

## Automatic deployment from the dev branch

The GitHub workflow `.github/workflows/deploy-dev-backend.yml` is the separate CI path and uses the repository Actions secrets below. The local `./deploy_vps.sh` command uses the SSH agent or identity configured in `.deploy/vps-config.yaml`; it does not read GitHub secrets. Work 006 still owns aligning the CI workflow with the stable deployment interface. The configured Actions secrets are:

### GitHub Actions Secrets

Configure these under **Settings $\rightarrow$ Secrets and variables $\rightarrow$ Actions** (see [GitHub Actions SSH Setup Guide](github-actions-ssh-setup.md) for full instructions):

| Secret | Purpose |
| --- | --- |
| `VPS_HOST` | `201.18.212.183` |
| `VPS_USER` | Dedicated deployment account (e.g. `root` during pre-production setup) |
| `VPS_SSH_PRIVATE_KEY` | Private key generated for GitHub Actions deployment |
| `VPS_KNOWN_HOSTS` | Pinned SSH host-key line obtained via `ssh-keyscan -H <vps-ip>` |

Application secrets are encrypted with SOPS/age and versioned under `secrets/encrypted/`. They do not belong in GitHub Actions secrets.

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

# Sulocraft secret management

This follows the owner-provided SOPS/age vault prompt. Never add credential values, decrypted output, or an age private key to Git.

## Agreed workflow

Preprod is the production rehearsal environment: use the same application code, deployment workflow, service topology, and security controls intended for production. Promotion should require selecting production configuration and credentials only. Keep environment selection explicit and fail closed when a target is missing; never reuse preprod secrets as a production fallback.

Use age public recipients to encrypt SOPS secret groups. The matching private key decrypts them. Public recipients may be committed in `.sops.yaml`; private keys remain outside the repository. A separate age keypair belongs to each authorized developer, and the VPS keeps its own private key at `/etc/sulocraft/age/keys.txt` with `root:root` ownership and mode `0600`.

Local development uses encrypted service-scoped groups and `scripts/decrypt_secrets.py` (supporting dynamic environment selection via `--env preprod|dev|prod` or `APP_ENV`/`SULOCRAFT_ENV`); generated plaintext stays under ignored `backend/.secrets/<env>/` with owner-only permissions. On the VPS, the deploy/bootstrap process decrypts only the needed groups into `/run/sulocraft/` with mode `0700` for the directory and `0600` for files, then gives each Docker service only its own credentials. The age private key is never mounted into a container.

Do not leave a decrypted production `.env` in the project or give one giant environment file to every service. If deployment tooling temporarily needs dotenv input, it must be ignored, permission-restricted, excluded from rsync/build contexts, and split into service-scoped files before Compose starts.

```text
secrets/encrypted/backend.enc.env  -> /run/sulocraft/backend/
secrets/encrypted/postgres.enc.env -> /run/sulocraft/postgres/
secrets/encrypted/backup.enc.env   -> /run/sulocraft/backup/
```

For a single VPS, SOPS + age is sufficient; do not add HashiCorp Vault, Kubernetes, or Consul without a concrete need.

## Secret inventory

| Setting | Consumer | Required in local development | Required in production |
| --- | --- | --- | --- |
| `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | API / PostgreSQL | Local or preprod values | Yes |
| `SESSION_SECRET` | Backend | Only if the actual auth design requires it | Only if required by the actual auth design |
| `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` | Backend image storage | Only for R2 upload tests | When R2 storage is enabled |
| `RESEND_API_KEY` | Backend email | Optional; mock provider works locally | When Resend is enabled |
| `GOOGLE_CLIENT_SECRET`, `FACEBOOK_APP_SECRET` | Backend OAuth | Optional if local flow does not need server-side exchange | If required by configured OAuth flow |
| `FAST2SMS_API_KEY`, `TWILIO_AUTH_TOKEN` | Backend SMS | Optional; mock provider works locally | Only for selected provider |
| `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET` | Backend payments | Optional; mock payments work locally | When Razorpay is enabled |
| `POSTGRES_BACKUP_*` / backup R2 credentials | Backup job | No | When remote backups are enabled; use credentials separate from product media |

Public/non-secret configuration such as `APP_ENV`, `FRONTEND_URL`, `IMAGE_BASE_URL`, bucket names, sender labels, OAuth client IDs, and `VITE_API_BASE_URL` belongs in ordinary configuration. Never pass private values to Vite, frontend source, build arguments, or image layers.

## Current implementation status

- Backend configuration supports `<SETTING>_FILE` with precedence over `<SETTING>` and fails closed with redacted errors. Focused tests cover precedence, fallback, and error redaction.
- `.env.example` files contain names/placeholders only.
- SOPS is available through the ephemeral Docker image `ghcr.io/getsops/sops:v3.13.3`, so the workflow need not install host OS packages.
- Local age-key access is repaired and verified. `.sops.yaml` contains the local and VPS public recipients; the three preprod groups are encrypted and verified decryptable by both authorized identities.
- The VPS age key is now provisioned and verified as `root:root` mode `0600`, in a `root:root` directory with mode `0700`. Only its public recipient is recorded in the vault work notes.
- Automated VPS key bootstrap and guarded rotation are implemented; see Work 003 tasks 3.6–3.7.
- The encrypted deploy script excludes plaintext env files from rsync. The live API was previously deployed from the saved plaintext preprod env as an owner-directed recovery; this does not count as encrypted-vault release verification.
- The local decrypt helper and Compose overlay have built the API and frontend successfully; API health and the same-origin API proxy return HTTP 200. Full storefront visual verification remains pending because the available browser automation blocks `/api/v1` requests. Gemini's catalogue seed idempotency task is also active; see Work 003 Task 3.11.

## Local development and VPS setup

1. Generate an age keypair for each authorized developer and a separate keypair directly on the VPS. Share only public recipient strings. The local developer key and VPS key are provisioned; their private contents remain undisclosed.
2. Store developer private keys outside the repository with owner-only permissions. Store the VPS private key at `/etc/sulocraft/age/keys.txt`, root-owned with mode `0600`.
3. `.sops.yaml` contains local and VPS public recipient rules. The three preprod groups are encrypted at `secrets/encrypted/{backend,postgres,backup}.enc.env` and verified decryptable by both authorized keys.
4. Commit only `secrets/encrypted/*.enc.env` ciphertext and `.sops.yaml`; never add plaintext credentials, private keys, or generated runtime files.
5. For local Docker, run `python3 scripts/decrypt_secrets.py --env preprod` (or `--env dev`) to decrypt backend and PostgreSQL groups into owner-only files. It points the API at the isolated local Compose database and writes only file paths (never values) to the generated Compose env. Start with `docker compose --env-file backend/.secrets/preprod/compose.env -f docker/compose.yaml -f docker/compose.preprod.yaml up --build`; remove local files with `python3 scripts/decrypt_secrets.py --clean --env preprod`.
6. The VPS bootstrap/deploy scripts are implemented, but encrypted-vault deployment is not yet accepted. The last owner-directed recovery used the saved plaintext preprod env to restore the live API. Before claiming secure release, validate the SOPS bootstrap on the VPS, preserve rollback behavior, and verify health without transferring plaintext env files.

Set `SOPS_AGE_KEY_FILE` when selecting a developer or VPS key. Never send private keys or decrypted env files over chat, paste them into commands, or print them in logs.

## Rotation and recovery

To rotate one credential, edit only the owning service group, re-encrypt it for the approved recipients, deploy, verify the consumer, then revoke the old provider credential. When recipients change, re-encrypt each affected group before removing an old recipient. Guarded VPS age-key bootstrap and candidate rotation scripts are implemented; key rotation has not been executed. Keep a controlled owner recovery key so a lost device does not make production data unrecoverable.

Deployment must validate required values without printing them. Errors may name a missing setting, never its value. Preprod currently has no dedicated backup R2 key, so its encrypted backup group reuses the existing preprod R2 key; provision a separate bucket-scoped key and re-encrypt before production use.

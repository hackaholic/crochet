# Sulocraft secret management

This follows the owner-provided SOPS/age vault prompt. Never add credential values, decrypted output, or an age private key to Git.

## Agreed workflow

Use age public recipients to encrypt SOPS secret groups. The matching private key decrypts them. Public recipients may be committed in `.sops.yaml`; private keys remain outside the repository. A separate age keypair belongs to each authorized developer, and the VPS keeps its own private key at `/etc/sulocraft/age/keys.txt` with `root:root` ownership and mode `0600`.

Local development stays convenient through ignored `backend/.env.preprod` values or equivalent local secret files. Encrypt development values into service-scoped SOPS groups before Git sees them. On the VPS, the deploy/bootstrap process decrypts only the needed groups into `/run/sulocraft/` with mode `0700` for the directory and `0600` for files, then gives each Docker service only its own credentials. The age private key is never mounted into a container.

Do not leave a decrypted production `.env` in the project or give one giant environment file to every service. If deployment tooling temporarily needs dotenv input, it must be ignored, permission-restricted, excluded from rsync/build contexts, and split into service-scoped files before Compose starts.

```text
secrets/backend.sops.yaml  -> /run/sulocraft/backend/
secrets/postgres.sops.yaml -> /run/sulocraft/postgres/
secrets/backups.sops.yaml  -> /run/sulocraft/backups/
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
- The SOPS container is available through Docker, so the workflow need not install host OS packages.
- SOPS recipient rules and encrypted secret groups do not exist yet. Local age-key setup is incomplete and must be resolved before encryption.
- The VPS age key is now provisioned and verified as `root:root` mode `0600`, in a `root:root` directory with mode `0700`. Only its public recipient is recorded in the vault work notes.
- Automated VPS key bootstrap and guarded rotation are still required; see Work 003 tasks 3.6–3.7.
- Current VPS deployment still transfers a plaintext preprod environment file. Replace this before vault deployment; never rsync ignored local env files.
- Local API startup is currently blocked by a duplicate product/occasion seed association. Fix and verify the integrated Docker stack before local acceptance.

## Local development and VPS setup

1. Generate an age keypair for each authorized developer and a separate keypair directly on the VPS. Share only public recipient strings.
2. Store developer private keys outside the repository with owner-only permissions. Store the VPS private key at `/etc/sulocraft/age/keys.txt`, root-owned with mode `0600`.
3. Add public recipient rules in `.sops.yaml`. Preprod groups may include authorized developer recipients and the VPS recipient; production groups include the VPS recipient and an owner-approved recovery recipient.
4. Keep local preprod credentials in ignored files or local secret files. Use SOPS to encrypt per-service groups; commit only encrypted `*.sops.yaml` groups.
5. For local Docker, decrypt only required development groups to protected local files, start/rebuild Compose, and verify API plus UI.
6. On VPS deploy, transfer encrypted groups only, decrypt the selected groups under `/run/sulocraft/`, mount/inject only the values each Compose service needs, verify health, and clean temporary files while preserving safe rollback.

Set `SOPS_AGE_KEY_FILE` when selecting a developer or VPS key. Never send private keys or decrypted env files over chat, paste them into commands, or print them in logs.

## Rotation and recovery

To rotate one credential, edit only the owning service group, re-encrypt it for the approved recipients, deploy, verify the consumer, then revoke the old provider credential. When recipients change, re-encrypt each affected group before removing an old recipient. Keep a controlled owner recovery key so a lost device does not make production data unrecoverable.

Deployment must validate required values without printing them. Errors may name a missing setting, never its value. Keep backup credentials separate from product image credentials wherever practical.

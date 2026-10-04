# Encrypted secret groups only

Commit only SOPS-encrypted service groups: `encrypted/backend.enc.env`, `encrypted/postgres.enc.env`, and `encrypted/backup.enc.env`. Plaintext dotenv files, decrypted values, and age private keys must remain outside Git. See [docs/secrets.md](../docs/secrets.md) for the workflow and task status.

The encrypted groups and `.sops.yaml` recipient rules are provisioned for preprod. The backup group currently reuses the preprod R2 credentials because no dedicated backup credentials were configured; production backup must use its own bucket-scoped key and be re-encrypted before launch. Never put real credentials in examples or starter files.

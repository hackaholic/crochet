# Encrypted secret groups only

Commit only SOPS-encrypted service groups such as `backend.sops.yaml`, `postgres.sops.yaml`, and `backups.sops.yaml`. Plain YAML, dotenv files, decrypted values, and age private keys must remain outside Git. See [docs/secrets.md](../docs/secrets.md) for the workflow and task status.

Encrypted groups and `.sops.yaml` recipient rules will be added after authorized age public recipients are provisioned. No real credentials belong in examples or starter files.

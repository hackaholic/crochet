# Task 3.8 — Provision .sops.yaml recipient rules and encrypt preprod groups

**Owner:** Codex / Owner
**Status:** Completed

## Objective

Add `.sops.yaml` configuration containing authorized public age recipients (developer and VPS recipients), and encrypt approved preprod dotenv groups into `secrets/encrypted/backend.enc.env`, `secrets/encrypted/postgres.enc.env`, and `secrets/encrypted/backup.enc.env`. This filename/format matches Gemini's active `bootstrap_secrets.sh` contract, which decrypts env-format groups and materializes one secret file per variable.

## Context and contract

Never commit plaintext credentials, private age keys, or unencrypted secret files. Only public age recipients may be committed in `.sops.yaml`. Refer to `docs/secrets.md`.

## Scope

- In scope:
  - Create root `.sops.yaml` mapping recipient rules to the three `secrets/encrypted/*.enc.env` groups.
  - Encrypt preprod secret values into service-scoped files.
  - Verify that only encrypted ciphertext is tracked by Git.
- Out of scope:
  - Exposing private keys.

## Dependencies and relevant files

- Depends on: Task 3.5 local developer age key provisioning.
- Inspect/edit:
  - `.sops.yaml`
  - `secrets/`
  - `docs/secrets.md`

## Acceptance checks

- [x] `.sops.yaml` contains correct creation rules and public recipients.
- [x] All three `secrets/encrypted/*.enc.env` groups are SOPS-encrypted and decryptable with the authorized local and VPS age keys; plaintext comparisons did not print values.
- [x] No plaintext files exist in `secrets/`; Git ignore rules allow only encrypted `.enc.env` groups.
- [x] `bash scripts/security/scan-config.sh` passes all 6 configuration checks.

## Handoff back

- Update `work/work-003-vault/tasks.md` and `notes.md`.

# Task 3.8 — Provision .sops.yaml recipient rules and encrypt preprod groups

**Owner:** Codex / Owner
**Status:** Pending

## Objective

Add `.sops.yaml` configuration containing authorized public age recipients (developer and VPS recipients), and encrypt approved preprod secret groups into `secrets/backend.sops.yaml`, `secrets/postgres.sops.yaml`, and `secrets/backups.sops.yaml`.

## Context and contract

Never commit plaintext credentials, private age keys, or unencrypted secret files. Only public age recipients may be committed in `.sops.yaml`. Refer to `docs/secrets.md`.

## Scope

- In scope:
  - Create root `.sops.yaml` mapping recipient rules to `secrets/*.sops.yaml`.
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

- [ ] `.sops.yaml` contains correct creation rules and public recipients.
- [ ] `secrets/*.sops.yaml` are encrypted and decryptable with authorized age keys.
- [ ] No plaintext files exist in `secrets/`.

## Handoff back

- Update `work/work-003-vault/tasks.md` and `notes.md`.

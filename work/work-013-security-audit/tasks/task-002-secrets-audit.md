# Task 9.2 — Secret scanning and secret architecture audit

**Owner:** Gemini
**Status:** Pending

## Objective

Implement `scripts/security/scan-secrets.sh` (Gitleaks integration) and `scripts/security/scan-config.sh` (secret architecture validation) to detect unencrypted credentials and enforce the SOPS + age vault architecture.

## Context and contract

Refer to `docs/secrets.md` and `work/work-003-vault/`.
The scanner must detect committed API keys, OAuth secrets, R2 credentials, DB passwords, private age keys, and tokens without printing secret contents to logs.

## Scope

- In scope:
  - `scripts/security/scan-secrets.sh` scanning tracked files, staged changes, and git history.
  - Reviewed suppression via `.gitleaks.toml`.
  - `scripts/security/scan-config.sh` verifying:
    - No plaintext production `.env` committed.
    - No age private key in repo or container mounts.
    - All `*.sops.yaml` files are encrypted.
    - PostgreSQL port 5432 is not publicly exposed.
    - `VITE_*` variables are strictly public.
- Out of scope:
  - Modifying decrypted secret values.

## Dependencies and relevant files

- Depends on: Task 9.1.
- Inspect/edit:
  - `scripts/security/scan-secrets.sh`
  - `scripts/security/scan-config.sh`
  - `.gitleaks.toml`

## Acceptance checks

- [ ] `scan-secrets.sh` runs and exits 0 on clean repo, fails closed on test dummy secret.
- [ ] `scan-config.sh` verifies Compose and secret file permissions without leaking secrets.

## Handoff back

- Update `work/work-013-security-audit/tasks.md` and `notes.md`.

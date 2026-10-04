# Task 3.12 — Integrate SOPS dotenv inputs with local and VPS runtime

**Owner:** Codex
**Status:** Completed
**Work item:** Work 003

## Objective

Make SOPS dotenv ciphertext decrypt consistently in the local helper, VPS bootstrap, and rotation checks, and ensure Alembic honors the same file-backed database URL as the API.

## Context and contract

- Follow the Work 003 decisions: encrypted groups use `.enc.env`; private keys stay outside Git and application containers; secret values must not appear in logs.
- Integration found SOPS cannot infer `dotenv` from the `.enc.env` suffix. It needs explicit `--input-type dotenv --output-type dotenv` flags.
- Alembic previously preferred the plain `DATABASE_URL` environment variable over `DATABASE_URL_FILE`, causing local migrations to authenticate with stale Compose defaults.

## Scope

- In scope: add explicit dotenv flags to decryption/rotation commands; use the shared file-aware database URL resolver for Alembic; regression-test local secret materialization and migration precedence.
- Out of scope: changing credentials, key rotation, external deployment, or changing the owner-approved database contents.

## Dependencies and relevant files

- Depends on: Tasks 3.1, 3.3, 3.4, 3.8.
- Inspect/edit: `scripts/decrypt_preprod_secrets.py`, `backend/scripts/bootstrap_secrets.sh`, `backend/scripts/rotate_vps_key.sh`, `backend/app/core/config.py`, `backend/alembic/env.py`, and focused tests.

## Acceptance checks

- [x] Actual encrypted dotenv groups decrypt with explicit input/output types without printing plaintext.
- [x] Local and VPS decrypt paths specify dotenv formats; rotation verification does too.
- [x] Alembic uses `DATABASE_URL_FILE` even when a stale plain `DATABASE_URL` is present; a one-off Compose migration succeeded against local PostgreSQL.
- [x] Rotation verification's Docker fallback specifies dotenv formats and successfully verifies all three encrypted groups with the authorized local key.
- [x] Local helper tests pass (3/3); security scan passes (6 checks); local API and frontend containers build, and API health is HTTP 200.
- [x] Local storefront visual verification: the homepage renders the campaign hero image, product cards, occasions, and story section from the local API; API and same-origin proxy checks return HTTP 200.

## Handoff back

- Record changed files and exact verification in Work 003 `notes.md`.
- Keep Task 3.9 open until Gemini completes repeat-seed verification; visual rendering has now been confirmed locally.
- Do not push or deploy until integrated local review is complete.

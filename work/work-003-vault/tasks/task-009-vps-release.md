# Task 3.10 — Owner review and encrypted VPS release deployment

**Owner:** Owner + Codex
**Status:** Pending

## Objective

Review local verification results with the owner, push encrypted configuration changes to `dev`, execute the SOPS/age VPS deployment workflow, and verify that the API and frontend operate securely on `https://dev.sulocraft.com` without plaintext secrets in Git or container images.

## Context and contract

Follow DEC-003-1 through DEC-003-3. The VPS must decrypt secrets into `/run/sulocraft/` on deploy, mount service-scoped files into containers, and verify container health before traffic cutover.

## Scope

- In scope:
  - Run `backend/scripts/deploy_vps.sh` using encrypted secrets.
  - Verify `/run/sulocraft` permissions (`0700` dir, `0600` files).
  - Verify `https://dev.sulocraft.com/health` and live storefront.
- Out of scope:
  - Modifying production DNS.

## Dependencies and relevant files

- Depends on: Task 3.3 VPS deploy script, Task 3.4 tests, Task 3.9 local verification.
- Inspect/edit:
  - `backend/scripts/deploy_vps.sh`
  - `docs/secrets.md`

## Acceptance checks

- [ ] Release deploys successfully on VPS without errors.
- [ ] No plaintext `.env` files transferred over rsync or stored in release directory.
- [ ] Service health check passes and containers run healthy.

## Handoff back

- Mark Work 003 completed in `work/INDEX.md` and `work/work-003-vault/tasks.md`.

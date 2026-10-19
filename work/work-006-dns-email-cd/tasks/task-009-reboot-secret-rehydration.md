# Task 6.9 — Recover runtime secrets automatically after VPS reboot

**Owner:** Codex
**Status:** Pending
**Work item:** Work 006

## Objective / scope
Prevent recurrence of6.8: regenerate ephemeral runtime secrets before starting environment containers on boot. Keep `/run` ephemeral and encrypted vault persistent; do not move plaintext secrets to permanent disk. Use the same configurable flow for preprod and prod, with separate identities/paths/groups and fail-closed production configuration.

## Dependencies and relevant files
- Depends on: 6.8
- Dependency context: Incident recovery first; reuse installed vault bootstrap/deployment config, do not introduce a parallel manual release mechanism.
- Blocked by: None
- Blocker reason: None
- Next action: Design configurable environment boot ordering and add local tests before installing on VPS.
- Inspect/edit: deploy_vps.sh, backend/scripts/bootstrap_secrets.sh, deployment config/automation tests; environment-scoped systemd template if selected.

## Acceptance / test cases
- [ ] Unit/integration: validated environment selects exact vault/key/runtime/release/project; prod cannot fall back to preprod.
- [ ] Failure/security: missing key, failed decryption or mismatched DB target prevents service startup without leaking plaintext.
- [ ] Lifecycle: secret bootstrap precedes DB/API restart; no dependency cycle if bootstrap uses Docker SOPS. Account for Docker restart policies attempting early restarts.
- [ ] Secrets retain0700 directories/0600 files; database volume and existing artifact unchanged.
- [ ] Locally test orchestration, then verify controlled preprod service restart and owner-coordinated reboot; production remains unmodified.

## Security validation
Trust boundary: root boot orchestration reading existing encrypted vault. Review command quoting, executable ownership, symlink release resolution, systemd ordering, privilege scope and redacted logs. No raw secrets in unit config or command lines. Disposition: Pending.

## Handoff back
Record exact config/test evidence, deployment effects and any reboot required before marking complete. No claim of durable recovery based only on an immediate manual restart.

# Work 026 tasks

## In Progress
None.

## Pending
None.

## Completed

- [x] 26.0 Codex: Audit current config paths. Backend `config_value()` supports `*_FILE` and env values; API exposes public OAuth config; local Compose's Vite fallback is obsolete; VPS release rendering omits Google client ID file path and API secret mount. Evidence is recorded in `notes.md`.
- [x] 26.1 Codex: [Use API runtime configuration for OAuth in the frontend](tasks/task-001-api-runtime-oauth-config.md) — no Vite auth IDs; social controls wait for API config; 6/6 focused tests and typecheck pass; local API runtime ID and storefront verified.
- [x] 26.2 Codex: [Make local Compose configuration explicit and repeatable](tasks/task-002-local-env-config.md) — root `.env` command is documented; API receives local ID while frontend has no Vite OAuth variable.
- [x] 26.3 Codex: [Wire SOPS OAuth files through preprod/prod deployment](tasks/task-003-sops-oauth-runtime-parity.md) — target-specific Google ID/secret paths render for both environments and mount only into the API; focused tests and SAST pass.
- [x] 26.4 Codex: [Prove local/preprod/prod config parity and update runbooks](tasks/task-004-config-parity-verification.md) — direct-env/file-source parity test, environment isolation, non-disclosure checks, local API/storefront health, and runbook update completed. Local OAuth sign-in itself remains unverified because no Google client ID is configured locally.
- [x] 26.5 Codex: [Export OAuth secret-file paths in VPS deployment](tasks/task-005-deployment-oauth-secret-env.md) — both remote Compose paths now export target-specific Google OAuth secret paths, including legacy preprod backup fallback; focused tests, shell syntax, and SAST pass. Preprod deployment remains pending.

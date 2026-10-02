# Work 003 notes

- VPS SSH access succeeds as root; Docker exists. Owner created the VPS age key; verification confirmed `/etc/sulocraft/age` is `root:root` mode `0700` and `keys.txt` is `root:root` mode `0600`.
- VPS public age recipient (safe to share/store): `age1tg0gun8qc9a9t0j92eg0uzhqt9axnptf3hchqz8cxl5aaqva3vsqdkvz0k`.
- SOPS and Alpine images were pulled for ephemeral tooling; do not install packages on the host OS.
- Do not inspect, print, copy, or commit values from local ignored environment files.
- Task 3.1 completed:
  - Updated `backend/docker-compose.yml` to define service-scoped secrets (`postgres_db`, `postgres_user`, `postgres_password` for `postgres`; `database_url` for `api`). Removed all hardcoded fallback credentials (`sulocraft_secure_pw`). Added `_FILE` environment variables for backend secret resolution.
  - Enhanced `backend/app/core/config.py` `config_value()` to handle whitespace trimming and discover candidate mounts under `/run/secrets/backend` and `/run/secrets` with strict fail-closed behavior without disclosing paths or secret contents.
  - Updated `backend/scripts/backup_db.sh` to resolve credentials via `read_secret`, removed hardcoded default password, added failure checks when credentials are missing, and prioritized dedicated `BACKUP_R2_*` credentials over general `R2_*` credentials.
  - Added comprehensive tests in `backend/tests/test_config_secrets.py` verifying Compose secret isolation, `docker-compose config` validation with dummy secret files, fail-closed handling on missing passwords/files, and backup R2 credential precedence. All 8 secret tests and 142 total backend tests pass.
- Task 3.2 now has a dedicated pickup-ready contract at `tasks/task-002-local-preprod-decrypt.md`; Gemini should take it only when explicitly assigned and update its status/notes on handback.
- Next action: assign Gemini Task 3.2 (local preprod decrypt helper). Owner help is still needed to fix local key permissions (Task 3.5).
- No Git push, VPS secret deployment, or dev deployment has occurred.

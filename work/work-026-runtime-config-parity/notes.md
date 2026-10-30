# Work 026 notes

## Initial audit — 2026-10-31

- Backend `config_value()` checks `<SETTING>_FILE` first, then the direct environment variable. `/api/v1/auth/config` returns public provider IDs from backend settings.
- `docker/compose.preprod.yaml` has Google ID/secret file references and SOPS-backed secret definitions for local preprod-style Compose.
- `docker/compose.yaml` passes Google IDs to the frontend as `VITE_*` and allows a direct backend env fallback. The `AuthModal` message still directs operators to set `VITE_GOOGLE_CLIENT_ID`.
- `scripts/deploy_vps.py::render_runtime_environment()` currently renders DB and Cashfree secret paths but not Google ID/secret paths. `backend/docker-compose.yml` lacks the Google ID file secret mount and sets Google ID as a direct value.
- `.env.preprod` contains non-secret frontend/deployment settings only; it is not the SOPS backend secret store. Do not add OAuth credentials to it.
- The most recent local runtime check with `.env.preprod` showed `/api/v1/auth/config` without a Google ID. Local was then recreated with the ignored local `.env`, with frontend Vite Google ID explicitly empty; API config then reported the ID present and storefront returned HTTP 200. Credential values were not recorded.

## Task 26.1 — 2026-10-31

- Removed the frontend Vite OAuth fallbacks and stale user-facing instruction. Social buttons now wait for `/api/v1/auth/config`; missing config shows a provider-neutral unavailable message.
- Updated local Compose to supply `GOOGLE_CLIENT_ID` and `FACEBOOK_APP_ID` to the API only. Added 6 focused component tests covering runtime config, load state, missing config, and email login regression.
- Verification: `./scripts/test.sh frontend pnpm exec vitest run src/components/AuthModal.test.tsx` -> 6/6; `./scripts/test.sh frontend pnpm typecheck` -> pass; `docker-compose --env-file .env -f docker/compose.yaml up -d --build frontend` -> healthy services; `/api/v1/auth/config` has Google ID, frontend Vite Google variable absent, storefront HTTP 200; `git diff --check` -> pass.
- Security disposition: pass. Frontend receives only the allowlisted public ID from the API; no credential value recorded. VPS/preprod untouched.

## Task 26.2 — 2026-10-31

- Documented the direct local `.env` Compose command and the separate SOPS-backed local overlay command in `docs/secrets.md`.
- Added local backend OAuth ID placeholders to root `.env.example`; no Vite OAuth variables remain there.
- Verification reused the passing Task 26.1 local Compose/API check: root `.env` provides the ID to the API, the frontend Vite variable is absent, `/api/v1/auth/config` reports the ID present without exposing its value, and storefront returns HTTP 200. Focused tests 6/6 and typecheck pass.
- Security disposition: pass; no plaintext values recorded or committed.

## Task 26.3 — 2026-10-31

- VPS release rendering now emits selected-target `GOOGLE_CLIENT_ID_FILE` and `GOOGLE_CLIENT_SECRET_FILE` paths. `backend/docker-compose.yml` maps those host paths to backend-only Docker secrets; the API resolves them at `/run/secrets/...`. No environment-specific application branch or preprod fallback was added.
- Verification: `./scripts/test.sh backend tests/test_config_secrets.py tests/test_vps_release_artifact.py tests/test_auth.py tests/test_vault_deploy.py` -> 48 passed, 3 skipped. Target isolation suite `./scripts/test.sh backend tests/test_vps_database_isolation.py` -> 1 passed, 2 skipped. `bash scripts/security/scan-sast.sh` -> 0 blocking high/critical findings; 33 repository warnings. OAuth secret values were not printed.
- Security disposition: pass. No VPS connection, deployment, or production secret creation performed.

## Task 26.4 — 2026-10-31

- Added a direct-environment vs file-backed `config_value()` parity test using a temporary dummy value. Updated `docs/secrets.md` with the single logical setting contract, local `.env` source, and isolated preprod/prod SOPS path behavior.
- Verification: focused backend suite -> 48 passed, 3 skipped; environment isolation suite -> 1 passed, 2 skipped; local `docker-compose --env-file .env -f docker/compose.yaml ps` showed API and DB healthy and frontend running; `/health`, `/api/v1/auth/config`, and storefront returned HTTP 200. Endpoint omitted the Google ID because none is configured in local runtime and did not expose a client secret. SAST had zero blocking high/critical findings.
- Security disposition: pass. Local provider sign-in and any VPS/preprod deployment remain outside verified scope. No push/deployment.

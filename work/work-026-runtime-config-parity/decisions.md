# Work 026 decisions

## DEC-026-001 — One logical app config, environment-specific source

**Context:** Local development uses an ignored `.env`; the VPS decrypts SOPS groups into per-environment runtime files. Both must run the same application code and use the same logical setting names.

**Decision:** Application code reads settings through the existing backend resolver (`NAME_FILE` first, then `NAME`). Local Compose supplies approved local values as environment variables; preprod/prod deployment renders the selected environment's file paths. No environment-specific application branch or preprod-to-prod fallback is allowed.

**Consequences:** Local and VPS Compose adapters and tests must be explicit about their input file/source. Missing required settings fail closed at the consumer. Secret values remain backend-only.

## DEC-026-002 — OAuth public identifiers are delivered at runtime

**Context:** `GET /api/v1/auth/config` already returns the public Google/Facebook identifiers resolved by the backend. The frontend still has a Vite build-time fallback, creating separate config paths and misleading setup text.

**Decision:** The frontend obtains public OAuth identifiers only from the API runtime config endpoint. Remove `VITE_GOOGLE_CLIENT_ID` / `VITE_FACEBOOK_APP_ID` as required inputs and remove them from frontend Compose/build configuration. The backend owns credential resolution from local env or SOPS-rendered files.

**Consequences:** Local OAuth requires the backend to receive its local `GOOGLE_CLIENT_ID`; preprod/prod require isolated SOPS file paths. No OAuth secret or provider config is compiled into frontend assets.

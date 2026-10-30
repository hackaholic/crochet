# Work 026 — Runtime configuration parity across local, preprod and prod

**Objective:** Give local, preprod and prod one stable application configuration contract. Only the source changes: local development reads its ignored `.env`; preprod and prod read their own SOPS-rendered runtime secret files.

**Scope:** Backend setting resolution, OAuth public config delivery to the frontend, local Compose input, and environment-specific SOPS path rendering. Preserve one application artifact and fail-closed environment isolation.

**Current state:** The frontend now reads public OAuth IDs from `/api/v1/auth/config`. Local Compose uses the ignored `.env`; preprod/prod runtime rendering selects distinct SOPS-backed Google ID/secret paths and mounts the files only into the API. Backend, isolation, API non-disclosure, and local health checks pass. Local Google sign-in itself was not exercised because the local runtime currently has no Google client ID configured. No secret values are recorded here.

**Architecture:** Keep the existing modular monolith and centralized backend config resolver. The frontend gets public OAuth identifiers at runtime from the API. Local `.env` uses logical variables such as `GOOGLE_CLIENT_ID`; preprod/prod Compose points the same setting to environment-specific SOPS files with `GOOGLE_CLIENT_ID_FILE`. Frontend bundles never receive OAuth settings.

**Dependencies:** Completed inputs: Work 003 tasks 3.12 and 3.14; Work 012 task 12.05.1; Work 007 task 7.2.4.1. This work closes cross-environment gaps without redoing vault creation, key setup, or Cashfree integration.

**Definition of done:** The same app code/API config route works with local env-backed settings and preprod/prod file-backed settings; no Vite OAuth IDs are required; local Compose has one documented invocation; deployment renders isolated SOPS paths for both preprod and prod; tests prove source parity, fail-closed behavior and no frontend secret exposure. Local checks pass before any deployment. No deployment is included in this work.

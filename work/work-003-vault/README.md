# Work 003 — SOPS/age secret vault

**Objective:** Keep credentials out of Git, Docker images, and frontend bundles while making local development and single-VPS deployment practical.

**Scope:** SOPS + age, service-scoped backend/PostgreSQL/backup groups, local preprod decryption, VPS bootstrap/deploy automation, validation, tests, and rotation/recovery docs.

**Current state:** In Progress. Generic backend `<SETTING>_FILE` support and focused tests are complete. The VPS age key has been provisioned and verified; local developer-key access and key automation remain pending. Gemini can implement Compose/deploy work using dummy credentials.

**Architecture:** Public age recipients encrypt; matching private keys decrypt. Local developer private keys stay outside the repo. VPS private key stays at `/etc/sulocraft/age/keys.txt`, root-owned mode `0600`; it never enters app containers. VPS decrypts only required service groups under `/run/sulocraft/`.

**Dependencies:** Gemini's handoff in `docs/handoffs.md`; variable inventory in `docs/secrets.md`; local Docker currently has an unrelated API seed blocker.

**Done when:** Local dev secrets can be decrypted safely; VPS deploy transfers encrypted groups only and materializes least-privilege runtime files; tests pass; local Docker is healthy and verified; owner reviews before dev deployment.

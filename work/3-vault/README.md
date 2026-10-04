# Work 003 — SOPS/age secret vault

**GitHub Issue:** [#3](https://github.com/hackaholic/crochet/issues/3) · Work 003

**Objective:** Keep credentials out of Git, Docker images, and frontend bundles while making secure local decryption and service-scoped runtime secret materialization practical.

**Scope:** SOPS + age, service-scoped backend/PostgreSQL/backup groups, configurable local/VPS secret decryption and materialization interfaces, validation, tests, and rotation/recovery docs. VPS release orchestration lives in Work 012.

**Current state:** Completed. SOPS/age recipient rules and encrypted secret groups are provisioned; local developer and VPS key permissions are verified. Local decryption, Compose secret overlay, configurable environment selection, VPS secret bootstrap/rotation scripts, fail-closed database guards, disposable test container environment, and 100% full-suite regression coverage (173/173 tests) are complete. Local Docker services are verified healthy. VPS release automation and live deployment acceptance are handed off to Work 012.

**Architecture:** Public age recipients encrypt; matching private keys decrypt. Local developer private keys stay outside the repo. VPS private key stays at `/etc/sulocraft/age/keys.txt`, root-owned mode `0600`; it never enters app containers. Preprod follows the same application code, deployment workflow, service topology, and security controls intended for production. Runtime environment selection and paths come from explicit config, environment, or CLI inputs. Promotion to production should require selecting production configuration and credentials only; missing production configuration must fail closed rather than reuse preprod secrets.

**Dependencies:** Task-specific handoffs are recorded in this folder's `coordination.md` and task contracts; older Gemini reports are in the [handoff archive](../../docs/archive/handoffs-history.md). Variable inventory: `docs/secrets.md`. Work 012 owns VPS release mechanics and consumes Work 003's encrypted secret groups/bootstrap interface. Work 006 owns CI orchestration and consumes Work 012's deploy command.

**Done when:** Local secrets can be decrypted safely; encrypted groups materialize as least-privilege runtime files; configuration and cross-environment isolation tests pass; local Docker is healthy and verified. VPS release automation and live deployment acceptance belong to Work 012.

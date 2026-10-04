# Work 003 decisions

### DEC-003-1 — Use SOPS + age on the single VPS

**Decision:** Use SOPS with age recipients; do not deploy HashiCorp Vault, Kubernetes, or Consul.

**Reason:** The current deployment is a single-VPS Docker Compose application and needs a lightweight encrypted-at-rest workflow.

**Impact:** Git stores only encrypted service groups. Public recipients are safe to commit; private keys stay on authorized hosts.

### DEC-003-2 — Split secrets by service

**Decision:** Keep backend, PostgreSQL, and backup secrets in separate groups and materialize only required files under `/run/sulocraft/`.

**Reason:** A compromised service must not automatically gain unrelated database or backup credentials.

**Impact:** Do not leave one global production `.env` accessible to every container. Local dev may keep ignored preprod environment inputs.

### DEC-003-3 — Keep frontend configuration public-only

**Decision:** Never pass private credentials through Vite, frontend source, build arguments, or image layers.

**Impact:** OAuth client IDs may be public only where the actual auth design requires them; client secrets remain backend-only.

### DEC-003-4 — Select deployment environment from runtime configuration

**Decision:** Deployment and secret decryption must accept the target environment through configuration, environment variables, or command-line arguments. Preprod-specific names and paths must not be embedded as the only supported deployment mode.

**Reason:** The same vault workflow should be reusable for preprod and later environments without editing application or deployment logic.

**Impact:** The current encrypted preprod groups remain the data source for today's release; future environments must provide their own explicit config and encrypted groups.

### DEC-003-5 — Keep preprod production-equivalent

**Decision:** Build and operate preprod with the same application code, deployment workflow, service topology, and security controls intended for production. Environment differences must be supplied through validated configuration and environment-specific encrypted secret groups.

**Reason:** Preprod is the production rehearsal environment. Promoting the application to production should require selecting production configuration and credentials, not changing code or introducing a separate deployment design.

**Impact:** Deployment configuration must be environment-neutral and support explicit `dev`, `preprod`, and `prod` targets where configured. Do not bake a preprod-only filename, path, host, or behavior into the workflow. Missing target configuration must fail closed; never silently reuse preprod secrets for production.

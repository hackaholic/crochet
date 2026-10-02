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

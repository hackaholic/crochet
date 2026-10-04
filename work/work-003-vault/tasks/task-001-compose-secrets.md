# Task 3.1 — Compose secret interfaces

**Owner:** Gemini
**Status:** Completed

**Goal:** Make Compose consume service-scoped secret files and remove insecure credential defaults.

**Scope:**

- PostgreSQL receives only its database name, user, and password.
- API receives its own credentials plus only the DB connection details required to reach PostgreSQL.
- Backup tooling receives only separate backup credentials.
- Keep the age private key out of containers and images.
- Support `_FILE` configuration where the backend setting resolver supports it.
- Keep local mock email/payment and local DB development straightforward.

**Constraints:** No committed/plaintext secrets or fallback passwords. Use dummy credentials in tests. Do not change the public root Vite env behavior.

**Verify:** Compose config validates with dummy files; a service does not receive another service's unrelated secret; missing required values fail clearly without exposing values.

**Handoff:** Record changed files, test results, and remaining dependencies in this work folder's `notes.md` and check off task 3.1 in `tasks.md`.

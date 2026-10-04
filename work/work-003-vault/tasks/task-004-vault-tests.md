# Task 3.4 — Vault/deploy regression tests

**Owner:** Gemini

**Goal:** Cover secret bootstrap and deployment failure modes without real credentials.

**Test cases:**

- Missing encrypted group, missing/invalid age key, and unsupported required setting fail clearly.
- Runtime directory/files have the required restrictive permissions.
- Logs/errors never contain dummy secret values.
- Temporary plaintext is cleaned after success/failure while rollback files needed by the active release remain available.
- Healthy service activates; unhealthy service fails and preserves the prior release.
- No ignored plaintext env file is included in rsync or Docker build context.

**Constraints:** Use disposable test keys and dummy values only. Do not read current ignored production/preprod credential values.

**Verify:** Run the relevant tests plus the full backend suite; write exact results to this work folder's `notes.md` and mark task 3.4.

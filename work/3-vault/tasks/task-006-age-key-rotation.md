# Task 3.7 — Guarded age-key rotation

**Owner:** Gemini + Codex

**Goal:** Rotate the VPS age identity without losing the ability to decrypt any committed SOPS group.

**Workflow:**

1. Generate a new candidate key at a separate path; never overwrite the active key.
2. Add the new public recipient to the appropriate `.sops.yaml` rules and update every affected encrypted group.
3. Confirm all encrypted groups can be decrypted with the candidate key and deploy/health-check using it while the old key remains available for rollback.
4. Require owner confirmation before retiring/removing the old private key. Keep an approved recovery recipient and protected backup procedure.

**Safety:** Do not expose private keys in logs, command output, Git, or app containers. Fail closed if any group cannot be re-encrypted or verified. Do not revoke provider credentials as part of age-key rotation.

**Verify:** Exercise rotation with temporary keys and dummy groups, including interrupted rotation and rollback. Update Work 003 task 3.7 and notes.

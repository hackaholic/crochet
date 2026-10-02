# Task 3.3 — VPS secret bootstrap and deploy

**Owner:** Gemini

**Goal:** Deploy from encrypted groups; decrypt only on the VPS into restricted runtime files.

**Scope:** Update `backend/scripts/deploy_vps.sh` and add `scripts/bootstrap-secrets.sh` or the project's equivalent. Validate required tools, VPS key presence/permissions, encrypted groups, and required settings. Transfer encrypted SOPS files only; exclude ignored local preprod env files from rsync and Docker contexts. Use `umask 077`, create `/run/sulocraft/` with mode `0700`, materialize service groups as `0600`, start Compose, check health, and clean failed/superseded plaintext safely.

**Preserve:** Existing backup-before-migration, timestamped release activation, rollback behavior, and Cloudflare frontend deployment config.

**Constraints:** Age private key remains host-only. Never log secret values or pass them in command-line arguments. Do not deploy or rotate live credentials during implementation.

**Verify:** Exercise with temporary age keys and dummy groups on a test/local deployment path; prove missing key/group and unhealthy service fail the deployment without secret disclosure.

**Handoff:** Record changed files, test results, and any operator action in `notes.md`; update task 3.3 status.

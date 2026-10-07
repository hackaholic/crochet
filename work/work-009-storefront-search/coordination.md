# Work 009 coordination

This file is the work-local coordination entry point. The work folder is the source of truth: read this file with README.md, tasks.md, decisions.md, and only the assigned task contract.

## Current handoffs

- **Gemini backend completed:** [Task 9.8 — Search empty-state discovery API](tasks/task-009-search-discovery-api.md). Core endpoint, 9.8.1 bounds/rate limiting, and 9.8.2 retention/purging are complete and locally verified.
- **Gemini preprod deployment completed:** [Task 9.10 — Preprod search API availability](tasks/task-009-preprod-search-api-availability.md). Verified release `0ca1ee0` deployed to preprod; `api-dev.sulocraft.com` returns HTTP 200 on suggestions and events endpoints.
- **Codex completed:** [Task 9.9 — Search suggestions unavailable state](tasks/task-009-search-suggestions-unavailable.md). The preprod overlay was verified to show neutral guidance for empty API arrays instead of the unavailable error.
- **Codex blocked:** Task 9.7 desktop-width visual acceptance; only the narrow in-app browser is available and the Chrome browser target is unavailable.

## Return protocol

The assigned agent updates the exact contract, tasks.md, notes.md, and this file before returning the task. The global registry at docs/handoffs.md points here; it does not duplicate this work's status.

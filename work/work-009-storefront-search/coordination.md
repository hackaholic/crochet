# Work 009 coordination

This file is the work-local coordination entry point. The work folder is the source of truth: read this file with README.md, tasks.md, decisions.md, and only the assigned task contract.

## Current handoffs

- **Gemini backend handoff returned:** [Task 9.8 — Search empty-state discovery API](tasks/task-009-search-discovery-api.md). Core endpoint and 9.8.1 telemetry bounds/rate limiting are complete and locally verified. Task 9.8.2 retention/rollup remains pending; see `tasks.md`.
- **Codex blocked:** Task 9.7 desktop-width visual acceptance; only the narrow in-app browser is available and the Chrome browser target is unavailable.
- **Codex completed diagnosis; blocked on backend:** [Task 9.9 — Search suggestions unavailable state](tasks/task-009-search-suggestions-unavailable.md). Preprod reproduces the error; its suggestions API returns 404. Local frontend/API render suggestions, so no frontend defect was found. Recheck after Task 9.10.
- **Preprod rollout blocked pending owner review:** [Task 9.10 — Preprod search API availability](tasks/task-009-preprod-search-api-availability.md). Local API returns HTTP 200 and local overlay renders suggestions; current preprod API still returns HTTP 404. Do not publish until the owner reviews and authorizes the preprod phase.

## Return protocol

The assigned agent updates the exact contract, tasks.md, notes.md, and this file before returning the task. The global registry at docs/handoffs.md points here; it does not duplicate this work's status.

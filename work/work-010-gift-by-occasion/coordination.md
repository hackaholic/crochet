# Work 010 coordination

This file is the work-local coordination entry point. The work folder is the source of truth: read this file with README.md, tasks.md, decisions.md, and only the assigned task contract.

## Current handoffs

- **Returned by Gemini; Codex integration is in progress:** [Task 10.18 — Default occasion visibility and image repair](tasks/task-018-default-occasions-and-images.md). Gemini reports the migration, seed/data repair, image-key updates, toggle behavior, and backend regression coverage complete. Codex still needs to rebuild the local Docker API/database/frontend and verify the five defaults and distinct images in browser before owner review.
- The ten additional occasion images are already uploaded to R2 and their public URLs verified. Backend work is limited to using the provided keys in DB/seed/migration; no copying or re-uploading is required.

## Return protocol

The assigned agent updates the exact contract, tasks.md, notes.md, and this file before returning the task. The global registry at docs/handoffs.md points here; it does not duplicate this work's status.

# Work 004 — Agent task workflow

**Objective:** Coordinate Codex and Gemini around small, verifiable subtasks while reducing repeated context reads.

**Current state:** Completed. Every current work folder has a coordination entry point; global handoff/status files are short registries, with prior history preserved; Gemini has a reusable context/rules prompt.

**Architecture:** `work/INDEX.md` is navigation only. Each work folder contains concise scope, actionable tasks, decisions, notes, and `coordination.md` for current owner/agent handoffs. Every cross-agent subtask gets its own contract file based on `work/TASK_TEMPLATE.md`. Global `docs/handoffs.md` and `docs/coordination-status.md` are compact indexes; historical detail is archived, not copied into live status.

**Done when:** All work folders have the same coordination entry point, active task contracts live beside their task, global handoff/status docs are compact registries, historical records remain available, Gemini has a reusable prompt, and links/statuses are checked for consistency.

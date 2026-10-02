# Work 004 — Agent task workflow

**Objective:** Coordinate Codex and Gemini around small, verifiable subtasks while reducing repeated context reads.

**Current state:** Completed. Cross-agent subtasks now use a reusable contract/handoff file.

**Architecture:** `work/INDEX.md` is navigation only. Each work folder contains concise scope, actionable tasks, decisions, and current notes. Cross-agent tasks get their own contract file based on `work/TASK_TEMPLATE.md`; Gemini receives a direct link in `docs/handoffs.md`.

**Done when:** Project instructions define the read/update workflow, cross-agent task contracts are self-contained, the active work is represented in dedicated folders, and the large task file is only a pointer.

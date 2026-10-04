# Work 014 — Agent Coordination & Task Progress GUI

**Status:** In Progress
**Owner:** Gemini
**Current Task:** [Task 14.01.1](tasks/task-001-task-progress-gui.md)

## Goal

Provide a lightweight, interactive web GUI dashboard to visualize, navigate, and track all work items, subtasks, agent handoffs, and completion progress across the `work/` tracking system.

## Architecture & Principles

1. **Source of Truth**: The files under `work/` (`work/INDEX.md`, each `work/work-*/README.md`, `tasks.md`, `coordination.md`, and `tasks/*.md`) remain the authoritative database. The GUI is a visualization and navigation lens over this repository state.
2. **Zero Extra Dependencies**: Built using standard Python library for parsing and local HTTP serving, and client-side modern JavaScript + allowlisted Tailwind CSS for the user interface.
3. **Dual Delivery**:
   - **Static Dashboard**: A standalone HTML file (`work/dashboard.html`) and conversation artifact viewable in any browser or IDE preview.
   - **Live Local Server**: `python3 scripts/workflow_gui.py --serve` dynamically re-parses `work/` on each request so markdown edits are immediately visible.
4. **Theme Parity**: Adheres to system semantic design tokens (`--background`, `--card`, `--border`, `--foreground`, `--primary`, `--muted-foreground`) for native light and dark mode support.

## Subtasks

- [ ] **14.1** — Work item definition, coordination setup, and metadata schema.
- [ ] **14.2** — Python parser engine to scan `work/INDEX.md`, work folders, `tasks.md`, `coordination.md`, and `tasks/*.md`.
- [ ] **14.3** — Interactive web dashboard with real-time search, status filtering, progress bars, subtask checklists, and task contract viewer.
- [ ] **14.4** — Dual delivery: static HTML generator (`--build`) and live local server (`--serve`).
- [ ] **14.5** — Automated unit test suite in `backend/tests/test_workflow_gui.py`.

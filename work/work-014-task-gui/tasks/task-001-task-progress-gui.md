# Task 14.01.1 — Interactive Agent Coordination & Task Progress GUI

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 014 (Agent Coordination & Task Progress GUI)

## Objective

Build and deliver an interactive web-based dashboard and CLI to visualize the entire `work/` tracking system: list all work items, track completion percentages, navigate individual subtasks and checklists, inspect cross-agent handoffs, and view detailed task contracts. Containerize as a Docker Compose service with live mounted `work/` volume for auto-loading.

## Context and contract

The repository organizes long-lived multi-agent work in `work/INDEX.md` and numbered work folders (`work/work-*/`). Operators and developers need a simple visual overview to track progress, inspect which agent is currently working on what, and navigate directly to task specifications.

## Scope

- In scope:
  - Python parser in `scripts/workflow_gui.py` scanning `work/INDEX.md`, each `work/work-*/` directory, `tasks.md`, `coordination.md`, and individual task contracts.
  - Interactive single-page web GUI with responsive two-column layout, real-time status filtering (All, In Progress, Completed, Pending), search bar, subtask checklists, and task contract viewer.
  - Standalone static HTML generator (`python3 scripts/workflow_gui.py --build`).
  - Embedded local development server (`python3 scripts/workflow_gui.py --serve [--port 8088]`).
  - Docker containerization: `docker/workflow-gui.Dockerfile` and Compose service with live mounted `work/` volume.
  - JSON export mode (`python3 scripts/workflow_gui.py --json`).
  - Unit tests in `backend/tests/test_workflow_gui.py`.
- Out of scope:
  - Adding heavy external web frameworks (Django, React SSR, etc.).
  - Modifying the underlying markdown schema or task contracts in other work folders.

## Dependencies and relevant files

- Inspect/parse:
  - `work/INDEX.md`
  - `work/work-*/README.md`
  - `work/work-*/tasks.md`
  - `work/work-*/coordination.md`
  - `work/work-*/tasks/*.md`
- Create:
  - `scripts/workflow_gui.py`
  - `backend/tests/test_workflow_gui.py`

## Acceptance checks

- [ ] `scripts/workflow_gui.py` accurately parses all active work items and subtasks from disk without error.
- [ ] `./backend/.venv/bin/pytest backend/tests/test_workflow_gui.py` passes all unit tests.
- [ ] `python3 scripts/workflow_gui.py --build` generates `work/dashboard.html` with valid syntax and complete project data.
- [ ] Interactive filtering, search, and contract inspection work smoothly in the GUI across light and dark themes.
- [ ] `python3 scripts/workflow_gui.py --serve` responds with HTTP 200 and live-rendered HTML.

## Handoff back

- Update `work/work-014-task-gui/tasks.md`, `coordination.md`, and `notes.md`.
- Register Work 014 in `work/INDEX.md`.

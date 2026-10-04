# Collaboration guide

## Frontend and backend coordination

- **Frontend Agent**: ChatGPT (UI/UX, pages, client state, components, API client integration)
- **Backend Agent**: Gemini (FastAPI, SQLAlchemy, database, models, migrations, auth, OpenAPI contracts)
- **Implementation & Orchestration**: Codex

The master specification is [SPECIFICATION.md](SPECIFICATION.md). The canonical API contract is [/docs/openapi.yaml](openapi.yaml) and [api-catalogue.md](api-catalogue.md). The [global handoff registry](handoffs.md) links to work-local coordination and task contracts; it is not a second task database. An interactive visual dashboard is available via [Workflow GUI](workflow-gui.md) (`http://localhost:8088`).

Before changing a shared request, response, pricing unit, authentication assumption, or endpoint path, update the contract and note the change in [decisions.md](decisions.md). A completed backend endpoint must be documented with schema and examples before frontend integrates it.

## Before starting work

1. Read `README.md`, [plan.md](plan.md), [TODO.md](TODO.md), and [pending.md](pending.md).
2. Mark one task as `In progress` with your name before editing overlapping files.
3. Check `git status` and preserve unrelated work.

## During work

- Keep each change focused on one task.
- Reuse existing components and theme tokens where appropriate.
- Do not replace approved content or make product decisions without recording them.
- Update related documentation when a decision, system boundary, or task status changes.
- Avoid editing another agent's active files unless coordinated.

## Before handoff

1. Run the relevant validation for the change.
2. For frontend work, verify Chrome/Chromium, Firefox, and mobile rendering using [testing-plan.md](testing-plan.md); mobile is required, not optional.
3. Update the task status and document any limitation in `pending.md`.
4. Add a dated note to `decisions.md` for material decisions.
5. State changed files, validation performed, and any follow-up work.

## Ownership convention

The agent currently working on a task owns the files it changes until it marks the task `Review` or `Done`. If work must overlap, agree on the boundary before editing.

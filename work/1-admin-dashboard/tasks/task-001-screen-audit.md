# Task 1.1 — Figma admin export audit and component inventory

**Owner:** Codex / ChatGPT
**Status:** Pending

## Objective

Inspect the provided Figma admin export, existing components in `src/admin/`, and `/admin` routes to identify exact screens, typography, layout shells, and assets needed for integration without hardcoding dummy data.

## Context and contract

Follow the design in `src/admin/` and the backend contracts in `docs/api-admin.md`. Admin functionality must reflect real database records.

## Scope

- In scope:
  - Inventory existing components in `src/admin/` (`DashboardOverview`, `OrdersTable`, `FinanceView`, `ReturnsQueue`, etc.).
  - Remove extraneous Figma design tokens, demo mock arrays, or hardcoded values.
  - Identify exact screen mapping to current `/admin` routes.
- Out of scope:
  - Modifying backend endpoints or database models.
  - Redesigning the visual theme away from the owner's Figma export.

## Dependencies and relevant files

- Depends on: Backend APIs ready in `docs/api-admin.md`.
- Inspect/edit:
  - `src/admin/`
  - `src/pages/AdminPage.tsx`
  - `docs/api-admin.md`

## Acceptance checks

- [ ] Clear inventory of active and placeholder admin views documented.
- [ ] No hardcoded business analytics or orders remain in UI component bodies.
- [ ] Screen shell aligns with existing `/admin` route structure.

## Handoff back

- Update `work/1-admin-dashboard/tasks.md` and `notes.md`.
- Report findings before wiring live API client calls in Task 1.2/1.3.

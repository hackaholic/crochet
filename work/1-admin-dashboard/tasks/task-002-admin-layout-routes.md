# Task 1.2 — Admin layout shell and route integration

**Owner:** Codex / ChatGPT
**Status:** Pending

## Objective

Integrate the Figma admin layout shell (navigation sidebar, topbar with search/alerts, and responsive main canvas) into the existing `/admin` route without replacing it with an incompatible layout or breaking route authentication guards.

## Context and contract

The `/admin` route is guarded by admin authentication checks. The shell must house sub-navigation for Dashboard, Orders, Finance, Returns, Catalog/Occasions, and Settings cleanly.

## Scope

- In scope:
  - Responsive desktop/tablet sidebar and header.
  - Active navigation state indicator.
  - Integration with React Router navigation under `/admin`.
  - Admin sign-out and profile dropdown.
- Out of scope:
  - Re-implementing authentication session cookies.

## Dependencies and relevant files

- Depends on: Task 1.1 audit.
- Inspect/edit:
  - `src/pages/AdminPage.tsx`
  - `src/admin/components/AdminLayout.tsx`
  - `src/App.tsx`

## Acceptance checks

- [ ] `/admin` loads the integrated Figma layout with responsive sidebar and header.
- [ ] Navigation switches between views without full-page reloads.
- [ ] Unauthorized visitors redirect to login; authorized admins can navigate freely.

## Handoff back

- Update `work/1-admin-dashboard/tasks.md` and `notes.md`.

# Task 1.4 — Admin UI automated tests and Docker verification

**Owner:** Codex / ChatGPT
**Status:** Pending

## Objective

Add and update comprehensive frontend unit/integration tests for the integrated admin views, run the frontend test suite, and verify functionality in the live local Docker container stack at `http://localhost:8080/admin`.

## Context and contract

Follow the project working rules:
- Verify changes locally first in Docker.
- Run `pnpm test` and `pnpm typecheck`.
- Confirm visual fidelity and responsiveness in the browser matrix (Chrome, mobile widths).

## Scope

- In scope:
  - Vitest test coverage for `AdminPage.test.tsx` and admin subcomponents.
  - Mock API tests for loading, empty, and error states.
  - End-to-end admin inspection on `http://localhost:8080/admin`.
- Out of scope:
  - Altering backend test suites.

## Dependencies and relevant files

- Depends on: Task 1.3 API integration.
- Inspect/edit:
  - `src/pages/AdminPage.test.tsx`
  - `src/admin/**/*.test.tsx`
  - `docker/compose.yaml`

## Acceptance checks

- [ ] `npm test` passes all tests with zero type errors (`pnpm typecheck`).
- [ ] Admin dashboard renders without console errors on `http://localhost:8080/admin`.
- [ ] Verification recorded in `notes.md` with screenshot/evidence before marking complete.

## Handoff back

- Mark Work 001 completed in `work/INDEX.md` and `work/1-admin-dashboard/tasks.md`.

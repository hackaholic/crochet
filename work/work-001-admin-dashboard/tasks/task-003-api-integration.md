# Task 1.3 — Admin API client integration and state management

**Owner:** Codex / ChatGPT
**Status:** Pending

## Objective

Connect all admin views to real backend API endpoints using typed client methods in `src/lib/api/admin.ts`. Replace placeholder data with real persisted database data, and implement explicit loading, empty, and error states.

## Context and contract

Refer to `docs/api-admin.md` for exact request/response schemas.
Key endpoints:
- `GET /api/v1/admin/dashboard/summary` & `GET /api/v1/admin/dashboard/sales`
- `GET /api/v1/admin/finance/summary` & `GET /api/v1/admin/finance/sales`
- `GET /api/v1/admin/dashboard/attention` & `GET /api/v1/admin/search`
- `GET /api/v1/admin/orders` (with filters)
- `GET /api/v1/admin/returns`, status update, and refund dispatch
- `GET /api/v1/admin/occasions` and CRUD operations

## Scope

- In scope:
  - Connect dashboard metrics cards and sales charts to live APIs.
  - Wire up orders table with pagination, search, and status filters.
  - Connect finance breakdown cards and net revenue trends.
  - Implement return requests review and refund modal.
  - Connect occasion manager for holiday/seasonal scheduling.
  - Graceful handling of empty states, network latency, and HTTP errors.
- Out of scope:
  - Fabricating synthetic data or statutory tax deductions on the client side.

## Dependencies and relevant files

- Depends on: Task 1.2 layout shell; backend endpoints verified in `docs/api-admin.md`.
- Inspect/edit:
  - `src/lib/api/admin.ts`
  - `src/admin/`
  - `src/pages/AdminPage.tsx`

## Acceptance checks

- [ ] All views render real data returned from the backend.
- [ ] Dates and financial metrics display in `Asia/Kolkata` time and INR paise currency formatting (`₹`).
- [ ] Refunds and status updates trigger API mutations and refresh views upon completion.
- [ ] Zero orders/returns render dedicated empty states rather than broken tables.

## Handoff back

- Update `work/work-001-admin-dashboard/tasks.md` and `notes.md`.

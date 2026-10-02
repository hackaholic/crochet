# Work 001 tasks

## In Progress

- [ ] 1.6 Verify the integrated admin in local Docker/browser, including API-backed data, error/empty/mutation states, and desktop/mobile rendering; record defects before marking the integration accepted.

## Pending

- [ ] 1.7 Replace the Products placeholder with a reusable catalogue screen using existing product/variant APIs; cover create/edit/list behavior with tests.
- [ ] 1.8 Replace the Inventory placeholder using existing inventory/adjustment APIs; cover safe stock adjustments and feedback with tests.
- [ ] 1.9 Define the minimum useful Customers screen and audit existing customer APIs; write a Gemini contract before adding backend capability.
- [ ] 1.10 Define which Settings belong in V1 and audit existing admin APIs; write a separate Gemini contract before adding backend capability.
- [ ] 1.12 Owner reviews the locally verified admin experience and decides whether any additional sections or visual changes are required; only then consider a dev push/deploy.

## Completed

- [x] 1.1 Inspect the provided `/home/anu/Downloads/admin.zip` export and current implementation. The source includes a `mockData.ts`; it is not present in the app runtime. The supplied shell, dashboard, orders, order detail, finance, returns, and placeholder page structure exists under `src/admin/`.
- [x] 1.2 Integrate the supplied admin layout/navigation into the existing `/admin` route without replacing it with a new design.
- [x] 1.3 Wire the implemented dashboard, orders/order detail, finance, and returns screens to typed API service calls; retain loading/empty states and remove prototype records from runtime rendering.
- [x] 1.4 Keep the admin route behind an administrator access check with sign-in, loading, and API error states.
- [x] 1.5 Gemini reports the dashboard metrics, sales/finance, attention/search, order filters, and return/refund backend contracts implemented; see the dated backend completion handoff in `docs/handoffs.md` (126 backend tests reported there).

## Blocked

- [ ] 1.11 Add screen-level UI tests for the dashboard, order list/detail, finance, returns, and any newly implemented pages; run the suite in the supported Node/Docker environment. Current host Node cannot start Vitest, and the direct backend test attempt yielded no result.
- Frontend test run on the host is blocked by the installed Node runtime: Vitest/Rolldown imports `node:util.styleText`, which this Node version does not provide. Run tests using the project's supported Node version/container.
- A direct run of `backend/tests/test_admin_dashboard.py` produced no result before it was interrupted; backend tests need rerunning in the project Docker/test environment before acceptance.

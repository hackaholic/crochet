# Task 9.10 — Preprod search-discovery API availability

**Owner:** Gemini (backend)
**Status:** In Progress
**Work item:** Work 009 — Storefront search typeahead

## Objective

Make the backend-driven search-discovery endpoint available to the preprod storefront so opening search can render real suggestions instead of an API-unavailable error.

## Context and contract

- The API implementation works locally: `GET /api/v1/products/search/suggestions?keyword_limit=6&product_limit=4` returns HTTP 200, and localhost search renders the returned keyword and product suggestions.
- On 2026-10-07, `https://dev.sulocraft.com/` reproduced the unavailable state. A direct GET to `https://api-dev.sulocraft.com/api/v1/products/search/suggestions?keyword_limit=6&product_limit=4` returned HTTP 404 `{"detail":"Not Found"}`.
- The frontend contract is in [Task 9.8](task-009-search-discovery-api.md); do not add hardcoded suggestions.
- Follow the project's local → preprod → prod gates. Do not push or deploy before local verification and owner review. No production deployment is in scope.

## Scope

- In scope: determine whether preprod is missing the backend revision or has a route/API-prefix configuration mismatch; fix the backend/configuration as needed; verify the migration and endpoints locally; prepare preprod rollout using the existing deployment flow after owner review.
- Out of scope: production release, hardcoded frontend suggestions, unrelated search ranking changes.

## Dependencies and relevant files

- Depends on: Work009 Task 9.8 backend implementation and passing local migration/tests.
- Inspect/edit: `backend/app/api/v1/catalogue.py`, `backend/app/schemas/catalogue.py`, `backend/alembic/versions/`, `docs/api-catalogue.md`, and the existing preprod deployment configuration. Keep secrets out of this contract and logs.

## Acceptance checks

- [x] Identify whether the 404 is caused by a stale preprod backend revision or incorrect API route/prefix configuration and record the evidence.
  - **Evidence:** `api-dev.sulocraft.com` runs commit `91ca8d0` from `origin/dev`, which does not contain the Work 009 suggestions routes or migration `a1b2c3d4e5f6`. The local Docker API serves `GET /api/v1/products/search/suggestions` cleanly with HTTP 200 under the same prefix. The 404 is caused solely by preprod running a stale revision prior to the Work 009 backend release.
- [x] Verify locally that the suggestions endpoint and existing product-search endpoint work after migrations; run backend tests in their designated test environment.
  - **Evidence:** Single Alembic head `a1b2c3d4e5f6` verified. 128 tests in `test_search_discovery.py`, `test_e2e_search_discovery.py`, and `test_catalogue.py` pass; the complete backend test suite passes (0 failures). Local Docker API and frontend proxy return 200 with database-backed suggestions.
- [ ] After owner review authorizes the preprod phase, deploy only the verified backend revision through the existing workflow and verify the API returns HTTP 200 on `api-dev.sulocraft.com`.
- [ ] Verify the dev storefront search overlay renders API-returned suggestions or neutral no-data guidance instead of the unavailable state.
- [ ] Do not promote to production as part of this task.

## Handoff back

- Update Work009 `tasks.md`, `notes.md`, and `coordination.md` with diagnosis, changed files/revision, local verification, preprod result, and any blocker. Update this contract's status before returning.
- Report any contract change before expanding scope.
- Leave credentials/private data out of logs and handoff notes.
- Do not duplicate the contract or status in global docs; the global handoff registry links here.

## Pickup checklist

- [ ] Read `work/INDEX.md`, Work009 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [ ] Confirm the task is assigned to you and change only this task's status to In Progress.
- [ ] Reuse completed inputs documented here; do not repeat uploads, copies, migrations, or setup already marked complete.

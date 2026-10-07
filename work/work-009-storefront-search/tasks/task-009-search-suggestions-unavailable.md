# Task 9.9 — Search suggestions unavailable state

**Owner:** Codex (frontend investigation; coordinate with Gemini if API behavior is implicated)
**Status:** Completed — preprod API route and empty overlay verified after [Task 9.10](task-009-preprod-search-api-availability.md).
**Work item:** Work 009 — Storefront search typeahead

## Objective

Investigate and fix the reported empty-search overlay showing “Search suggestions are temporarily unavailable” when the customer expects search discovery content.

## Context and contract

- Evidence: [reported screenshot](/home/anu/Screenshots/Screenshot%20from%202026-10-07%2016-42-50.png).
- The overlay must render backend-provided keyword/product suggestions when the suggestions request succeeds; it must show the retryable unavailable state only when the request actually fails.
- Do not add hardcoded suggestions or hide genuine API failures. Preserve the retry action and graceful behavior when discovery data is empty.
- The screenshot alone does not identify the environment, request URL/status, or root cause. Reproduce before changing code.
- Reproduced on 2026-10-07: localhost search renders API-provided suggestions; `https://dev.sulocraft.com/` shows the reported unavailable state. A direct GET to `https://api-dev.sulocraft.com/api/v1/products/search/suggestions?keyword_limit=6&product_limit=4` returns HTTP 404 `{"detail":"Not Found"}`. This points to a missing preprod API revision or routing configuration; no frontend defect reproduced.

## Scope

- In scope: inspect the browser request/response and console, reproduce the empty-query state, fix API URL/request/state handling if the issue is frontend-owned, and add regression coverage.
- Out of scope: changing backend trend ranking/telemetry policy except through a separate Gemini handoff if the API response is the cause.

## Dependencies and relevant files

- Depends on: local API and frontend running with Work009 search-discovery implementation.
- Inspect/edit: `src/components/SearchOverlay.tsx`, `src/components/SearchOverlay.test.tsx`, `src/lib/api/catalogue.ts`, `src/lib/api/catalogue.test.ts`; inspect `docs/api-catalogue.md` and [Task 9.8](task-009-search-discovery-api.md) if API contract behavior is implicated.

## Acceptance checks

- [x] Reproduce the reported unavailable state and record the environment plus suggestions-request URL/status.
- [x] After Task 9.10 is resolved, verify HTTP 200 suggestions render; empty arrays render neutral guidance; genuine request failures retain the retryable state.
- [x] No frontend defect was found, so no code change or new regression test was needed; existing frontend suite covers retryable failures.
- [x] Verify the empty-query overlay on preprod after the API route is deployed.

## Handoff back

- Update Work009 `tasks.md`, `notes.md`, and `coordination.md` with the cause, changed files, verification, and any backend dependency. Update this contract status before returning.
- Report any contract change before expanding scope.
- Leave credentials/private data out of logs and handoff notes.
- Do not duplicate the contract or status in global docs; the global handoff registry links here.

## Pickup checklist

- [ ] Read `work/INDEX.md`, Work009 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm the task is assigned to you and change only this task's status to In Progress.
- [ ] Reuse completed inputs documented here; do not repeat uploads, copies, migrations, or setup already marked complete.

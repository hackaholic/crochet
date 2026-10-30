# Task 26.2 — Make local Compose configuration explicit and repeatable

**Owner:** Codex  
**Status:** Completed  
**Work item:** Work 026

## Objective

Make local Docker startup consistently read the ignored local `.env` for backend runtime settings, without depending on frontend Vite OAuth variables.

## Context and contract

- Follow Work 026 README/tasks/decisions and [26.1](task-001-api-runtime-oauth-config.md).
- Local credentials stay in the developer's ignored `.env` or an explicitly selected local SOPS runtime overlay; `.env.preprod` is not the local OAuth secret source.
- Backend consumers use the shared env/`*_FILE` config resolver. Do not add secret values to Compose YAML or docs.

## Scope

- In scope: one documented/reusable local Compose entry point or command, explicit env-file handling, and local configuration tests.
- Out of scope: modifying preprod/prod deployment artifacts or changing local mock payments.

## Dependencies and relevant files

- Depends on: [26.1](task-001-api-runtime-oauth-config.md)
- Dependency context: Frontend OAuth no longer requires Vite variables.
- Blocked by: None
- Blocker reason: None
- Next action: Inspect existing local scripts and select the smallest explicit `.env` Compose invocation; add verification for the API config without exposing the value.
- Inspect/edit: `docker/compose.yaml`, local startup documentation/scripts, `.env.example`, and focused config tests.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 26.2-TC01 | Local `.env` reaches backend | Success | Start local API with `docker-compose --env-file .env -f docker/compose.yaml up -d --build frontend` | `/api/v1/auth/config` reports configured without printing ID | Local Docker/API smoke check | PASS; ID present, no value logged |
| 26.2-TC02 | Empty local OAuth config is safe | Failure | Run component test with null runtime config | API response remains null; frontend explains provider unavailable without a Vite instruction | `AuthModal.test.tsx` | PASS, 6/6 |
| 26.2-TC03 | Local OAuth config stays out of frontend env | Security | Inspect running frontend env | Vite Google ID is absent; frontend resolves it from API | Docker env audit | PASS; Vite Google ID absent |

## Security validation

- Changed assets/trust boundaries and plausible abuse: Local developer secrets flow into the API container; only public OAuth identifiers may be returned to browsers.
- Applicable controls and linked negative test IDs: Explicit allowlisted Compose settings, ignored local env files, TC02 fail-safe behavior, and TC03 bundle/env boundary.
- Commands/target/results and evidence (redacted): Local Compose rebuilt using explicit ignored `.env`; API `/api/v1/auth/config` reported Google ID present; frontend Vite Google ID absent; storefront HTTP 200; focused tests 6/6 and `pnpm typecheck` pass.
- Disposition: Pass.
- Findings, severity, remediation owner, and blockers: None known.

## Acceptance checks

- [x] Local startup has one clear command that explicitly loads local config; documented in `docs/secrets.md`.
- [x] API runtime config is populated from backend config; frontend Vite OAuth variables are unnecessary.
- [x] Relevant checks and security validation pass and are recorded.
- [x] Peer review is accurately identified as Codex self-review.

## Handoff back

- Update this contract and Work 026 state files with the exact local command and test evidence.
- Do not put secret values in logs or documentation. Do not deploy.

## Pickup checklist

- [ ] Read Work 026 context and Task 26.1 return.
- [ ] Confirm ownership and mark only this task In Progress.
- [ ] Reuse local config existing in ignored `.env`; do not repeat credential setup.

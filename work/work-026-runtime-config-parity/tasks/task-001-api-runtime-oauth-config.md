# Task 26.1 — Use API runtime configuration for OAuth in the frontend

**Owner:** Codex  
**Status:** Completed  
**Work item:** Work 026

## Objective

Use the existing backend `/api/v1/auth/config` endpoint as the only frontend source for Google/Facebook public OAuth identifiers. Remove the obsolete Vite build-time path and user-facing instruction to set `VITE_GOOGLE_CLIENT_ID`.

## Context and contract

- Follow Work 026 `README.md`, `tasks.md`, `decisions.md`, and `coordination.md`.
- Backend auth config already resolves its ID from environment or `*_FILE` and returns only public provider identifiers.
- Preprod/prod SOPS runtime path wiring is tracked separately in [26.3](task-003-sops-oauth-runtime-parity.md); do not modify those deployment files in this task.
- Preserve the existing provider flows and UI design. Show a neutral unavailable message if runtime config cannot be loaded; never tell operators to configure a Vite variable.

## Scope

- In scope: AuthModal runtime config loading/error/loading behavior, remove Vite OAuth client ID usage from frontend source/Compose/example configuration, and focused frontend tests.
- Out of scope: changing OAuth verification, credentials, Google Cloud origins, session/logout behavior, or deployment.

## Dependencies and relevant files

- Depends on: None
- Dependency context: Existing backend `GET /api/v1/auth/config` implementation is present and returns public IDs from backend settings.
- Blocked by: None
- Blocker reason: None
- Next action: Remove Vite fallback, add focused tests for runtime config loading and missing config, then locally verify.
- Inspect/edit: `src/components/AuthModal.tsx`, `src/components/AuthModal.test.tsx`, `docker/compose.yaml`, `.env.example`.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 26.1-TC01 | API runtime ID initializes Google | Success | Open auth modal with `/auth/config` returning Google client ID; click Google | Provider token client uses API-returned ID and no Vite variable | `./scripts/test.sh frontend pnpm exec vitest run src/components/AuthModal.test.tsx` | PASS, 6/6 |
| 26.1-TC02 | Config loading does not show a false missing-config error | Regression | Open modal while config request is pending and activate Google | Social buttons stay disabled until config resolves | Focused component test | PASS, 6/6 |
| 26.1-TC03 | Missing config is safe and understandable | Failure | API returns null ID; click Google/Facebook | No provider call; neutral message contains no build-variable instructions | Focused component test | PASS, 6/6 |
| 26.1-TC04 | No frontend build-time OAuth setting remains | Security | Inspect frontend source/config and running container | OAuth IDs are obtained at runtime; frontend Vite OAuth variables are absent | `rg` audit + Docker env check | PASS; Vite Google ID absent from frontend |

## Security validation

- Changed assets/trust boundaries and plausible abuse: Public OAuth IDs cross API-to-browser at runtime; private provider credentials must remain backend-only. A malformed/unavailable config must not invoke the provider with an empty ID.
- Applicable controls and linked negative test IDs: Runtime config is an allowlisted response of public IDs only; TC03 verifies missing config fails safely; TC04 verifies no private credential or frontend build-time injection.
- Commands/target/results and evidence (redacted): Focused frontend tests 6/6; `pnpm typecheck` passed; Docker frontend rebuilt with local `.env`, backend config endpoint reported Google ID present, frontend Vite Google variable absent, storefront HTTP 200; `git diff --check` passed.
- Disposition: Pass.
- Findings, severity, remediation owner, and blockers: None known.

## Acceptance checks

- [x] Frontend reads OAuth IDs only through `/api/v1/auth/config`.
- [x] No UI error advises setting a Vite variable.
- [x] Focused tests and typecheck pass; local API/UI runtime config is verified.
- [x] Test/security evidence is recorded; no unresolved checks are hidden.
- [x] Peer review recorded as Codex self-review.

## Handoff back

- Update this contract, Work 026 `tasks.md`, `notes.md`, and `coordination.md` with changed files and exact verification.
- Do not edit SOPS/deploy runtime mapping here; return those requirements to Task 26.3.
- Do not push or deploy.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 026 README/tasks/decisions/coordination, and this contract.
- [x] Confirm ownership and mark only this task In Progress.
- [x] Reuse the existing API config endpoint; do not repeat OAuth setup or credential entry.

# Task 9.11 — Paginated search API

**Owner:** Gemini
**Status:** Pending
**Work item:** Work 009
**Work owner:** Codex

## Objective

Extend public GET /api/v1/products/search with offset pagination while preserving its existing array response. Keep limit 1–50, add offset >= 0 (default 0), and order by reviews_count DESC then product id ASC. Existing callers remain compatible.
Dependencies: No implementation prerequisite; existing search endpoint available.
Blockers: None reported at planning; prerequisites must be verified at pickup.

## Context and contract

Read ../README.md, ../decisions.md, ../coordination.md and work/GEMINI_WORKFLOW_PROMPT.md before backend pickup. Preserve environment parity and existing completed features. Record uncertainty instead of guessing business facts.

## Scope

- In scope: Extend public GET /api/v1/products/search with offset pagination while preserving its existing array response. Keep limit 1–50, add offset >= 0 (default 0), and order by reviews_count DESC then product id ASC. Existing callers remain compatible.
- Out of scope: Production deployment, unrelated refactors, fabricated product claims, changing existing rate limits without an agreed contract.

## Dependencies and relevant files

- Depends on: No implementation prerequisite; existing search endpoint available.
- Inspect/edit: backend/app/api/v1/catalogue.py; backend/tests; docs/api-catalogue.md
- Readiness: Planning complete; implementation evidence pending.
- Blocker protocol: Record exact missing input and owner here and in coordination.md; ask the user about ambiguous product/image classification.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 9.11-TC1 | Pages over a fixture with more than two batches return all active matches once; tied rankings use deterministic order. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 9.11-TC2 | Default request remains compatible; negative offset and invalid limit return 422; an exhausted page returns []. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 9.11-TC3 | Search matches names, descriptions, tags and categories; inactive products remain excluded; SQL-like input is handled safely. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 9.11-TC4 | Existing rate/telemetry controls are preserved; pagination GETs do not ingest additional telemetry. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |

## Security validation

- Use existing authorization, parameterized ORM queries, bounded requests and public response schemas. Do not expose draft products, customer records or secrets.
- Taxonomy writes require explicit target environment, a dry-run diff, narrow updates and a rollback plan; never reset the database.
- Test applicable invalid input, unauthorized mutation and inactive-product exclusion. Documentation-only planning introduces no application trust-boundary change.
- Disposition: Implementation validation pending.

## Acceptance checks

- [ ] Pages over a fixture with more than two batches return all active matches once; tied rankings use deterministic order.
- [ ] Default request remains compatible; negative offset and invalid limit return 422; an exhausted page returns [].
- [ ] Search matches names, descriptions, tags and categories; inactive products remain excluded; SQL-like input is handled safely.
- [ ] Existing rate/telemetry controls are preserved; pagination GETs do not ingest additional telemetry.
- [ ] Tests and security evidence recorded; self-review or independent review identified accurately.
- [ ] Changed behavior verified locally in Docker/API and browser before any push or preprod deployment.

## Handoff back

Update this contract, tasks.md, notes.md and coordination.md with status, changed files, exact tests/results, dependencies, blockers and next owner. Return to Codex for integration. Keep the global registry as links only. Do not push/deploy as part of this task without the release gate.

## Pickup checklist

- [ ] Read work/INDEX.md and this selected work folder/contract.
- [ ] Confirm ownership and prerequisites; mark only this task In Progress.
- [ ] Reuse verified existing assets and URLs; no repeat uploads or placeholder copies.

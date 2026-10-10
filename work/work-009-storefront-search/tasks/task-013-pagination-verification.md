# Task 9.13 — Local paginated search acceptance

**Owner:** Codex
**Status:** Pending
**Work item:** Work 009
**Work owner:** Codex

## Objective

Verify paginated search in rebuilt local frontend/API services with a known multi-page catalogue fixture and record browser/API evidence.
Dependencies: Tasks 9.11 and 9.12 completed.
Blockers: None reported at planning; prerequisites must be verified at pickup.

## Context and contract

Read ../README.md, ../decisions.md, ../coordination.md and work/GEMINI_WORKFLOW_PROMPT.md before backend pickup. Preserve environment parity and existing completed features. Record uncertainty instead of guessing business facts.

## Scope

- In scope: Verify paginated search in rebuilt local frontend/API services with a known multi-page catalogue fixture and record browser/API evidence.
- Out of scope: Production deployment, unrelated refactors, fabricated product claims, changing existing rate limits without an agreed contract.

## Dependencies and relevant files

- Depends on: Tasks 9.11 and 9.12 completed.
- Inspect/edit: Docker configuration; SearchOverlay tests; work-local notes
- Readiness: Planning complete; implementation evidence pending.
- Blocker protocol: Record exact missing input and owner here and in coordination.md; ask the user about ambiguous product/image classification.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 9.13-TC1 | Relevant API/frontend tests pass using multi-page data; existing discovery and rate-limit behavior regressions pass. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 9.13-TC2 | Chrome, Firefox and mobile viewport checks confirm usable scrolling, keyboard navigation, stable results and image rendering. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 9.13-TC3 | Local API/browser evidence recorded before release; unavailable browsers or checks are documented as blockers rather than claimed passed. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |

## Security validation

- Use existing authorization, parameterized ORM queries, bounded requests and public response schemas. Do not expose draft products, customer records or secrets.
- Taxonomy writes require explicit target environment, a dry-run diff, narrow updates and a rollback plan; never reset the database.
- Test applicable invalid input, unauthorized mutation and inactive-product exclusion. Documentation-only planning introduces no application trust-boundary change.
- Disposition: Implementation validation pending.

## Acceptance checks

- [ ] Relevant API/frontend tests pass using multi-page data; existing discovery and rate-limit behavior regressions pass.
- [ ] Chrome, Firefox and mobile viewport checks confirm usable scrolling, keyboard navigation, stable results and image rendering.
- [ ] Local API/browser evidence recorded before release; unavailable browsers or checks are documented as blockers rather than claimed passed.
- [ ] Tests and security evidence recorded; self-review or independent review identified accurately.
- [ ] Changed behavior verified locally in Docker/API and browser before any push or preprod deployment.

## Handoff back

Update this contract, tasks.md, notes.md and coordination.md with status, changed files, exact tests/results, dependencies, blockers and next owner. Return to Codex for integration. Keep the global registry as links only. Do not push/deploy as part of this task without the release gate.

## Pickup checklist

- [ ] Read work/INDEX.md and this selected work folder/contract.
- [ ] Confirm ownership and prerequisites; mark only this task In Progress.
- [ ] Reuse verified existing assets and URLs; no repeat uploads or placeholder copies.

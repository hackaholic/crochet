# Task 16.3 — Local storefront taxonomy verification

**Owner:** Codex
**Status:** Pending
**Work item:** Work 016
**Work owner:** Codex

## Objective

Check corrected products through local catalogue/search/filter APIs and storefront category and occasion views; reconcile the inventory report with rendered results.
Dependencies: Task 16.2 returned with correction/test evidence; uncertain cases resolved or explicitly blocked.
Blockers: None reported at planning; prerequisites must be verified at pickup.

## Context and contract

Read ../README.md, ../decisions.md, ../coordination.md and work/GEMINI_WORKFLOW_PROMPT.md before backend pickup. Preserve environment parity and existing completed features. Record uncertainty instead of guessing business facts.

## Scope

- In scope: Check corrected products through local catalogue/search/filter APIs and storefront category and occasion views; reconcile the inventory report with rendered results.
- Out of scope: Production deployment, unrelated refactors, fabricated product claims, changing existing rate limits without an agreed contract.

## Dependencies and relevant files

- Depends on: Task 16.2 returned with correction/test evidence; uncertain cases resolved or explicitly blocked.
- Inspect/edit: src/components storefront filters; local Docker services; this work report/notes
- Readiness: Planning complete; implementation evidence pending.
- Blocker protocol: Record exact missing input and owner here and in coordination.md; ask the user about ambiguous product/image classification.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 16.3-TC1 | Local API mappings match approved report; known products appear in correct filters and relevant search results. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 16.3-TC2 | Actual local storefront images and names match the product mapping on desktop/mobile; empty categories are legitimate or reported. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 16.3-TC3 | Record exact checks, unresolved user questions and release readiness; do not mark the entire audit complete while classifications remain unresolved. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |

## Security validation

- Use existing authorization, parameterized ORM queries, bounded requests and public response schemas. Do not expose draft products, customer records or secrets.
- Taxonomy writes require explicit target environment, a dry-run diff, narrow updates and a rollback plan; never reset the database.
- Test applicable invalid input, unauthorized mutation and inactive-product exclusion. Documentation-only planning introduces no application trust-boundary change.
- Disposition: Implementation validation pending.

## Acceptance checks

- [ ] Local API mappings match approved report; known products appear in correct filters and relevant search results.
- [ ] Actual local storefront images and names match the product mapping on desktop/mobile; empty categories are legitimate or reported.
- [ ] Record exact checks, unresolved user questions and release readiness; do not mark the entire audit complete while classifications remain unresolved.
- [ ] Tests and security evidence recorded; self-review or independent review identified accurately.
- [ ] Changed behavior verified locally in Docker/API and browser before any push or preprod deployment.

## Handoff back

Update this contract, tasks.md, notes.md and coordination.md with status, changed files, exact tests/results, dependencies, blockers and next owner. Return to Codex for integration. Keep the global registry as links only. Do not push/deploy as part of this task without the release gate.

## Pickup checklist

- [ ] Read work/INDEX.md and this selected work folder/contract.
- [ ] Confirm ownership and prerequisites; mark only this task In Progress.
- [ ] Reuse verified existing assets and URLs; no repeat uploads or placeholder copies.

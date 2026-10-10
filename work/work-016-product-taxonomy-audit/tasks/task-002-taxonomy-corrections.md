# Task 16.2 — Apply approved classification corrections

**Owner:** Gemini
**Status:** Pending
**Work item:** Work 016
**Work owner:** Codex

## Objective

Implement a narrow idempotent update mechanism for confirmed product category/tag/occasion mappings. Store the approved mapping and dry-run diff in this work; use environment/config inputs to select the target. Provide rollback data for changed associations.
Dependencies: Task 16.1 returned; user answers required for ambiguous products. Confirmed products can proceed independently; unresolved ones remain documented.
Blockers: None reported at planning; prerequisites must be verified at pickup.

## Context and contract

Read ../README.md, ../decisions.md, ../coordination.md and work/GEMINI_WORKFLOW_PROMPT.md before backend pickup. Preserve environment parity and existing completed features. Record uncertainty instead of guessing business facts.

## Scope

- In scope: Implement a narrow idempotent update mechanism for confirmed product category/tag/occasion mappings. Store the approved mapping and dry-run diff in this work; use environment/config inputs to select the target. Provide rollback data for changed associations.
- Out of scope: Production deployment, unrelated refactors, fabricated product claims, changing existing rate limits without an agreed contract.

## Dependencies and relevant files

- Depends on: Task 16.1 returned; user answers required for ambiguous products. Confirmed products can proceed independently; unresolved ones remain documented.
- Inspect/edit: backend/app/db/seed.py or existing maintenance mechanism; backend/tests/test_taxonomy.py; task 16.1 report
- Readiness: Planning complete; implementation evidence pending.
- Blocker protocol: Record exact missing input and owner here and in coordination.md; ask the user about ambiguous product/image classification.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 16.2-TC1 | Dry run lists exact association changes; second execution makes no further changes. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 16.2-TC2 | Each confirmed product appears in its intended category/tag/occasion queries and never in an incorrect group. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 16.2-TC3 | Uncertain products are skipped pending user feedback; SKU/id, prices, stock, orders and image URLs remain intact. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 16.2-TC4 | Correction/rollback tests use isolated data and explicit environment selection; no unauthorized database writes. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |

## Security validation

- Use existing authorization, parameterized ORM queries, bounded requests and public response schemas. Do not expose draft products, customer records or secrets.
- Taxonomy writes require explicit target environment, a dry-run diff, narrow updates and a rollback plan; never reset the database.
- Test applicable invalid input, unauthorized mutation and inactive-product exclusion. Documentation-only planning introduces no application trust-boundary change.
- Disposition: Implementation validation pending.

## Acceptance checks

- [ ] Dry run lists exact association changes; second execution makes no further changes.
- [ ] Each confirmed product appears in its intended category/tag/occasion queries and never in an incorrect group.
- [ ] Uncertain products are skipped pending user feedback; SKU/id, prices, stock, orders and image URLs remain intact.
- [ ] Correction/rollback tests use isolated data and explicit environment selection; no unauthorized database writes.
- [ ] Tests and security evidence recorded; self-review or independent review identified accurately.
- [ ] Changed behavior verified locally in Docker/API and browser before any push or preprod deployment.

## Handoff back

Update this contract, tasks.md, notes.md and coordination.md with status, changed files, exact tests/results, dependencies, blockers and next owner. Return to Codex for integration. Keep the global registry as links only. Do not push/deploy as part of this task without the release gate.

## Pickup checklist

- [ ] Read work/INDEX.md and this selected work folder/contract.
- [ ] Confirm ownership and prerequisites; mark only this task In Progress.
- [ ] Reuse verified existing assets and URLs; no repeat uploads or placeholder copies.

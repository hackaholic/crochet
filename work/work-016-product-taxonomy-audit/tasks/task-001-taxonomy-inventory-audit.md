# Task 16.1 — Inventory and classification report

**Owner:** Gemini
**Status:** Pending
**Work item:** Work 016
**Work owner:** Codex

## Objective

Produce an exhaustive product-to-category/tag/occasion report from the local database with id, SKU where available, slug, image URL, current mapping, proposed mapping, rationale and confidence. Include untagged, inactive and duplicate-association cases. Ask the user about ambiguous images/products before dependent corrections.
Dependencies: Existing local database and schema; use current taxonomy, not a new invented taxonomy.
Blockers: None reported at planning; prerequisites must be verified at pickup.

## Context and contract

Read ../README.md, ../decisions.md, ../coordination.md and work/GEMINI_WORKFLOW_PROMPT.md before backend pickup. Preserve environment parity and existing completed features. Record uncertainty instead of guessing business facts.

## Scope

- In scope: Produce an exhaustive product-to-category/tag/occasion report from the local database with id, SKU where available, slug, image URL, current mapping, proposed mapping, rationale and confidence. Include untagged, inactive and duplicate-association cases. Ask the user about ambiguous images/products before dependent corrections.
- Out of scope: Production deployment, unrelated refactors, fabricated product claims, changing existing rate limits without an agreed contract.

## Dependencies and relevant files

- Depends on: Existing local database and schema; use current taxonomy, not a new invented taxonomy.
- Inspect/edit: backend/app/models/catalogue.py; backend/app/db/seed.py; backend/tests/test_taxonomy.py; this work notes/report
- Readiness: Planning complete; implementation evidence pending.
- Blocker protocol: Record exact missing input and owner here and in coordination.md; ask the user about ambiguous product/image classification.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 16.1-TC1 | Report covers every product exactly once and includes untagged products; counts reconcile to the database. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 16.1-TC2 | Current and proposed category/tag/occasion mappings are explicit; existing image URLs are reused. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 16.1-TC3 | Ambiguous products are identified by id/SKU and image with a concise question for the user; no uncertain mapping is applied. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |

## Security validation

- Use existing authorization, parameterized ORM queries, bounded requests and public response schemas. Do not expose draft products, customer records or secrets.
- Taxonomy writes require explicit target environment, a dry-run diff, narrow updates and a rollback plan; never reset the database.
- Test applicable invalid input, unauthorized mutation and inactive-product exclusion. Documentation-only planning introduces no application trust-boundary change.
- Disposition: Implementation validation pending.

## Acceptance checks

- [ ] Report covers every product exactly once and includes untagged products; counts reconcile to the database.
- [ ] Current and proposed category/tag/occasion mappings are explicit; existing image URLs are reused.
- [ ] Ambiguous products are identified by id/SKU and image with a concise question for the user; no uncertain mapping is applied.
- [ ] Tests and security evidence recorded; self-review or independent review identified accurately.
- [ ] Changed behavior verified locally in Docker/API and browser before any push or preprod deployment.

## Handoff back

Update this contract, tasks.md, notes.md and coordination.md with status, changed files, exact tests/results, dependencies, blockers and next owner. Return to Codex for integration. Keep the global registry as links only. Do not push/deploy as part of this task without the release gate.

## Pickup checklist

- [ ] Read work/INDEX.md and this selected work folder/contract.
- [ ] Confirm ownership and prerequisites; mark only this task In Progress.
- [ ] Reuse verified existing assets and URLs; no repeat uploads or placeholder copies.

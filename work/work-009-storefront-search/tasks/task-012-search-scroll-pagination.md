# Task 9.12 — Scroll to load search batches

**Owner:** Codex
**Status:** Pending
**Work item:** Work 009
**Work owner:** Codex

## Objective

Add offset support to the typed search client and append batches of six when the results panel approaches its bottom. Only one page request per query may run at once. Stop after a short/empty batch; deduplicate by id. A full final batch may require one final empty fetch. Reset results, offset, scroll and cancellation when query changes or dialog closes.
Dependencies: Task 9.11 returned with API tests passing; do not fake pagination client-side.
Blockers: None reported at planning; prerequisites must be verified at pickup.

## Context and contract

Read ../README.md, ../decisions.md, ../coordination.md and work/GEMINI_WORKFLOW_PROMPT.md before backend pickup. Preserve environment parity and existing completed features. Record uncertainty instead of guessing business facts.

## Scope

- In scope: Add offset support to the typed search client and append batches of six when the results panel approaches its bottom. Only one page request per query may run at once. Stop after a short/empty batch; deduplicate by id. A full final batch may require one final empty fetch. Reset results, offset, scroll and cancellation when query changes or dialog closes.
- Out of scope: Production deployment, unrelated refactors, fabricated product claims, changing existing rate limits without an agreed contract.

## Dependencies and relevant files

- Depends on: Task 9.11 returned with API tests passing; do not fake pagination client-side.
- Inspect/edit: src/lib/api/catalogue.ts; src/components/SearchOverlay.tsx; associated tests
- Readiness: Planning complete; implementation evidence pending.
- Blocker protocol: Record exact missing input and owner here and in coordination.md; ask the user about ambiguous product/image classification.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 9.12-TC1 | Initial query loads six; scrolling appends the next batch without replacing earlier results or moving selection. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 9.12-TC2 | Rapid scrolling cannot issue duplicate concurrent requests; end of results stops further requests. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 9.12-TC3 | Query change/close cancels pending pages; stale responses cannot append; duplicate ids never render twice. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 9.12-TC4 | Later-page error or 429 keeps existing results and offers explicit retry without a retry storm; loading states are distinct. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |
| 9.12-TC5 | Keyboard selection scrolls active items into view; accessible Load more fallback works on desktop/mobile; telemetry records the query once rather than every batch. | Acceptance/regression | Isolated local fixtures; exercise this criterion | Criterion holds; no unrelated records changed | Automated test or documented local API/browser evidence | Not run |

## Security validation

- Use existing authorization, parameterized ORM queries, bounded requests and public response schemas. Do not expose draft products, customer records or secrets.
- Taxonomy writes require explicit target environment, a dry-run diff, narrow updates and a rollback plan; never reset the database.
- Test applicable invalid input, unauthorized mutation and inactive-product exclusion. Documentation-only planning introduces no application trust-boundary change.
- Disposition: Implementation validation pending.

## Acceptance checks

- [ ] Initial query loads six; scrolling appends the next batch without replacing earlier results or moving selection.
- [ ] Rapid scrolling cannot issue duplicate concurrent requests; end of results stops further requests.
- [ ] Query change/close cancels pending pages; stale responses cannot append; duplicate ids never render twice.
- [ ] Later-page error or 429 keeps existing results and offers explicit retry without a retry storm; loading states are distinct.
- [ ] Keyboard selection scrolls active items into view; accessible Load more fallback works on desktop/mobile; telemetry records the query once rather than every batch.
- [ ] Tests and security evidence recorded; self-review or independent review identified accurately.
- [ ] Changed behavior verified locally in Docker/API and browser before any push or preprod deployment.

## Handoff back

Update this contract, tasks.md, notes.md and coordination.md with status, changed files, exact tests/results, dependencies, blockers and next owner. Return to Codex for integration. Keep the global registry as links only. Do not push/deploy as part of this task without the release gate.

## Pickup checklist

- [ ] Read work/INDEX.md and this selected work folder/contract.
- [ ] Confirm ownership and prerequisites; mark only this task In Progress.
- [ ] Reuse verified existing assets and URLs; no repeat uploads or placeholder copies.

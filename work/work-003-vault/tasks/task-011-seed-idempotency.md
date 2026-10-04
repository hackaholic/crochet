# Task 3.11 — Repair idempotent catalogue seed associations

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 003

## Objective

Fix the local database seed failure caused by duplicate product/occasion associations so catalogue seeding can be rerun safely and the API starts cleanly against the local database.

## Context and contract

- Follow the [Work 003 README](../README.md), [task list](../tasks.md), [decisions](../decisions.md), and [seed verification task](task-008-seed-repair-verification.md).
- The current known failure is a duplicate association in `product_occasions` during seeding. The relevant association insertion logic is in `backend/app/db/seed.py` near the product/occasion seed paths.
- Preserve the existing product and occasion taxonomy, display ordering, enabled defaults, and database-driven behavior. Do not remove valid associations to hide the error.
- Do not change or expose credentials. Do not push or deploy.

## Scope

- In scope: identify the duplicate source; make seed insertion idempotent for product/occasion associations; add a focused regression test covering a fresh seed and a repeated seed (and existing association state where relevant); run the relevant backend checks.
- Out of scope: vault/decryption scripts, unrelated catalogue changes, frontend changes, migrations unless the current schema proves they are required, and deployment.

## Dependencies and relevant files

- Depends on: none for the code fix. The integrated Docker verification in Task 3.9 still depends on Tasks 3.2 and 3.8.
- Inspect/edit: `backend/app/db/seed.py`, `backend/app/models/catalogue.py`, relevant seed/storefront tests under `backend/tests/`, and only the minimal supporting files needed.

## Acceptance checks

- [x] A fresh database seed completes without duplicate-key errors.
- [x] Running the seed again is idempotent and preserves the expected product/occasion associations and ordering.
- [x] A focused regression test reproduces the previously failing path and passes (`test_seed_repair_idempotence` and `test_fresh_database_seed_idempotency_isolated` in `backend/tests/test_occasions_admin.py`).
- [x] Relevant backend tests pass: all 173 backend tests pass in `pytest backend/tests/`.
- [x] No unrelated changed files or secret-bearing output are included in the handoff.

## Completion details

- Extracted and centralized occasion association logic into a dedicated helper `seed_product_occasions(db)` in `backend/app/db/seed.py`.
- Replaced the redundant duplicate loops in `_seed_taxonomy_and_products(db)` and `seed_storefront_content(db)` with `seed_product_occasions(db)`.
- In `seed_product_occasions(db)`, product IDs are deduplicated in order, existing database associations and pending session associations are tracked to prevent duplicate primary key collisions, and existing associations have their `display_order` updated idempotently.
- In `reseed_catalogue(db)`, updated `db.query(ProductOccasion).delete()` to ensure session identity map synchronization.
- Enhanced regression tests in `backend/tests/test_occasions_admin.py` covering repeated seed runs, fresh isolated database seed, association ordering verification, display order updates, and reseed functionality.

## Handoff back

- Update this contract, Work 003 `tasks.md`, `notes.md`, and `coordination.md` with changed files, verification, and any blocker.
- Leave Task 3.9 as the integrated local Docker verification owner unless its contract is explicitly reassigned.
- Do not duplicate detailed implementation notes in global docs; update only the registry link if the handoff state changes.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 003 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm assignment; mark only Task 3.11 In Progress and set the work-local coordination handoff Active.
- [x] Reuse existing seed data and tests; do not repeat completed vault setup.

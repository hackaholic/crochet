# Task 3.9 — Repair duplicate seed issue, rebuild local Docker, and verify

**Owner:** Codex + Gemini
**Status:** Pending

## Objective

Ensure local API container starts cleanly with idempotent database seeding, rebuild local Docker services, decrypt local preprod secrets, and verify that the complete storefront and API function properly on `http://localhost:8080` and `http://localhost:8000`.

## Context and contract

Follow the project working rule: never deploy to VPS or push to `dev` before verifying the integrated Docker app locally.

## Scope

- In scope:
  - Rebuild Docker images (`docker/compose.yaml` and `backend/Dockerfile`).
  - Verify seed execution succeeds idempotently without unique constraint violations.
  - Verify health endpoints (`/health`) and sample storefront requests.
- Out of scope:
  - VPS deployment.

## Dependencies and relevant files

- Depends on: Task 3.2 local decrypt helper and Task 3.8 encrypted groups.
- Inspect/edit:
  - `backend/app/db/seed.py`
  - `docker/compose.yaml`

## Acceptance checks

- [ ] `docker compose up --build` brings up `api`, `frontend`, and `db` cleanly.
- [ ] `http://localhost:8080` and `http://localhost:8000/health` respond successfully.
- [ ] No duplicate key collisions or uncaught exceptions in container logs.

## Handoff back

- Update `work/work-003-vault/tasks.md` and `notes.md`.

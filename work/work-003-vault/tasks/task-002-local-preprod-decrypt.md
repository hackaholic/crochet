# Task 3.2 — Local preprod secret decrypt helper

**Owner:** Gemini  
**Status:** Pending

## Objective

Provide a simple local command that decrypts only the approved preprod secret groups needed for local Docker development, with safe file permissions and ignored plaintext outputs.

## Context and contract

- Follow [Work 003 README](../README.md), [task list](../tasks.md), [decisions](../decisions.md), and [secret inventory](../../../docs/secrets.md).
- Use SOPS + age and the recipient rules established by the vault work. Never place private keys or plaintext secrets in Git, logs, handoff notes, or container images.
- Preserve the owner's request for a convenient local `.env.preprod` workflow, while keeping local preprod secrets distinct from production secrets.
- Follow repository [agent rules](../../../AGENTS.md) and this [task contract template](../../TASK_TEMPLATE.md).

## Scope

- In scope: add or update a local helper/target to decrypt the required dev/preprod groups; fail clearly if SOPS, the age identity, encrypted inputs, or recipients are missing; create plaintext outputs with restrictive permissions; ensure generated outputs remain ignored; document usage and cleanup.
- Out of scope: VPS deployment/bootstrap, key generation or rotation, production secret activation, changing application behavior, and printing secret values.

## Dependencies and relevant files

- Depends on: task 3.1 service-scoped Compose secret interface and task 3.8 SOPS recipient/group configuration. Coordinate dependencies; do not invent encryption paths or variable names.
- Inspect/edit as needed: `.sops.yaml`, `secrets/`, `.gitignore`, `.env.example`, `backend/.env.example`, Compose files, `docs/secrets.md`, and relevant scripts/Makefile targets.

## Acceptance checks

- [ ] One documented local command decrypts only the intended preprod groups and makes them available to local Docker.
- [ ] Missing tools, key, or encrypted inputs fail safely with actionable messages and no secret values in output.
- [ ] Plaintext outputs have owner-only permissions, are ignored by Git, and are excluded from Docker build contexts.
- [ ] Tests use temporary keys and dummy values; relevant tests pass and results are recorded.
- [ ] Local Docker API/frontend verification is performed when dependencies permit; otherwise record the exact blocker without marking dependent work complete.

## Handoff back

- Update Work 003 task status and `notes.md` with changed files, commands/checks, results, and blockers.
- Record the local command and expected generated-file locations without including secret values.
- Report any contract/dependency change before expanding scope; leave unrelated task statuses unchanged.

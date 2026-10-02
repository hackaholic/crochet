# Task 9.1 — Threat model, audit policy, and security directory structure

**Owner:** Gemini + Codex
**Status:** In Progress

## Objective

Establish the security governance foundation: create the `work/security/` hierarchy (`findings/`, `exceptions/`, `reports/`), document the Sulocraft e-commerce threat model, and codify the automated security release gate policy with pass/fail criteria.

## Context and contract

Refer to `docs/SPECIFICATION.md` and user security requirements. Security infrastructure must integrate cleanly with the existing multi-agent task tracking workflow.

## Scope

- In scope:
  - `work/security/README.md`
  - `work/security/threat-model.md`
  - `work/security/audit-policy.md`
  - `work/security/decisions.md`
  - `work/security/tasks.md`
  - `work/security/notes.md`
  - Directory placeholders for findings, exceptions, and reports.
- Out of scope:
  - Modifying application business logic or UI components.

## Dependencies and relevant files

- Depends on: None.
- Inspect/edit:
  - `work/security/`
  - `work/INDEX.md`
  - `PROJECT_STATE.md`

## Acceptance checks

- [ ] `work/security/` contains README, threat-model, audit-policy, decisions, tasks, and notes.
- [ ] Threat model covers D2C shopping, payments, admin, secrets, R2 assets, and magic links.
- [ ] Audit policy establishes explicit blocking vs warning criteria across Level 1, 2, and 3.

## Handoff back

- Mark Task 9.1 completed in `work/security/tasks.md` and update `work/INDEX.md`.

# Task 9.1 — Threat model, audit policy, and security directory structure

**Owner:** Gemini + Codex
**Status:** In Progress

## Objective

Establish the security governance foundation: create the `work/work-013-security-audit/` hierarchy (`findings/`, `exceptions/`, `reports/`), document the Sulocraft e-commerce threat model, and codify the automated security release gate policy with pass/fail criteria.

## Context and contract

Refer to `docs/SPECIFICATION.md` and user security requirements. Security infrastructure must integrate cleanly with the existing multi-agent task tracking workflow.

## Scope

- In scope:
  - `work/work-013-security-audit/README.md`
  - `work/work-013-security-audit/threat-model.md`
  - `work/work-013-security-audit/audit-policy.md`
  - `work/work-013-security-audit/decisions.md`
  - `work/work-013-security-audit/tasks.md`
  - `work/work-013-security-audit/notes.md`
  - Directory placeholders for findings, exceptions, and reports.
- Out of scope:
  - Modifying application business logic or UI components.

## Dependencies and relevant files

- Depends on: None.
- Inspect/edit:
  - `work/work-013-security-audit/`
  - `work/INDEX.md`
  - `PROJECT_STATE.md`

## Acceptance checks

- [ ] `work/work-013-security-audit/` contains README, threat-model, audit-policy, decisions, tasks, and notes.
- [ ] Threat model covers D2C shopping, payments, admin, secrets, R2 assets, and magic links.
- [ ] Audit policy establishes explicit blocking vs warning criteria across Level 1, 2, and 3.

## Handoff back

- Mark Task 9.1 completed in `work/work-013-security-audit/tasks.md` and update `work/INDEX.md`.

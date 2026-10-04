# Task 13.1 — Inventory current work and establish lossless GitHub mappings

**Owner:** Codex
**Status:** Blocked — Projects V2 inventory is not available through the connected GitHub tools
**Work item:** Work 013 — GitHub Projects task tracking integration

## Objective

Inventory repository work items and determine the existing GitHub Project/Issue state and access path. Produce a lossless mapping plan before creating, renaming, or deleting any task record.

## Context and contract

- Follow the user-supplied spec captured in Work 013 notes.
- Preserve `/work` as the multi-agent execution layer. GitHub is the high-level GUI/source for major work status only after the mapping is established.
- Current repository is `hackaholic/crochet`; `gh` CLI is not installed.
- Existing folders may have Work IDs rather than issue numbers; Work 012 includes both isolation and deployment folders. Do not assume a one-to-one mapping until the work records are reviewed.

## Scope

- In scope: inventory `work/INDEX.md` and major work-folder metadata; inspect GitHub project/issue state through an authenticated approved interface if available; propose mappings and identify any existing issue IDs; record access blockers accurately.
- Out of scope: deleting or renaming existing directories, discarding/rewriting subtask history, creating duplicate issues/projects before inventory, adding third-party sync automation, or changing task scope/status to manufacture a mapping.

## Dependencies and relevant files

- Depends on: repository access and user-authorized GitHub repository access.
- Inspect/edit: `work/INDEX.md`, each major work `README.md` and `tasks.md` as needed for mapping; Work 013 tracking files.

## Acceptance checks

- [x] Enumerate existing major work items from `work/INDEX.md`; preserve stable Work IDs and all work-folder task records.
- [x] Inspect repository Issues before creating new objects; there were no existing open or closed Issues.
- [x] Check public owner Projects; none are listed. Private Project inventory remains unavailable through this connector.
- [ ] Produce a bidirectional mapping proposal or a concrete access blocker; do not guess issue numbers.
- [x] Confirm no existing work file, contract, handoff, or task was removed or overwritten.

## Handoff back

- Update this contract, Work 013 `tasks.md`, `notes.md`, and `coordination.md` with exact inventory/mapping results or blocker.
- Do not create GitHub issues/project until existing GitHub state has been inspected.
- Preserve the current work folders and status data.

## Pickup checklist

- [x] Read `work/INDEX.md`, Work 013 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [x] Confirm the repository identity from `git remote` and check whether `gh` is available.
- [x] Inspect whether an authenticated GitHub access path is available: GitHub web page shows Sign in; no GitHub connector is connected and `gh` is absent.
- [x] Confirm authenticated profile and admin access to `hackaholic/crochet`; the connector exposes issue operations but no Projects V2 operations.
- [ ] Inspect private Project state before creating the board, using the authenticated GitHub Projects UI/API.

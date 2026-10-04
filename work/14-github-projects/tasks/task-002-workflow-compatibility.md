# Task 13.2 — Define compatible GitHub ↔ `/work` operating rules

**Owner:** Codex
**Status:** Completed locally
**Work item:** Work 013 — GitHub Projects task tracking integration

## Objective

Update repository instructions so GitHub Projects/Issues can become the human-facing high-level task system while preserving existing `/work` execution files, subtasks, contracts, and handoffs.

## Context and contract

- Follow the user-provided GitHub Projects integration specification recorded in Work 013 notes.
- The repository already uses `work/INDEX.md`, per-work `README.md`, `tasks.md`, `decisions.md`, `notes.md`, `coordination.md`, and pickup-ready contracts. Do not replace or flatten this workflow.
- GitHub high-level status wins only after an issue mapping is verified; task-level ownership, progress, blockers, validation, and handoff remain work-local.
- Existing folders have stable Work IDs and many cross-links. Any issue-number-based path migration must be incremental, reversible, and occur only after references are inventoried.

## Scope

- In scope: concise `work/README.md` convention, updates to `AGENTS.md` and Gemini workflow prompt, clear high-level vs execution status responsibilities, task-reading and continuation rules, safe mapping/migration guidance.
- Out of scope: GitHub-side project or issue creation, directory renames, task/subtask deletion, duplicate task databases, third-party synchronization automation, and unrelated changes to current Work items.

## Dependencies and relevant files

- Depends on: Work 013.1 mapping/access inventory (GitHub-side steps remain blocked until authenticated access is available).
- Inspect/edit: `AGENTS.md`, `work/README.md`, `work/GEMINI_WORKFLOW_PROMPT.md`, Work 013 tracking files.

## Acceptance checks

- [x] Rules clearly preserve `/work` as the execution/coordination source and GitHub as high-level human tracking.
- [x] Existing subtasks remain in `/work`; Issues are created only for major, independently trackable work.
- [x] Existing directories and history cannot be discarded or renamed without a completed mapping/reference audit.
- [x] Agent instructions cover GitHub status conflicts, selected-task loading, continuation, handoffs, and validation.
- [x] Documentation links and whitespace checks pass; no live GitHub changes are claimed.

## Handoff back

- Update Work 013 `tasks.md`, this contract, and `notes.md` with changed files and verification.
- Keep Work 013.1 blocked until authenticated GitHub inventory is available; continue other independent local work.
- Do not change unrelated task status or rewrite existing work-folder history.

## Pickup checklist

- [x] Read the Work 013 scope and supplied integration specification.
- [x] Inspect existing repository workflow files and confirm `/work` content is intact.
- [x] Update and validate repository workflow documentation.

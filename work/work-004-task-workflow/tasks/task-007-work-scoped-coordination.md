# Task 4.7 — Work-scoped coordination and handoffs

**Owner:** Codex
**Status:** Completed

## Objective

Apply one consistent, low-duplication coordination and handoff workflow to every work item, and provide Gemini a reusable prompt that makes the repository rules explicit.

## Context and contract

The work directory is the source of truth for task scope and live state. Global docs must not repeat implementation contracts or status reports. Preserve existing history while making the current handoff easy to find. The user explicitly wants this applied to all work items, not only Work 010.

## Scope

- In scope:
  - Define global index vs work-local source-of-truth responsibilities in `AGENTS.md`, workflow decisions, and task template.
  - Give every current work folder a `coordination.md` entry point, with active handoffs linked to exact task contracts.
  - Replace global handoff/status narrative with compact routing indexes and retain old history in an archive.
  - Reconcile Work 010's Task 10.18 status with Gemini's reported completion without claiming local integration verification is done.
  - Create a reusable Gemini context/rules prompt and validate all affected links and statuses.
- Out of scope:
  - Implementing application features, pushing branches, or deploying to the VPS.
  - Marking unverified work complete based only on stale historical notes.

## Dependencies and relevant files

- Depends on: Work 004 tasks 4.1–4.6; current work directories and task contracts.
- Inspect/edit: `AGENTS.md`, `work/INDEX.md`, `work/TASK_TEMPLATE.md`, all `work/work-*/` and `work/work-013-security-audit/` folders, `docs/handoffs.md`, `docs/coordination-status.md`, relevant Markdown links.

## Acceptance checks

- [x] Every current work item has a concise `coordination.md` and its own source-of-truth task files remain authoritative.
- [x] Global docs contain only routing/current registry information; full prior history remains archived.
- [x] Work 010 clearly says Gemini backend work is reported complete and Codex local verification remains pending/in progress.
- [x] Gemini prompt instructs it to read/update only the selected work, use one contract per handoff, and avoid repeating completed asset work.
- [x] Repository instructions and template enforce the same process.
- [x] Markdown links and active statuses are validated; no push/deployment is performed.

## Handoff back

- Update Work 004 `tasks.md`, `notes.md`, `decisions.md`, and `coordination.md` with changed files, verification, and any unresolved migration issue.
- Report the Gemini prompt file path and explain the global-index/work-local-contract model to the owner.

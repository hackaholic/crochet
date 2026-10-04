# Task 13.4 — Map existing work to GitHub Issues and issue-numbered workspaces

**Owner:** Codex
**Status:** In Progress
**Work item:** Work 013 — GitHub Projects task tracking integration

## Objective

Map each indexed major work item to one verified GitHub Issue and a matching `work/<issue-number>-<slug>/` directory, preserving every existing Work ID, task/subtask, contract, handoff, decision, blocker, and validation record.

## Context and contract

- Follow Work 013's supplied GitHub Projects integration brief and `decisions.md`.
- GitHub Issue is authoritative for high-level objective and state. Work folders remain authoritative for detailed agent execution.
- Authenticated GitHub issue read/write access is available for `hackaholic/crochet`; no repository issues existed before migration.
- Project board creation is tracked separately in Task 13.3 and is unavailable through the current connector.
- Do not create Issues for small subtasks; keep those in existing local work files.

## Scope

- In scope: create one Issue for each major work indexed in `work/INDEX.md` and Security; close only work already marked Completed; rename folders to issue-number-based paths; update every local link; add reciprocal Issue links to each work README and issue body; verify task file counts/content and cross-links.
- Out of scope: GitHub Projects V2 board creation, issue creation for every local subtask, changing technical task statuses, rewriting task history, deleting the empty legacy Work 012 deployment stub, or pushing repository changes.

## Dependencies and relevant files

- Depends on: Task 13.1 issue inventory and Task 13.2 workflow rules.
- Inspect/edit: `work/INDEX.md`, every indexed work README/tasks file, issue bodies #1–#14, repository-wide Markdown references, `docs/handoffs.md`, `TASKS.md`.

## Acceptance checks

- [ ] Every indexed major work and Security has exactly one Issue with objective, acceptance, current high-level state, and workspace path.
- [ ] Each issue-numbered work README links back to its Issue and retains its stable Work ID.
- [ ] All repository references to old work paths are updated; Markdown links resolve.
- [ ] Existing task/contract files are preserved and no small tasks were converted to Issues.
- [ ] Completed work Issues are closed; incomplete items remain open.
- [ ] No repository commit/push/deployment is performed as part of this migration.

## Handoff back

- Update this contract, `tasks.md`, `notes.md`, and `coordination.md` with exact mapping and validation evidence.
- Report any unmapped legacy backlog item rather than silently dropping or reclassifying it.
- Keep Project V2 setup as the remaining external dependency.

## Pickup checklist

- [x] Confirmed Issues #1–#14 and their initial states.
- [x] Renamed the indexed work folders and updated issue bodies/local links.
- [ ] Validate all links, statuses, and task records.

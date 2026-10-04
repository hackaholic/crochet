# Work 013 — GitHub Projects task tracking integration

**GitHub Issue:** [#14](https://github.com/hackaholic/crochet/issues/14) · Work 013

**Status:** In Progress. GitHub Issues #1–#14 are created and linked to issue-numbered workspaces; repository workflow rules preserve existing subtasks/contracts. The authenticated GitHub connector can read/write Issues, but does not expose Projects V2 operations. The current GitHub browser session is signed out, so board creation and private-project inventory remain blocked.

**Objective:** Add a usable GitHub Projects board for Sulocraft work without losing or duplicating any current work item, subtask, task contract, decision, or handoff.

**Current task:** None locally; waiting for a signed-in GitHub Project interface to complete tasks 13.1, 13.3, and 13.6.

**Current known state:** Repository `hackaholic/crochet`; authenticated as `hackaholic` with admin/push access. Issues #1–#14 exist and each indexed major work item has an issue-numbered work folder. The current local branch is `dev`. The GitHub connector has no Projects V2 operations, `gh` is not installed, and the browser session is signed out.

**Responsibility split:**
- GitHub Project/Issues: human-visible backlog, major-work objective and acceptance, status, priority, owner, dependencies, milestone, area, environment, and completion.
- `/work`: detailed execution context, local subtasks/contracts, agent ownership and handoffs, decisions, blockers, and validation evidence.
- If a mapped high-level status conflicts, GitHub wins and the corresponding `/work` summary is reconciled; detailed execution records remain in their work folder.

**Preservation constraints:** Do not delete task records, flatten contracts, or rename an existing work folder before its issue mapping and all references are inventoried. Prefer incremental migration and retain stable Work IDs alongside GitHub issue numbers. Do not create GitHub issues for tiny implementation steps.

**Dependencies:** Repository issue management is available. Creating the Projects V2 board requires a signed-in GitHub browser session or a connected Projects-capable tool. Check existing private Projects before creating a duplicate.

**Definition of done:** A compact GitHub Project has the agreed fields and statuses; each in-scope major work item maps bidirectionally to a GitHub Issue and issue-numbered work directory; existing subtasks/contracts/handoffs remain intact; unique actionable entries from legacy snapshots are reconciled; repository rules explain the division and safe sync process; any unavailable user-only setup is recorded precisely.

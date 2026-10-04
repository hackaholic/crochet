# Work 013 decisions

- GitHub Project/Issues are the human-facing source of truth for high-level backlog, priority, ownership, dependencies, milestones, and overall status once the project is connected.
- `/work` remains the agent execution source of truth for technical subtasks, contracts, handoffs, decisions, blockers, and validation. Do not replace it with GitHub Projects.
- Preserve existing Work IDs, task files, contracts, and history. After verifying issue IDs and repository references, issue-numbered folders provide the GitHub lookup path while each README retains the original Work ID. GitHub issue numbers supplement rather than erase Work IDs.
- Create Issues for major independently trackable work only; keep small execution steps in existing work-local task files.
- No automatic synchronization mechanism is assumed. Define an explicit low-maintenance reconciliation flow and avoid adding a second global task database.
- Recommended board statuses are Backlog, Todo, In Progress, Blocked, Review, and Done. Map existing high-level `Pending` to Todo, `In Progress` to In Progress, `Blocked` to Blocked, and `Completed` to Done; do not infer priority, owner, milestone, or environment when the repository/GitHub record does not specify it.
- Use only the proposed fields from the supplied spec: Priority (P0–P3), Owner, Area, Milestone, and Environment (None/Dev/Preprod/Prod/Multiple), alongside Status. Prefer GitHub's native assignee field where it represents the actual person; agent roles remain work-local unless a board field is explicitly configured for them.
- Preserve the current numbered work folders until authenticated issue IDs exist and a repository-wide link/reference audit can support a safe path rewrite. The work README and Issue's implementation-workspace link provide bidirectional traceability during migration.

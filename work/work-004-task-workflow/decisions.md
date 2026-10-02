# Work 004 decisions

- `work/INDEX.md` stays short and contains only work-item links and high-level statuses.
- Agents read the index, one selected README, its task list and decisions, and only relevant task/code files.
- Each task status has one source of truth in that work folder; `docs/handoffs.md` communicates cross-agent contracts rather than duplicating implementation state.
- Every cross-agent subtask has a separate, self-contained contract file with scope, dependencies, acceptance checks, and a handback checklist. Small tasks owned by one agent can remain in `tasks.md`.
- **Release ownership:** Gemini implements and hands off backend subtasks; Codex owns the integrated release commit and push to `dev` after local frontend/API/database verification. Agents do not push separate partial builds, so each preview represents one tested contract.

# Work 004 decisions

- `work/INDEX.md` stays short and contains only work-item links and high-level statuses.
- Agents read the index, one selected README, its task list and decisions, and only relevant task/code files.
- Each task status and active contract has one source of truth in its work folder. Global `docs/handoffs.md` is an active-handoff link registry only; `docs/coordination-status.md` is a small router. Historical logs live under `docs/archive/`.
- Every cross-agent subtask has a separate, self-contained contract file with scope, dependencies, acceptance checks, and a handback checklist. Small tasks owned by one agent can remain in `tasks.md`.
- Every work item, including completed or queued work, has a `coordination.md` entry point. It links only confirmed active handoffs; task status remains authoritative in `tasks.md`.
- Gemini receives the reusable repository workflow prompt once per context reset/new session, plus the selected work ID and exact contract. Never send only a broad global handoff or ask Gemini to infer its assignment from chat history.
- Verified R2 asset uploads are complete inputs. A backend handoff updates the DB reference to the supplied object key; it must not copy or upload duplicate assets unless the contract explicitly reopens that scope.
- **Release ownership:** Gemini implements and hands off backend subtasks; Codex owns the integrated release commit and push to `dev` after local frontend/API/database verification. Agents do not push separate partial builds, so each preview represents one tested contract.

- Contract filenames follow the existing `task-NNN-description.md` convention. Logical IDs and historical status remain unchanged; completed contracts are retained. Nested work task directories retain their established structure.

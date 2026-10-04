# Work 004 notes

- Initial migration is complete. Reconcile old TODO statuses with actual implementation before moving queued work back to In Progress.
- Future user requests should first be represented as a new work item or a scoped subtask, then implemented.
- Every cross-agent subtask now gets a focused contract file; shared handoffs link directly to it, and the receiving agent must update the same work folder on return.
- Work 4.7 applies this contract and return path to every work item. The global handoff page is only a registry; work-local `coordination.md` plus the exact task contract carries active state. Old global narratives are retained as archives for history, not treated as current instructions.
- Work 4.7 verification: all 12 current work folders (Work 001–011 plus Security) have `coordination.md`; global registry/status docs are 9 lines each; the prior 1,763-line handoff and 595-line status logs are preserved under `docs/archive/`; local Markdown-link validation found 0 broken links across 155 files. No code tests, push, or deployment were required for this documentation-only task.

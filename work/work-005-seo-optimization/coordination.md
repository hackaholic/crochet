# Work005 coordination
**Work owner:** Codex
**CURRENT:**5.5 read-only audit — ready, Pending
**Active cross-agent handoffs:** None started
**Handoff state:** Backend contracts prepared; waiting on audit5.5 before implementation

## Exact backend pickup sequence — Gemini
First read work/GEMINI_WORKFLOW_PROMPT.md, then this work README/tasks/decisions and exact contract only.
- [5.17 metadata/entity truth](tasks/task-017-backend-seo-content-contract.md) — first backend implementation after audit; nullable approved facts and backward-compatible typed API.
- [5.18 public inventory/snapshot/generators](tasks/task-018-backend-public-route-inventory.md) — depends on5.17; Codex rendering/root resources consume returned contract.
- [5.19 slug lifecycle](tasks/task-019-backend-slug-lifecycle.md) — independent after audit; frontend redirects consume result.
- [5.20 image metadata](tasks/task-020-backend-image-metadata.md) — independent after audit; existing R2 assets reused.
- [5.15 Merchant feed](tasks/task-015-merchant-center-feed.md) — dependencies/policy and account facts must be checked; no fabricated compliance values.

One task In Progress per agent. Return exact changed files/schema/examples/test/security results and blockers in assigned contract plus work-local notes/tasks/coordination. Do not repeat foundational setup or asset uploads. Global registry links here only. No code implementation started by this planning pass.

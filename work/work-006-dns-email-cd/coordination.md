# Work 006 coordination

**Current owner:** Codex — Task 6.3.5 (backend test failures from the `dev` Actions run)
**Active cross-agent handoffs:** Task 6.3 workflow setup remains with Gemini; Task 6.3.5 is being verified by Codex.
**Handoff state:** The full backend suite passed on GitHub. Task 6.3.5 remains In Progress because the deploy step passed an empty SSH host; workflow invocation is fixed and regression-tested locally. A new push must verify PREPROD deployment and health check. Follow-up contract: [Task 6.3.5](tasks/task-006-backend-actions-failure.md). No Gemini handoff is needed.

## Ownership boundaries

- Work 003 owns SOPS/age vault and secret lifecycle.
- Work 012 owns VPS environment isolation and runtime contracts.
- Work 006 configures CI triggers and GitHub Actions deployment execution.

See [global active handoff registry](../../docs/handoffs.md).

# Work 012 coordination

**Current owner:** Codex — Work 012 item 09 (Deployment Workflow)
**Active cross-agent handoffs:** None. Gemini's Task 12.10.1 is completed; no Gemini task is waiting.
**Handoff state:** Tasks 12.09.2, 12.09.3, and 12.09.4 are completed. PREPROD release `d27b8d5da01b-9a161e68c2c6` is live and healthy. Task 12.09.5 (same-artifact PROD promotion) is pending; production encrypted secret groups are not provisioned. Task 12.09.6 (Work 006 CI alignment) is pending.

## Ownership boundaries

- Work 003 owns SOPS/age vault and secret lifecycle. Work 012 consumes its documented interfaces; do not reimplement vault behavior here.
- Work 006 owns CI triggers and workflow policy. Work 012 provides the reusable deploy/promotion interface for Work 006 to call.
- Any Gemini assignment must use a pickup-ready contract under this folder's relevant numbered subfolder, and this coordination file must record its active/returned/blocked state.

See [global active handoff registry](../../docs/handoffs.md).

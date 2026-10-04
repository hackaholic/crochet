# Work 012 coordination

**Current owner:** None (Item 07 completed; awaiting next item selection)
**Active cross-agent handoffs:** None active
**Handoff state:** Returned / Completed. Task 12.07.1 completed locally with 21/21 security tests passing. All preprod emails sandboxed fail-closed to allowlist, domains separated.

## Ownership boundaries

- Work 003 owns SOPS/age vault and secret lifecycle. Work 012 consumes its documented interfaces; do not reimplement vault behavior here.
- Work 006 owns CI triggers and workflow policy. Work 012 provides the reusable deploy/promotion interface for Work 006 to call.
- Any Gemini assignment must use a pickup-ready contract under this folder's relevant numbered subfolder, and this coordination file must record its active/returned/blocked state.

See [global active handoff registry](../../docs/handoffs.md).

# Work 012 coordination

**Current owner:** Codex
**Active cross-agent handoffs:** None
**Handoff state:** No handoff. Item 01 discovery has been reviewed; item 02 is active with Codex.

## Ownership boundaries

- Work 003 owns SOPS/age vault and secret lifecycle. Work 012 consumes its documented interfaces; do not reimplement vault behavior here.
- Work 006 owns CI triggers and workflow policy. Work 012 provides the reusable deploy/promotion interface for Work 006 to call.
- Any Gemini assignment must use a pickup-ready contract under this folder's relevant numbered subfolder, and this coordination file must record its active/returned/blocked state.

See [global active handoff registry](../../docs/handoffs.md); there is no Work 012 Gemini handoff currently.

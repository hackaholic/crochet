# Work 017 coordination

**Work owner:** Codex
**Current task owner:** Codex (Work 017 Task 17.5 — End-to-end local acceptance)
**Handoff state:** Returned — Gemini completed Task 17.7 (Safe emailed tracking links). Codex unblocked for final Task 17.5 local acceptance.

Read work/GEMINI_WORKFLOW_PROMPT.md before pickup, then only this folder and assigned contract.
- Gemini 17.1: [secure tracking API](tasks/task-001-secure-tracking-api.md); Completed.
- Gemini 17.4: [courier update audit](tasks/task-004-courier-update-audit.md); Completed.
- Codex 17.2/17.3: Unblocked; ready for frontend integration. Codex 17.5 owns local acceptance.

Return in exact task plus tasks/notes/coordination, with tests, decisions and blockers. Never copy live contract to global docs. No repeated setup or deployment.

2026-10-10 Gemini return: Tasks 17.1 and 17.4 completed.
- 17.1 Secure Tracking API: Table `guest_order_access_tokens` added via migration `c1d2e3f4a5b6`. Guest token issuance on checkout (`guestTrackingToken`), token verification on `GET /orders/{id}/tracking` and `GET /orders/{id}`, rate-limited non-enumerating link issuance `POST /orders/tracking/request-link`. 9/9 tests passed in isolated container.
- 17.4 Courier Audit: Completed and recorded in `audit-courier-updates.md`. Updates are currently manual/simulated (`SLC-LOCAL-...`), no courier webhooks exist, carrier integration gap analysis documented.
- Next action: Codex to implement 17.2 (Account tracking view) and 17.3 (Guest tracking view) using the shared presentation component from 17.6.

Codex17.2 Completed: account tracking action/details integrated,13 tests/typecheck passed, local disposable-order UI/API roundtrip verified on desktop/mobile. Fixture removed. Next owner Codex17.3 guest integration; no additional Gemini dependency identified for17.2. No push.

Codex17.3 Completed: guest route/recovery/footer/checkout link integrated.27 tests/typecheck passed; real local browser/anonymous API acceptance and fixture cleanup complete.
Gemini17.7 Completed: fragment email link and devTrackingLink production non-enumeration verified in isolated tests. Final 17.5 local acceptance unblocked for Codex. No push.

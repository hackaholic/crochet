# Work 017 tasks

## Pending
- [ ] 17.5 Codex — [End-to-end local acceptance](tasks/task-005-local-tracking-acceptance.md). Depends on returned17.7;17.2/17.3 implemented.

## In Progress
None.

## Completed
- [x] 17.7 Gemini — [Safe emailed tracking links](tasks/task-007-fragment-tracking-email-links.md). Completed. Fragment anchor `#token=...` implemented with encoded order numbers; `devTrackingLink` verified restricted from deployable environments; 10/10 security tests passed in isolated container.
- [x] 17.3 Codex — [Guest tracking UI](tasks/task-003-guest-tracking-ui.md).27 tests/typecheck pass; local browser and anonymous API verified. Backend17.7 security follow-up remains.
- [x] 17.2 Codex — [Account tracking view](tasks/task-002-account-tracking-ui.md).13 tests/typecheck pass; local real API desktop/mobile verified.
- [x] 17.1 Gemini — [Secure tracking access and API](tasks/task-001-secure-tracking-api.md). Completed. Added `GuestOrderAccessToken` model and migration `c1d2e3f4a5b6`, service `guest_tracking.py`, guest token issuance at checkout, protected `GET /orders/{id}/tracking` and `GET /orders/{id}` with guest token verification, `POST /orders/tracking/request-link` non-enumerating link issuance, 9/9 tests passed in isolated container, live API verified.
- [x] 17.4 Gemini — [Courier update audit](tasks/task-004-courier-update-audit.md). Completed. Audit report in `audit-courier-updates.md` confirms updates are manual/simulated (`SLC-LOCAL-...`), no logistics webhooks exist, and documented carrier integration gap analysis.
- [x] 17.6 Codex — [Shared tracking presentation](tasks/task-006-shared-tracking-presentation.md). 6 tests/typecheck passed; no API access or public route.

## Blocked
None. Frontend unblocked.

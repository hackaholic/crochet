# Task20.18 — Products table links and highlighting

**Owner:** Codex
**Status:** In Progress
**Work item:** Work020

## Objective and scope
Products table links and highlighting. Reuse shared AdminTable styles with bold700 sage headers and noticeable row hover/focus. Use native entity buttons, preserve existing actions/filters and permissions. No full redesign or backend changes. Products cell opens existing product editor; existing Edit remains functional.

## Dependencies
- Depends on: 20.15
- Dependency context: Shared template developed in same user-authorized batch; must verify before completion.
- Blocked by: None

## Tests and acceptance
- Native click/keyboard behavior opens correct entity; no duplicate request.
- Existing filters, action buttons and error paths remain unchanged.
- Labels escaped; permissions and disabled controls retained.
- Docker build, tests/typecheck and local browser/mobile checks required.

## Security validation
Pending; no change to authorization, endpoints or user data.

## Handoff
Record tests/local evidence and self-review here and work-local coordination. No push.

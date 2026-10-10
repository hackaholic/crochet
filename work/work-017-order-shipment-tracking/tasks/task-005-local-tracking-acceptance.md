# Task 17.5 — Local end-to-end tracking acceptance

**Owner:** Codex
**Status:** Pending
**Work item:** Work 017

## Objective/context and scope
Rebuild affected frontend/API Docker services; verify customer and guest flows with controlled local orders, denied access and empty shipment states. Verify desktop/mobile; Firefox where available. Record limitations before user review; no push without approval.
Out of scope: application redesign, unrelated changes, live shipment purchases, deployment.

## Dependencies and relevant files
Requires17.1–17.4 returns; tracking tests, local8080/8000, work records.

## Test cases (before implementation)
| ID | Category | Action/expected | Evidence |
| --- | --- | --- | --- |
| 17.5-TC01 | Acceptance/regression/failure/security | Relevant backend/frontend tests pass; local owner and guest UI/API render; unauthorized access denied; carrier capability described accurately; no production mutation or unverified deployment. | Not run; split into concrete cases before implementation |

## Security validation
Order access and shipment/customer data are sensitive. Enforce exact ownership or verified scoped guest credentials, validation/limits, safe errors and parameterized queries. No secrets/private contacts in handoff. Disposition: Pending audit/testing.

## Acceptance checks
- [ ] Scoped objective completed with relevant tests/evidence.
- [ ] Security disposition and self/independent review recorded accurately.
- [ ] Local verification recorded where runtime changes are made.

## Handoff back / pickup
Read work/GEMINI_WORKFLOW_PROMPT.md if Gemini, then selected work docs and this contract. Mark only assigned task In Progress. Return exact files/contracts, executed tests, remaining risks and blockers in this task and work-local tasks/notes/coordination. Report contract changes before expanding scope. No credentials or duplicate global contract.

Dependency update:17.2/17.3 implemented; before release acceptance requires returned Gemini17.7 emailed-link/response security checks. Full checkout→tracking link browser flow and email handoff remain in this task.

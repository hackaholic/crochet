# Task 22.2 — testclient cookie api

**Owner:** Gemini
**Status:** Pending
**Work item:** Work022
**Work owner:** Codex

## Objective
Replace deprecated per-request TestClient cookies with explicit client cookie setup/cleanup in affected tests as they are encountered. Preserve authentication intent and test isolation.

## Context and contract
DeprecationWarning: Setting per-request cookies=<...> is being deprecated; set cookies directly on the client instance instead. Observed in test_search_discovery.py::test_admin_prune_search_events_endpoint.
Read work/GEMINI_WORKFLOW_PROMPT.md for Gemini pickup. Evidence comes from existing Work009 run:25 passed,2 warnings; do not repeat a repo-wide audit or assume suggested package is automatically appropriate.

## Scope
- In scope: Targeted underlying warning fix and acceptance below.
- Out of scope: Global warning suppression, indiscriminate upgrades, unrelated failing-test repair, push/deployment.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Confirm overlap with Gemini's current failing-test work; reuse any fix already returned.
- Blocked by: None
- Blocker reason: None at planning; record exact compatibility/file-ownership issue at pickup
- Next action: Confirm owner/affected dependency or test setup, then mark only this task In Progress
- Inspect/edit: backend/tests/test_search_discovery.py; shared authenticated client fixtures only if needed

## Test cases
| ID | Category | Action | Expected outcome | Evidence |
| --- | --- | --- | --- | --- |
| 22.2-TC01 | Regression | Run affected tests in isolated test runner and capture warnings | Affected authenticated requests use supported cookie APIs and no longer emit this cookie warning. | Not run |
| 22.2-TC02 | Failure/security | Exercise unauthorized, session-isolation and incompatible dependency cases applicable to change | Cookies cannot leak between tests/users; unauthorized and wrong-role requests still fail; valid admin session still works. | Not run |

## Security validation
Dependency changes require compatibility/security review and reproducible lockfiles; do not weaken auth/session/DB isolation. No broad warning filtering. Record exact commands/results and accurately label self/peer review; disposition Pending.

## Acceptance checks
- [ ] Affected authenticated requests use supported cookie APIs and no longer emit this cookie warning.
- [ ] Cookies cannot leak between tests/users; unauthorized and wrong-role requests still fail; valid admin session still works.
- [ ] Meaningful tests pass; affected Docker/API/browser verification when behavior changes.
- [ ] Security disposition and evidence recorded; no silent suppression.
- [ ] Work-local status/handoff updated; no push.

## Handoff back
Update exact contract plus tasks.md/notes.md/coordination.md with files, commands/results, before/after warning evidence, dependency compatibility and blockers; return to Codex. Global handoff file links here only. Preserve completed contracts.

## Pickup checklist
- [ ] Read work/INDEX.md and selected work/task only.
- [ ] Confirm ownership and overlap with current Gemini fixes.
- [ ] Reuse completed fixes; add future warning subtasks only from actual new evidence.

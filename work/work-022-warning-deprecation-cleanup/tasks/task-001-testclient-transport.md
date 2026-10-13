# Task 22.1 — testclient transport

**Owner:** Gemini
**Status:** Pending
**Work item:** Work022
**Work owner:** Codex

## Objective
Investigate the installed FastAPI/Starlette/httpx compatibility matrix and replace the deprecated TestClient transport setup using the supported approach. Do not blindly install httpx2 or upgrade the whole dependency tree.

## Context and contract
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead. Seen from fastapi/testclient.py importing TestClient.
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
- Inspect/edit: backend/pyproject.toml and backend lockfile; backend/tests/conftest.py; affected TestClient fixtures; test Docker dependency setup

## Test cases
| ID | Category | Action | Expected outcome | Evidence |
| --- | --- | --- | --- | --- |
| 22.1-TC01 | Regression | Run affected tests in isolated test runner and capture warnings | Isolated affected tests construct TestClient without the transport warning; dependencies reproducible in local/CI images. | Not run |
| 22.1-TC02 | Failure/security | Exercise unauthorized, session-isolation and incompatible dependency cases applicable to change | Login, session cookies, redirects, async/lifespan and request behavior remain correct; existing security and isolated-DB controls preserved. | Not run |

## Security validation
Dependency changes require compatibility/security review and reproducible lockfiles; do not weaken auth/session/DB isolation. No broad warning filtering. Record exact commands/results and accurately label self/peer review; disposition Pending.

## Acceptance checks
- [ ] Isolated affected tests construct TestClient without the transport warning; dependencies reproducible in local/CI images.
- [ ] Login, session cookies, redirects, async/lifespan and request behavior remain correct; existing security and isolated-DB controls preserved.
- [ ] Meaningful tests pass; affected Docker/API/browser verification when behavior changes.
- [ ] Security disposition and evidence recorded; no silent suppression.
- [ ] Work-local status/handoff updated; no push.

## Handoff back
Update exact contract plus tasks.md/notes.md/coordination.md with files, commands/results, before/after warning evidence, dependency compatibility and blockers; return to Codex. Global handoff file links here only. Preserve completed contracts.

## Pickup checklist
- [ ] Read work/INDEX.md and selected work/task only.
- [ ] Confirm ownership and overlap with current Gemini fixes.
- [ ] Reuse completed fixes; add future warning subtasks only from actual new evidence.

# Task 22.3 — targeted verification

**Owner:** Codex
**Status:** Pending
**Work item:** Work022
**Work owner:** Codex

## Objective
Review returned fixes and verify affected local test/build/runtime paths emit neither recorded warning. Add targeted regression coverage where needed; register new distinct warnings encountered during this verification rather than scanning the whole repo.

## Context and contract
Known warnings are exact task001/task002 evidence. Current unrelated failing tests remain Gemini-owned; do not relabel those failures as deprecations.
Read work/GEMINI_WORKFLOW_PROMPT.md for Gemini pickup. Evidence comes from existing Work009 run:25 passed,2 warnings; do not repeat a repo-wide audit or assume suggested package is automatically appropriate.

## Scope
- In scope: Targeted underlying warning fix and acceptance below.
- Out of scope: Global warning suppression, indiscriminate upgrades, unrelated failing-test repair, push/deployment.

## Dependencies and relevant files
- Depends on: 22.1, 22.2
- Dependency context: Confirm overlap with Gemini's current failing-test work; reuse any fix already returned.
- Blocked by: None
- Blocker reason: None at planning; record exact compatibility/file-ownership issue at pickup
- Next action: Confirm owner/affected dependency or test setup, then mark only this task In Progress
- Inspect/edit: scripts/test.sh; affected backend tests; work-local evidence

## Test cases
| ID | Category | Action | Expected outcome | Evidence |
| --- | --- | --- | --- | --- |
| 22.3-TC01 | Regression | Run affected tests in isolated test runner and capture warnings | Focused isolated tests pass and known warning categories/messages are absent; local Docker/API/browser checks performed when behavior changes. | Not run |
| 22.3-TC02 | Failure/security | Exercise unauthorized, session-isolation and incompatible dependency cases applicable to change | No broad filterwarnings suppression, credential logs, DB isolation weakening or unrelated upgrade; exceptions/blockers recorded precisely. | Not run |

## Security validation
Dependency changes require compatibility/security review and reproducible lockfiles; do not weaken auth/session/DB isolation. No broad warning filtering. Record exact commands/results and accurately label self/peer review; disposition Pending.

## Acceptance checks
- [ ] Focused isolated tests pass and known warning categories/messages are absent; local Docker/API/browser checks performed when behavior changes.
- [ ] No broad filterwarnings suppression, credential logs, DB isolation weakening or unrelated upgrade; exceptions/blockers recorded precisely.
- [ ] Meaningful tests pass; affected Docker/API/browser verification when behavior changes.
- [ ] Security disposition and evidence recorded; no silent suppression.
- [ ] Work-local status/handoff updated; no push.

## Handoff back
Update exact contract plus tasks.md/notes.md/coordination.md with files, commands/results, before/after warning evidence, dependency compatibility and blockers; return to Codex. Global handoff file links here only. Preserve completed contracts.

## Pickup checklist
- [ ] Read work/INDEX.md and selected work/task only.
- [ ] Confirm ownership and overlap with current Gemini fixes.
- [ ] Reuse completed fixes; add future warning subtasks only from actual new evidence.

# Task <work-id>.<task-id> — <short title>

**Owner:** <agent/person>
**Status:** Pending
**Work item:** <Work NNN>

## Objective

What concrete result this subtask must produce.

## Context and contract

Relevant design/API/deployment decisions and expected behavior. Link only the docs needed to do this task.

## Scope

- In scope:
- Out of scope:

## Dependencies and relevant files

- Depends on:
- Inspect/edit:

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| <task>-TC01 | <criterion> | <success/boundary/failure/security/regression> | <concrete setup/input> | <observable outcome and side effects> | <verification> | Not run |

Cover changed behavior and relevant abuse cases; explain non-applicable categories. Record dependency readiness with evidence; do not begin blocked dependent work.

## Security validation (required for every subtask)

- Changed assets/trust boundaries and plausible abuse:
- Applicable controls and linked negative test IDs:
- API/database work: contract, object/field authorization, parameterized queries, validation, limits, safe errors, and least privilege.
- Commands/target/results and evidence (redacted):
- Disposition: <Pass / Fail / Blocked / Not applicable with rationale>
- Findings, severity, remediation owner, and blockers; any exception must link the existing authorized policy decision and review/expiry date:

## Acceptance checks

- [ ] Observable completion criteria.
- [ ] Relevant tests/checks and local verification.
- [ ] Test matrix executed; required cases pass and evidence is linked.
- [ ] Security disposition recorded; no unresolved blocking findings or required unrun checks.
- [ ] Peer review recorded, accurately identified as self-review or independent review.

## Handoff back

- Update this work item's `tasks.md` status and `notes.md` with changed files, verification, and blockers. Update `coordination.md` to Returned, Blocked, or the next agreed state.
- Report any contract change before expanding scope.
- Leave credentials/private data out of logs and handoff notes.
- Do not duplicate the contract or status in global docs; the global handoff registry links here.

## Pickup checklist

- [ ] Read `work/INDEX.md`, this work item's `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [ ] Confirm the task is assigned to you and change only this task's status to In Progress.
- [ ] Reuse completed inputs documented here; do not repeat uploads, copies, migrations, or setup already marked complete.

## Contract filename convention

Use `task-NNN-description.md`: a three-digit file number and lowercase hyphenated description. Preserve existing valid filenames and logical task IDs inside contracts/checklists; the filename number is not a dotted subtask ID. Allocate an unused number within the containing `tasks/` directory. Never delete completed contracts or renumber existing files to close gaps. When renaming a nonconforming file, preserve its content/status/ownership and update every reference, including coordination and handoff indexes.

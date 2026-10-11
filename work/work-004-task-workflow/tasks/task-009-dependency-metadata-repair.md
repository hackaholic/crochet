# Task 4.9 — Repair dependency metadata warnings
**Owner:** Codex
**Status:** Completed
**Work item:** Work 004
## Objective / scope
Fix the reported dependency-prose warnings in linked task contracts using the updated shared workflow format. Preserve every original narrative under Dependency context, all task IDs, owners, statuses and handoffs. No application/runtime changes or shared skill edits.
## Dependencies
Depends on: None
Dependency context: Updated workflow-coordinator/workflow-scaffold rules and WorkWeave read-only parser available.
## Acceptance / tests
Snapshot task IDs/owners/statuses/counts before editing; normalize only reported fields; use explicit existing task references, expand stated ranges, use contained contract links for ambiguous IDs. Broad work/infrastructure prerequisites remain context with Unknown/None as appropriate, never fabricated edges.
Reparse with WorkWeave: zero dependency-prose warnings, no new unknown/cycle warnings; original narrative retained, task inventory unchanged; git diff check.
## Handoff
Record evidence in this contract and work-local notes/coordination. No push.

## Return / evidence
56 parser-flagged contracts repaired. Original Depends on prose preserved verbatim under Dependency context. Explicit prerequisites use existing IDs; security-work IDs ambiguous with search-work IDs use contained contract links. Work-level prerequisites without a specific task remain Unknown with original context. Infrastructure-only prerequisites use None for task edges, retaining infrastructure requirements in context.
Read-only WorkWeave parse before/after: zero dependency-prose warnings; no new warnings (including unknown references/cycles); task IDs/titles/owners/statuses/contract links and counts identical. Preservation verified against /tmp/sulocraft-dependency-repair-evidence.json. Added shared workflow-coordinator pointer in SKILLS.md. Existing updated TASK_TEMPLATE.md preserved.
Self-review: documentation-only; no runtime/credentials/permission changes. No Docker rebuild needed. No push.

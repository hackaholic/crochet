# Work 001 coordination

This file is the work-local coordination entry point. The work folder is the source of truth: read this file with README.md, tasks.md, decisions.md, and only the assigned task contract.

**Current owner:** Codex — Work001; Customers1.9.2 completed, awaiting local user review
**Active cross-agent handoffs:** None active (Task 1.9.1 completed and returned to Codex)
**Handoff state:** Returned — Gemini completed Task 1.9.1; Codex completed Task 1.9.2

Dependencies: existing User and Order models available. Customer API implemented and verified.
Blockers: None. Customers API ready for UI integration.

## Current handoffs

Current implementation owner and status are recorded in the selected task entry in tasks.md. If no task is In Progress, the work is queued, completed, or blocked as that file states. A cross-agent handoff becomes active only when an exact contract is assigned and this section links to it.

## Return protocol

The assigned agent updates the exact contract, tasks.md, notes.md, and this file before returning the task. The global registry at docs/handoffs.md points here; it does not duplicate this work's status.

## Task ownership — 1.8–1.12
Codex owns 1.8 Inventory, 1.9 Customers scope/API audit, 1.10 Settings scope/API audit, 1.11 UI regression tests, and 1.12 local review delivery. The user provides final acceptance for 1.12. Backend enhancements discovered during these tasks require a separate exact Gemini contract before assignment; they do not transfer ownership of these parent tasks.

## Inventory handoff
[Task 1.8.4](tasks/task-008-inventory-concurrency.md) — Completed/Returned; owner Gemini. Codex frontend1.8 implemented and locally verified; Gemini atomic adjustment contract returned. Read reusable Gemini rules before pickup.

## Customers handoff
[1.9.1](tasks/task-010-customers-api.md) — Completed, Gemini; [1.9.2](tasks/task-011-customers-ui.md) — Completed, Codex. Scope audit 1.9 completed. Gemini completed read-only Customers API, test suite, and local Docker verification.

2026-10-10 Customers completion: Gemini 1.9.1 returned; 5/5 backend tests passing in isolated test container, live Docker API verified, docs/api-admin.md updated. Codex 1.9.2 unblocked to integrate Customers UI. No frontend changes or VPS push performed.

## Product visibility
Codex completed task1.7.10 (tasks/task-013-product-visibility.md); existing status API is ready. Customers1.9.2 completed after Gemini API return.

2026-10-10 Codex1.9.2 returned:34 tests/typecheck passed; Docker frontend rebuilt, real local desktop/mobile list/profile/history/open-order checked. No additional Gemini task needed for Customers V1. Firefox unavailable; broader acceptance remains pending. No push.

2026-10-10 Task1.8 Completed: Codex verified returned atomic API through local Inventory stock roundtrip and restoration, mobile validation, and5/5 Inventory tests. No active Inventory handoff or blocker. Next queued work:1.7.6 catalogue acceptance; no deployment performed.

Workflow metadata repaired under1.13: checklist IDs/statuses now match dedicated contracts; zero Work001 parser warnings. Parent blueprint/return history remains preserved. Catalogue final acceptance1.7.6 remains Pending.

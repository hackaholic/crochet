# Task 20.15 — Reusable admin table interaction template

**Owner:** Codex
**Status:** In Progress
**Work item:** Work 020

## Objective
Reusable admin table interaction template.

## Context and contract
User requests clickable product/entity names or cells, highlighted table rows on hover, and Pending payment navigation. Establish one reusable pattern across admin tables.

## Scope
- In scope: Create shared row hover/focus-within highlight and semantic clickable entity names/cells. Native links/buttons support keyboard and touch. Entire-cell click area is allowed; do not turn rows into invalid nested buttons or capture selection/control clicks. Clear affordance; no decorative links without a real destination.
- Out of scope: Full redesign, new reporting semantics, fake destinations, deployment and unrelated backend changes.

## Dependencies and relevant files
- Depends on: None
- Dependency context: Existing AdminApp/Dashboard order-filter callbacks, ProductsPage category filtering and existing product editing API can be reused. Backend task needed only if audit finds missing IDs or filter support; document exact gap before assigning Gemini.
- Blocked by: None
- Blocker reason: None
- Next action: Pick up after prerequisites are verified
- Inspect/edit: src/admin/AdminApp.tsx; src/admin/components/FinanceProductTable.tsx; FinanceAnalytics.tsx; FinanceTrendsTables.tsx; shared table styles; relevant admin pages

## Test cases
| Case | Category | Expected result |
| --- | --- | --- |
| Valid entity/status clicked | Success | Correct entity detail or filtered list; active reporting range preserved where applicable |
| Hover, keyboard focus, Enter/Space and touch | Accessibility | Highlighted row; native activation and readable focus; no hover-only dependency |
| Checkbox/menu/edit action inside row | Regression | Only intended action occurs; no double navigation |
| Missing/deleted ID or unsupported aggregate | Boundary | No invented link; safe fallback |
| Untrusted label/unauthorized entity | Security | Escaped content; existing backend authorization enforced; no data exposure |
| Mobile width and existing filters/paging | Regression | Contained scrolling and unchanged controls |

## Security validation
Disposition: Pending. Preserve admin auth/object permissions, use API entity IDs, never trust display text as routing input, safe errors and no credentials in logs.

## Acceptance checks
- [ ] Shared behavior implemented without copy-pasted row logic.
- [ ] Meaningful tests and security/self-review evidence recorded.
- [ ] Affected Docker frontend rebuilt and local desktop/mobile navigation verified before any push.

## Handoff back
Update this contract, tasks.md, notes.md and coordination.md. If backend support is missing, create one exact work-local Gemini contract with verified inputs and dependencies; do not duplicate global status. No push without authorization.

## Latest local evidence
2026-10-11: Bold 700 column headers confirmed on five pages, shared sage background and stronger hover confirmed. 25 scoped page tests plus 5 finance fixture tests passed; typecheck passed; frontend rebuilt/restarted. Product-name click opens persisted editor. No authorization/API changes; self-review performed. Remaining acceptance: resolve mobile dashboard table container width, verify remaining keyboard/entity actions and investigate existing product image failures. No push.

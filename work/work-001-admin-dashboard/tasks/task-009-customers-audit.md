# Task 1.9 — Customers scope and API audit

**Owner:** Codex
**Status:** Completed
**Work item:** Work 001

## Objective
Define the minimum useful V1 Customers screen, audit persisted models and current routes, and prepare a backend contract before implementing missing capabilities.

## Scope and dependencies
Read-only registered customer listing/profile and linked order history. Preserve supplied admin shell. Exclude customer editing, suspension, deletion, marketing, bulk export and invented lifetime-value metrics. Inspect src/admin/pages/PlaceholderPage.tsx, supplied admin.zip, backend user/order models, admin routes and docs/api-admin.md.

## Substeps
- Audit supplied design and existing API/data.
- Define V1 response/UI behavior and privacy boundaries.
- Prepare Gemini backend and dependent Codex UI contracts.
- Verify links, ownership and preserved task status.

## Acceptance/tests/security
Documentation-only: route/model/source audit and link checks; no runtime behavior changed. Require admin authorization, CUSTOMER-role scope and order association by user_id, never guessed email/phone matches. No sessions, credentials, identities or addresses in responses. Self-review required.

## Handoff back
Record findings and exact dependency contracts in work-local notes/coordination. No push or deployment.

## Findings and verification — 2026-10-10
Supplied admin.zip has pages/PlaceholderPage.tsx and no dedicated Customer design. Existing runtime Customers is also a placeholder. Global-search route limits customer candidates to 20 and includes all roles; no directory/profile/history API exists. User has nullable contacts, status, created_at/last_login_at; Order.user_id supports exact association. Existing admin router enforces get_current_admin.
V1 is read-only registered-customer directory/profile plus linked order history. Guest orders stay in Orders. Backend 1.9.1 and frontend 1.9.2 contracts created. Self-review: response minimizes PII and excludes auth/address data; no runtime change, Docker/test rerun not applicable for this planning task.

# Task 1.9.2 — Customers UI integration

**Owner:** Codex
**Status:** Completed
**Work item:** Work 001

## Objective and scope
Replace Customers placeholder with API-backed read-only list, profile and paginated order history inside supplied admin shell. No new design system, demo customer data or customer mutation features.

## Dependencies and relevant files
Requires returned/verified Gemini 1.9.1 task-010-customers-api.md. Add services/customers.ts and pages/CustomersPage.tsx with focused tests; reuse AdminShared, CatalogueFields styles and existing order-detail navigation via AdminApp. Supplied admin.zip includes Customers only as placeholder; preserve existing shell visual language.

## Acceptance/tests/security
- Query/pagination uses dedicated customer API; stable rows and abort stale requests.
- Profile renders nullable fields honestly and linked order count/history from backend. Open order uses existing OrderDetailPage.
- Loading, empty, error/retry and back-navigation states covered by tests.
- No role changes, email sending, stock/order mutations or contact-based history inference.
- Typecheck and regression tests; Docker rebuild; real local desktop/mobile browser acceptance; Firefox verification where available.
- Admin authorization remains; React safely renders text; no PII in logs.

## Handoff back
Update tasks/notes/coordination with tests, local browser evidence and security/self-review. No push until local review and user approval.

## Dependency check — 2026-10-10
Codex pickup requested. Gemini1.9.1 remains Pending in both task list and backend contract. Source audit finds no GET customer list/profile/order-history routes; only global search and POST send-welcome exist. Blocked on Gemini1.9.1 implementation/return. Do not implement dependent runtime integration or fabricate records.

## UI test cases prepared before implementation
| ID | Category | Action | Expected | Evidence |
| --- | --- | --- | --- | --- |
| 1.9.2-TC01 | Success | Load paginated API customers, search then next page | Backend totals/data rendered; search resets page; correct request parameters | CustomersPage.test.tsx, Passed |
| 1.9.2-TC02 | Regression | Slow previous search resolves after newer search | Stale response cannot replace current results | CustomersPage.test.tsx, Passed |
| 1.9.2-TC03 | Success/boundary | Open profile with nullable contacts and zero orders | Honest absent-value display and empty history; no fabricated fields | CustomersPage.test.tsx, Passed |
| 1.9.2-TC04 | Success | Page customer order history and open order | Exact customer id used; existing detail navigation receives orderNumber | CustomersPage.test.tsx, Passed |
| 1.9.2-TC05 | Failure/security | List/profile/history request fails or returns403 | No stale PII displayed as current; error/retry available, no fallback search | CustomersPage.test.tsx, Passed |
| 1.9.2-TC06 | Security | API customer name includes HTML-like text | Rendered as escaped text; no script/markup execution or PII logging | CustomersPage.test.tsx, Passed |
| 1.9.2-TC07 | Acceptance | Rebuild and inspect local desktop/mobile real API data | Supplied admin shell preserved; list/profile/history render; no page overflow | Local Docker/browser, Passed |

Next action: Gemini reads reusable workflow prompt and task-010-customers-api.md, implements1.9.1 and returns evidence. Codex then marks1.9.2 In Progress, implements, tests, rebuilds and verifies locally.

## Dependency ready — 2026-10-10
Gemini1.9.1 returned Completed with isolated tests/live API evidence and implemented routes. Codex1.9.2 now In Progress; earlier blocked check preserved as history.

## Return — 2026-10-10
Implemented typed customer service, reusable pagination, CustomersPage and CustomerProfile inside the supplied admin shell. Search is debounced and stale requests aborted; profile/history use exact API customer ID; order navigation uses existing order number detail flow. No customer mutations or fabricated business data.

Validation: Docker frontend rebuilt/restarted; TypeScript passed. All 34 admin/API tests passed with one worker, including six new Customers cases. Initial parallel run timed out in one existing Inventory test; serial rerun passed. Local browser verified persisted list, profile with three linked orders, opening existing order detail, nullable contacts, zero-order profile and unmatched search. At390×844 document width is390 with no page overflow. Only Chromium in-app browser available; Firefox remains unverified under broader1.6 acceptance.

Security/self-review: existing admin guard and credentialed transport retained; React text escaped, no PII logging, failed history clears profile state. Self-review completed; no independent peer review claimed. No further Gemini dependency for Customers V1. No commit/push/deployment. Next: user local review and remaining Work001 tasks. Earlier dependency notes above are historical.

# Task 1.9.3 — Clickable customer names and full profile
**Owner:** Codex
**Status:** Completed
**Work item:** Work 001
## Objective/context
Customer name opens the existing read-only profile. Remove the Actions column and separate View button. Profile shows all supported business profile information actually stored: name, email, account phone, status, joined/last login, linked order count/history, and saved addresses with recipient/contact/default label. No invented contact data.
## Scope
Reuse existing Customers/CustomerProfile design. Keyboard-accessible name button/link and visible focus. Render every owned address field returned by the dedicated admin API, including line1/line2, city/state/postal code/country and address phone/recipient; account phone remains separate. Missing fields display Not provided; empty addresses show No saved addresses. No customer mutation, guest email matching, credentials/auth tokens or provider identities.
## Dependencies/files
Depends on: 1.9.4
Dependency context: Current customer API includes name/email/phone/status/dates/order count only; it does not return saved addresses. Existing list/order APIs already implemented; do not recreate them.
Files: src/admin/pages/CustomersPage.tsx, src/admin/components/CustomerProfile.tsx, src/admin/services/customers.ts, CustomersPage.test.tsx.
## Tests/security
- TC01 click/keyboard customer name selects correct ID; Actions/View column absent. (Verified)
- TC02 returned multiple/default addresses and distinct account/address phones render without duplication/invention. (Verified)
- TC03 no addresses/null phone/line2 handled; customer change ignores stale response; error/retry/back/order navigation retained. (Verified)
- TC04 user content React-escaped; no PII logs; credentialed admin endpoint only. Link backend 1.9.4 auth/ownership evidence. (Verified)
- Test counts: 6/6 tests passed in `CustomersPage.test.tsx`; 64/64 tests passed across all 14 admin test suites; TypeScript typecheck and frontend production build pass with 0 errors.
- Docker frontend rebuilt and restarted; verified on `http://localhost:8080/admin` (HTTP 200 OK). No push/deploy.


## Return — 2026-10-11
Completed. Existing implementation had customer name buttons/no customer Actions column and typed saved-address detail rendering; finished integration verification and added wrapping/escaped-address regression. Reused Gemini1.9.4 returned6/6 backend authorization/ownership checks; no duplicate backend work.

`docker-compose -f docker/compose.yaml exec -T frontend sh -c 'pnpm exec vitest run src/admin/pages/CustomersPage.test.tsx src/admin/services/customers.test.ts && pnpm typecheck'`:8 CustomersPage tests passed; typecheck passed (no matching standalone customers transport test file, not counted). Covers correct ID/name navigation, list/search/paging, multi-address/default/distinct phone fields, missing fields, error/retry/back/order navigation, stale list responses and escaped long address text.

Frontend image rebuilt and restarted (Compose dependency startup issue handled by starting rebuilt container). Local realAPI admin: customer list has four columns without Actions; Enter opens Demo Customer, accountphone9999900124 separate addressphone9999900123, persisted QA Work018 Default address/NewDelhi/110001/IN and two linked orders visible. Mobile390x844 document390: no horizontal overflow. Screenshot /tmp/sulocraft-admin-customer-details.png. Viewport reset. Firefox unavailable, broader1.6 acceptance retains cross-browser limitation.

Security disposition: Pass; escaped customer/address content, no raw HTML/PII logs, read-only credentialed admin data and owned addresses per returned server tests. Self-review: no data changes, no guest identity inference, absent fields honest. Customer Actions column removed; linked-order navigation preserved. No push/deploy.

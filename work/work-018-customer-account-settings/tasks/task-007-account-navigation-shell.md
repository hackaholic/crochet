# Task 18.5.1 — Account navigation shell

**Owner:** Codex
**Status:** Completed
**Work item:** Work 018

## Objective
Create responsive Profile/Addresses/Orders navigation around existing persisted account content. Keep email read-only and exclude it from profile-save payload; existing name-save behavior preserved. Do not implement blocked phone/address/progress APIs.

## Dependencies and files
Existing account overview/address/order APIs available. src/pages/AccountPage.tsx, reusable src/components/account/AccountNavigation.tsx and tests. Parent18.5 remains pending until backend contracts return.

## Test cases
- TC01 navigation exposes each existing panel with accessible selection and no stale order details in other panels.
- TC02 login email is read-only and excluded from name-save payload.
- TC03 existing tracking open/close and logout continue working.
- TC04 API fixtures preserve authenticated transport; backend unchanged, returned backend validation/security acceptance remains in18.2–18.4.
- TC05 real localhost render/mobile layout after Docker build; browser availability limitations recorded.

## Security validation
No new authorization endpoints. Email mutation removed from client; API security remains backend18.2 responsibility. Escape API text; hidden tracking data must not appear on unrelated panels. No business data hardcoded.

## Acceptance
- [x] Frontend regression/typecheck passes; existing backend contracts unchanged.
- [x] Local Docker and browser navigation verified; evidence recorded.

## Handoff
Update exact task, tasks.md, notes.md, coordination.md. No push. Parent scope remains unchanged.

## Verification — 2026-10-10

8 scoped tests passed (AccountPage4, account API1, tracking panel3) and TypeScript passed in Docker. TC01–TC03 pass; TC04 authenticated transport test passes, backend behavior unchanged and server validation remains assigned18.2–18.4. Final image7486f04572ed built with frozen install and frontend restarted. Local browser Profile/Addresses/Orders navigation confirmed, email readOnly confirmed, mobile390px had scrollWidth380 (no overflow). IAB only; Firefox unavailable/unverified. No profile/order mutations during browser check. Screenshot /tmp/sulocraft-work018-profile.png.

Build blocker fixed: existing package source-map-js override missing from pnpm lockfile; pnpm10 lockfile-only regeneration added that one metadata line without version changes. Docker no-deps startup rejected existing api dependency; normal up -d frontend reused healthy API/db and started correctly. No push/deploy.

Security/local self-review: editable payload now name only; no hidden email mutation; React escaped text; unrelated order panel unmounted by navigation. Backend email-change enforcement is not claimed fixed by this frontend step.

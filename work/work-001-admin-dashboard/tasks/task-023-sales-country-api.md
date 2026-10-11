# Task 1.14.3 — Sales by country and Indian region

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 001 / 1.14 Finance analytics

## Objective and context
Aggregate by checkout shipping destination country from immutable order address snapshot, never current profile, IP or saved address. Return normalized country code, order count, product units, defined sales amount/share; unknown destinations have a separate bucket. Add Indian state breakdown when historical address data supports it, preserving unknown values. Do not invent international sales or geolocate customers. Country sales is money reporting, not a tax/demand inference.

## Scope
In scope: selected-period Sulocraft commerce analytics using existing database/API and supplied admin design. Out of scope: architecture redesign, fabricated sales, visitor analytics, inferred profit, production deployment and unrelated work.

## Dependencies and relevant files
Depends on: 1.14.1
Dependency context: Returned1.14.1.
Inspect/edit: Order shipping snapshots; focused analytics service/repository; admin schemas/routes; docs/api-admin.md

## Test cases (define before implementation)
Backend: IN and international fixtures, unknown/malformed legacy destination, saved-address edit does not change historical country, no duplicate order multiplication by line count, date/payment filters. Frontend: country/state rendering and unknown/empty states in1.14.6; no hardcoded country sales. Security: no street/email/phone fields returned; admin auth, bounded filters.

- 1.14.3-TC01: Country breakdown aggregates gross sales, units, orders from `Order.shipping_address_json`.
- 1.14.3-TC02: Indian destinations breakdown into state regions (`regions` list).
- 1.14.3-TC03: Missing or malformed countries grouped into "UNKNOWN" without failing.
- 1.14.3-TC04: Immutable snapshot preservation: no dependency on live User addresses.

## Security validation
Admin authentication verified. Strict exclusion of personal PII (no street addresses, recipient names, phone numbers, or zip codes in breakdown). Read-only database query.

## Acceptance checks
- [x] Metric/payload definitions documented, dependencies ready.
- [x] Relevant frontend/backend cases implemented with results or explicit dependent UI acceptance.
- [x] Accounting/boundary/security tests pass; no invented data or unsupported financial claims.
- [x] Review accurately labeled; performance concerns and blockers recorded.

## Handoff back
Return exact payload examples without customer PII, definitions/filter semantics, changed files, test commands/counts and Codex integration needs. Update this contract, tasks.md, notes.md and coordination.md. No push/deploy without user authorization; completed contracts preserved.

## Pickup checklist
- [ ] Read work/INDEX.md and Work001 README/tasks/decisions/coordination and this contract.
- [ ] Gemini first reads work/GEMINI_WORKFLOW_PROMPT.md.
- [ ] Confirm ownership; mark only selected task In Progress.

# Task 1.14.4 — Top-selling products and variants

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 001 / 1.14 Finance analytics

## Objective and context
Correct existing ranking semantics for selected date and eligible orders; rank by units or product revenue with stable tie-breaks, configurable bounded limit/pagination. Return product identifier, sale-time name, SKU/variant where supported, backend image_url, units, distinct orders, product revenue; separate cancelled/refunded treatment per1.14.1. Define unknown/deleted products honestly; products renamed across orders must not split just by name. No duplication of catalogue truth or constructed image storage paths in UI.

## Scope
In scope: selected-period Sulocraft commerce analytics using existing database/API and supplied admin design. Out of scope: architecture redesign, fabricated sales, visitor analytics, inferred profit, production deployment and unrelated work.

## Dependencies and relevant files
Depends on: 1.14.1
Dependency context: Returned1.14.1.
Inspect/edit: Existing get_admin_analytics; analytics service; order item snapshots; product/media resolver; docs/api-admin.md

## Test cases (define before implementation)
Backend: unpaid/cancelled exclusion, partial returns, date filtering, stable ties, renamed/deleted products, multiple variants, pagination and image URL handling. Frontend: ranking metric toggle, thumbnails/fallback and page transport fixtures in1.14.6. Security: admin only, valid metric/limit, no hidden secrets/PII in payload.

- 1.14.4-TC01: Date-filtered and eligible order-filtered ranking (`GET /api/v1/admin/finance/top-products`).
- 1.14.4-TC02: Metric sorting by revenue and units with deterministic tie-breaks.
- 1.14.4-TC03: Snapshot-driven attributes (`product_id`, `product_name`, `sku`, `variant_name`, `image_url`).
- 1.14.4-TC04: Cancelled orders excluded from sales rankings.

## Security validation
Admin session required. Parameterized order filtering, bounded limits (`ge=1, le=100`), whitelist `metric in ('revenue', 'units')`. No customer PII leaked. Read-only operation.

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

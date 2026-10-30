# Task 1.7.13 — Product production profile API

**Owner:** Gemini (pickup-ready)
**Status:** Pending — deferred for V1; do not start until scope is narrowed and owner reactivates it
**Work item:** Work 001 — Admin dashboard integration

## Objective

Add bounded, admin-only storage for production information captured while creating/editing any catalogue product across Sulocraft categories, and support assigning the product to configured occasions. Keep internal production data separate from the product copy returned to customers. The existing product name remains customer-facing and unchanged.

## Context and contract

- Existing admin product fields already cover name, description, category/tag IDs, photos, customization, status, variants/SKU/price/stock, and six customer-facing information fields (`handmadeDetails`, `materialsUsed`, `sizeDimensions`, `processingTime`, `careInstructions`, `shippingDelivery`). Do not duplicate these.
- `ProductVariant.cost` and `weight` plus admin create/update/read schemas already exist; the UI does not expose them. Reuse these fields; do not add a second total-cost or weight column.
- `ProductOccasion` and admin occasion CRUD exist, but product create/update does not accept occasion IDs. Extend the product admin API to read/write those existing associations.
- Public `ProductDetail.attributes` is serialized from `metadata_json`. Do not put production/cost/supplier data in `metadata_json` or any public storefront/SEO schema.
- Store the new typed `productionProfile` separately from public fields and expose it only through admin product create/read/update. It applies to flowers/bouquets, amigurumi, baby gifts, home/decor, pooja/devotional and other products; it may contain optional generic `components` rows (`name`, positive `quantity`, `unit`, optional `color`, `material`, `brand`, `shadeCode`) and one optional bounded `finishingNotes` value. Do not add a flower-only form, fixed Flower 1/2/3 slots, a duplicate product type/name, or arbitrary HTML.
- Customer-facing summary remains the existing description and six public detail fields. Production rows/finishing notes, supplier details, shade codes and costs never auto-render publicly; the owner can selectively summarize appropriate facts in the existing public fields.
- No lead-time/delivery promises or default production claims. Add-on relationships and material/packaging/labour cost breakdowns are deferred. Existing variant `cost` is the total unit cost; selling price minus cost/margin can be derived privately by the admin UI.

## Scope

- In scope: typed optional admin production profile persistence; bounded schema validation; admin product create/read/update serialization; product occasion association IDs on admin create/update/read; migration/model changes only if required; focused tests and API docs.
- Out of scope: public exposure of the production profile or cost; replacing the current product page; new public copy/defaults; image uploads; additional SKU/cost fields; add-on system; shipping/lead-time promises; taxonomy redesign.

## Dependencies and relevant files

- Depends on: None
- Dependency context: Product, ProductVariant, ProductOccasion and admin product/occasion endpoints already exist. Codex verified current model/schema/API fields on 2026-10-29; the ProductEditor lacks cost/weight/occasion/profile controls.
- Blocked by: None
- Blocker reason: None
- Next action: Gemini reads `work/GEMINI_WORKFLOW_PROMPT.md`, marks only 1.7.13 In Progress, and implements/returns this contract.
- Inspect/edit: `backend/app/models/catalogue.py`, `backend/app/schemas/admin.py`, `backend/app/api/v1/admin.py`, relevant migrations, `backend/tests/test_admin_products.py` and occasion tests, `docs/api-admin.md`.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1.7.13-TC01 | Persist a production profile | Success | Admin creates/updates a product with multiple component rows and finishing notes, then reads it | Exact validated profile round-trips through admin API | Backend product API integration test | Not run |
| 1.7.13-TC02 | Bound profile input | Boundary/failure | Submit empty names, non-positive/oversized quantities, too many rows, or overlong text | 422; no partial product/profile/association mutation | Backend integration test with state assertion | Not run |
| 1.7.13-TC03 | Protect admin data | Security | Anonymous/customer reads or updates profile and occasion IDs | 401/403; database state unchanged | Existing admin auth fixtures + new integration test | Not run |
| 1.7.13-TC04 | Keep production/cost data private | Security/regression | Request public catalogue, product detail, and SEO product representations for a product with distinctive internal values | No `productionProfile`, supplier/shade code, variant cost, or finishing notes appear in public payloads | Backend serialization tests for each public DTO | Not run |
| 1.7.13-TC05 | Validate occasion associations atomically | Failure/security | Admin submits valid and nonexistent occasion IDs together | Request fails; existing product and all occasion associations remain unchanged | Backend PostgreSQL integration test | Not run |
| 1.7.13-TC06 | Preserve legacy products | Regression | Read/update products with no production profile and existing occasion mappings | Existing fields/variants remain unchanged; profile is optional and no fabricated defaults appear | Existing catalogue regressions + migration test | Not run |

## Security validation (required for every subtask)

- Changed assets/trust boundaries and plausible abuse: Admin product API, database production profile, product/occasion associations; customer or anonymous callers may try to read/write private production/cost details, submit oversized nested data, inject HTML, or tamper with occasion IDs.
- Applicable controls and linked negative test IDs: Existing admin-role dependency; strict nested allowlist and bounded list/text/numeric limits; transactionally validate all occasion IDs; use ORM-bound values; serialize only allowlisted public fields. Required tests: TC02–TC05.
- API/database work: Admin authentication and role authorization; validate product and occasion ownership/existence; reject invalid shapes/limits; transaction rollback on association failure; safe 4xx responses; public/storefront/SEO schema exclusion.
- Commands/target/results and evidence (redacted): Not run; report exact isolated Docker test command and report link on return.
- Disposition: Pending
- Findings, severity, remediation owner, and blockers: None known; public-schema leakage must be covered before completion.

## Acceptance checks

- [ ] Admin-only typed profile and existing occasion association CRUD round-trip without duplicating SKU, cost, weight, or public description fields.
- [ ] Existing product/variant data and products without profiles remain compatible.
- [ ] Public storefront and SEO payloads exclude all production-only fields and variant cost.
- [ ] All test cases executed; applicable security negatives pass.
- [ ] API contract documented and migration is additive/reversible under project conventions.
- [ ] Peer review is accurately recorded as self-review or independent review.

## Handoff back

Return this exact contract with files/migration, API examples, exact Docker test command/results, security evidence, and any blockers. Update Work001 `tasks.md`, `notes.md`, and `coordination.md`. Do not modify the Codex UI task's status. Do not push/deploy.

## Pickup checklist

- [ ] Read `work/INDEX.md`, Work001 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [ ] Confirm 1.7.13 is assigned to Gemini; mark only this task In Progress.
- [ ] Reuse the existing variant `cost`/`weight` and `ProductOccasion` model/API; do not repeat previous setup or media work.

# Task 1.7.14 — Product editor production details

**Owner:** Codex
**Status:** Pending — deferred for V1; do not start until scope is narrowed and owner reactivates it
**Work item:** Work 001 — Admin dashboard integration

## Objective

Make creation/editing for every catalogue product category capture a concise production profile and useful customer-facing summary without overwhelming the existing form or exposing internal notes and costs. The existing product name remains customer-facing and unchanged.

## Context and contract

- Preserve the existing supplied admin visual language and ProductEditor structure.
- Existing public summary/detail fields remain the only customer-facing source: name, description, and the six Work019 information sections. Label these clearly as storefront content.
- Add a compact, optional, collapsed-by-default **Production details (internal)** section for repeatable generic component rows and finishing notes. It must work for flowers/bouquets, amigurumi, baby gifts, home/decor, pooja/devotional, and other products; never make a flower-only form or fixed Flower 1/2/3 fields. Show clearly that production rows and notes are internal and do not appear on the storefront.
- Extend the existing variant editor with its already-supported total cost and weight. Show derived margin only inside admin, per SKU/variant, from that variant's price and cost; never persist a second computed margin field.
- Add configured occasion association controls using the returned 1.7.13 product API contract. Do not hardcode occasion names or IDs.
- Reuse existing variant names for sizes, categories/tags for product classification, current SKU/stock/status/photos, and `sizeDimensions` for public dimensions. Do not duplicate those fields.
- Keep user-facing processing/shipping copy blank or factual until the owner confirms it; do not invent lead times.

## Scope

- In scope: typed ProductEditor/client interfaces and save/load integration for `productionProfile` and `occasionIds`; variant cost/weight editing; derived admin margin display; validation, accessible dynamic component-row controls, failure/retry preservation, customer/public display boundary tests; local browser verification.
- Out of scope: database/API implementation (Task 1.7.13), new storefront design, new default customer copy, add-on relationships, production lead-time promises, new cost breakdown categories, R2 uploads, or push/deploy.

## Dependencies and relevant files

- Depends on: [1.7.13](task-046-product-production-profile-api.md)
- Dependency context: Backend typed admin API, privacy tests, occasion IDs, and returned API docs must be complete before integrated UI acceptance. Product editor work can be prototyped with types/tests, but do not implement against guessed payloads.
- Blocked by: [1.7.13](task-046-product-production-profile-api.md)
- Blocker reason: Owner review concluded the full production profile may be overkill for V1; keep the existing catalogue and wait for a narrower approved scope.
- Next action: None until the owner reactivates a smaller product-editor improvement.
- Inspect/edit: `src/admin/components/ProductEditor.tsx`, `ProductInformationFields.tsx`, `VariantEditor.tsx`, `src/admin/services/catalogue.ts`, `src/lib/api/admin.ts`, related component tests, and storefront public DTO tests.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1.7.14-TC01 | Create/edit production rows | Success | Admin adds/removes multiple component rows, saves, reopens product | Rows and finishing notes persist exactly; no fixed row limit below API cap | ProductEditor unit/integration test and local admin round-trip | Not run |
| 1.7.14-TC02 | Variant cost, weight, and margin | Success/boundary | Admin edits SKU price/cost/weight including zero cost | Values persist per variant; margin displays correctly only in admin | VariantEditor tests + local round-trip | Not run |
| 1.7.14-TC03 | Occasion assignments | Success/regression | Select multiple API-provided occasions and save/reopen | Selected associations persist; no hardcoded options | ProductEditor/API integration test | Not run |
| 1.7.14-TC04 | Save failure preservation | Failure | Reject product/profile/occasion save | Visible error; entered values remain; no false success | ProductEditor test with rejected API request | Not run |
| 1.7.14-TC05 | Public/private boundary | Security/regression | Load public product page for product with internal profile and cost | Storefront displays only public summary/detail fields; no internal profile, cost, supplier, or shade code | Public page/API regression test and browser inspection | Not run |
| 1.7.14-TC06 | Accessible responsive editor | Acceptance | Keyboard-operate component rows and open editor at desktop/mobile sizes | Controls labeled, add/remove usable, no horizontal overflow or clipped fields | Focused tests and local Playwright browser check | Not run |

## Security validation (required for every subtask)

- Changed assets/trust boundaries and plausible abuse: Admin product form and transport for private costs/production notes; malformed text/numeric values and non-admin access must not reveal or mutate protected values.
- Applicable controls and linked negative test IDs: Render text as text, rely on backend validation/auth from 1.7.13, don't include internal fields in public-facing presentation or logs; TC04–TC06.
- API/database work: None in this UI task; verify request payload shapes are typed and server errors preserve input. Confirm public DTO cannot populate internal fields.
- Commands/target/results and evidence (redacted): Not run; after implementation run focused frontend Docker typecheck/tests and actual local browser verification.
- Disposition: Pending dependency
- Findings, severity, remediation owner, and blockers: Blocked by Gemini API contract 1.7.13.

## Acceptance checks

- [ ] Optional production form remains compact and clearly internal; existing customer-facing information stays intact.
- [ ] Variant cost/weight and calculated margin operate per SKU; cost/margin remain private.
- [ ] Occasion options and assignments are backend-driven.
- [ ] All tests/security cases pass and local Docker/browser behavior is verified.
- [ ] Peer review is accurately recorded as self-review or independent review.

## Handoff back

Update this contract and Work001 `tasks.md`, `notes.md`, and `coordination.md` with changed files, focused test commands/results, local UI evidence, security disposition, and blockers. Do not push/deploy.

## Pickup checklist

- [ ] Read `work/INDEX.md`, Work001 `README.md`, `tasks.md`, `decisions.md`, `coordination.md`, and this contract.
- [ ] Confirm 1.7.14 is assigned to Codex and only mark it In Progress when 1.7.13 returns.

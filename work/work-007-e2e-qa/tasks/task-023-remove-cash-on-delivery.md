# Task 7.13 — Remove Cash on Delivery from new purchases

**Owner:** Codex
**Status:** In Progress
**Work item:** Work 007

## Objective

Customers can only place new orders using supported online payment methods. COD is not offered in the storefront and the order API rejects COD requests.

## Context and contract

The owner confirmed Sulocraft does not offer Cash on Delivery. Retain legacy COD order rows and their admin/reporting behavior for historical records; do not migrate or delete order data. Payment methods remain configured by the existing payment-provider integration and this task does not alter Cashfree or provider credentials.

## Scope

- In scope: remove COD from checkout and basket payment messaging; remove COD as the API default/accepted new-order value; reject direct COD API requests before order/cart/inventory mutations; update current API documentation and affected checkout/API tests; preserve historical COD reads and reports.
- Out of scope: changing payment providers, deleting historical COD orders, changing old-order admin analytics, or deploying to production.

## Dependencies and relevant files

- Depends on: None
- Dependency context: None. Work 007 Cashfree retry integration is already complete locally and deployed to dev; COD removal is a separate checkout policy change.
- Blocked by: None
- Blocker reason: None
- Next action: Implement the storefront and API restriction, run targeted tests/security checks, rebuild Docker locally, and inspect local checkout before pushing to dev.
- Inspect/edit: `src/pages/CheckoutPage.tsx`, `src/pages/CartPage.tsx`, their tests, `src/lib/api/orders.ts`, `backend/app/schemas/order.py`, `backend/app/api/v1/orders.py`, order/purchase tests, and `docs/api-orders.md` / `docs/api-payments.md`.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 7.13-TC01 | COD is not offered to customers | Regression | Render checkout and basket | No COD payment option or “We accept COD” label appears | CheckoutPage and CartPage Vitest; local Playwright | PASS — frontend tests pass; local basket and payment step contain no COD text |
| 7.13-TC02 | Existing online checkout remains available | Success | Render checkout payment step with supported methods | UPI, card, net banking remain available; Cashfree integration still builds and its tests pass | CheckoutPage Vitest + local Playwright | PASS — three supported methods visible; Cashfree intent tests pass |
| 7.13-TC03 | Direct COD order creation is rejected without side effects | Security/failure | Guest POSTs `/api/v1/orders` with COD and a populated basket | Validation failure; no order/payment row, stock decrement, coupon increment, or cart clear | `backend/tests/test_purchase_regression.py::test_cod_checkout_rejected_without_side_effects` | PASS — COD returns 422; basket and stock unchanged; no matching order; no-method and unsupported method also return 422 |
| 7.13-TC04 | Historical COD remains readable | Compatibility | Run legacy order/reporting tests | Historical payment method and reports remain intact | Full `./scripts/test.sh all` | PASS — full backend suite exits 0; COD model/reporting paths remain available for stored records |
| 7.13-TC05 | Unsupported or missing payment values fail closed | Boundary | POST an unsupported method and then omit `paymentMethod` | API returns validation error before business mutation | `backend/tests/test_purchase_regression.py::test_cod_checkout_rejected_without_side_effects` | PASS — both requests return 422 before order/cart/stock mutation |

## Security validation

- Changed assets/trust boundaries and plausible abuse: public order-creation endpoint; a caller could bypass the removed UI and request COD directly.
- Applicable controls and linked negative test IDs: Pydantic request validation with a strict allowlist (`7.13-TC03`, `7.13-TC05`); assert no order, payment, inventory, coupon, or cart side effects. Preserve legacy COD only in persisted order/reporting models.
- API/database work: validate payment method at request boundary before service side effects; no SQL interpolation or new authorization scope.
- Commands/target/results (redacted): `./scripts/test.sh all` exited 0; its frontend suite reports `420/420` passing and backend suite reaches 100%. `corepack pnpm run typecheck` passed. `bash scripts/security/scan-sast.sh` reported zero blocking High/Critical findings (34 total findings including 33 warnings and one active exception); the full test gate's fallback SAST and secret checks both passed with zero findings. Live local OpenAPI reports `paymentMethod` enum `UPI`, `CARD`, `NETBANKING` and marks the field required. No secrets or customer data were printed.
- Disposition: Pass for the local change; dev deployment remains pending.
- Findings, severity, remediation owner, and blockers: None known; Codex owns remediation.

## Acceptance checks

- [x] COD is absent from checkout and basket payment messaging.
- [x] API rejects COD and unsupported/missing methods before mutations.
- [x] Historical COD orders remain readable and existing admin reporting still passes.
- [x] Relevant tests and security checks pass.
- [x] Rebuild local Docker services and verify checkout at `http://localhost:8080` plus API behavior at `http://localhost:8000`.
- [ ] Record self-review and evidence; push only after local verification; do not deploy production.

## Handoff back

Update this contract, Work 007 `tasks.md`, `notes.md`, and `coordination.md` with changed files, test/security/local browser evidence, and dev workflow status. Preserve unrelated working-tree changes.

## Pickup checklist

- [x] Read Work 007 context and relevant contracts.
- [x] Confirm assignment and set only this task In Progress.
- [ ] Reuse the existing Cashfree integration; do not repeat credential or asset setup.

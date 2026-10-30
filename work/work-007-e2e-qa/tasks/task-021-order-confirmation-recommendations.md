# Task 7.12 — Layered recommendations on order confirmation

**Owner:** Codex  
**Status:** Completed  
**Work item:** Work 007

## Objective

Use the existing product discovery template to show relevant product recommendations after an order is placed, making the confirmation screen useful for continued browsing while preserving a clear order/payment confirmation.

## Context and contract

The checkout already renders multiple API-driven recommendation sections before order placement using `ProductRecommendations` (You May Also Like, Best Sellers, New Arrivals, Featured Picks, Trending Now). The current `orderPlaced` and Cashfree verified-payment success states omit these sections. Reuse the existing component, discovery endpoint and Quick Add behavior; do not create hardcoded products or duplicate ranking/fetch logic.

Keep the confirmed order/payment summary visually primary and compact. Recommendation loading/failure must never delay, hide, or reverse a confirmed order. Additions after placement belong to a new basket and must not mutate the completed order.

## Scope

- In scope: render the shared layered recommendations in the local Mock and server-verified Cashfree success state; keep API order, accessible section headings, deduplication and Quick Add behavior; add focused UI and security regression coverage.
- Out of scope: backend discovery ranking/API changes, payment/order-state changes, email/tracking workflows, new product content, and preprod/live checkout.

## Dependencies and relevant files

- Depends on: 7.6.1, 7.2.4.2
- Dependency context: Existing discovery endpoint and ranked feed are implemented; frontend Cashfree and Mock success states are now integrated locally.
- Blocked by: None
- Blocker reason: None
- Next action: Returned/Completed; 7.2.4.1 Gemini runtime wiring remains the next Cashfree gate.
- Inspect/edit: `src/pages/CheckoutPage.tsx`, `src/pages/CheckoutPage.test.tsx`, `src/components/ProductRecommendations.tsx`, `src/lib/api/productDiscovery.ts`.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 7.12-TC01 | Successful local order includes layered product discovery | Success | Complete local COD checkout | Order number/status stays visible and multiple existing API-driven sections render below it | `CheckoutPage.test.tsx` + local Playwright browser | Pass — local COD order showed five API sections, order timeline and guest tracking link |
| 7.12-TC02 | Cashfree confirmation keeps recommendations | Regression | Resolve return verification with matching server SUCCESS | Payment confirmation remains primary; same recommendation template appears | `CheckoutPage.test.tsx` | Pass — Best Sellers and New Arrivals render with verified payment |
| 7.12-TC03 | Discovery failure never changes purchase status | Failure | Make discovery endpoint fail after order success | Confirmation remains visible; private errors are not shown | `CheckoutPage.test.tsx` | Pass — order confirmation remains visible and generic discovery retry alert is shown |
| 7.12-TC04 | Add after order creates only new basket activity | Regression/security | Quick Add from confirmation recommendations | Existing order/payment remains unchanged; product is added through canonical basket API | `CheckoutPage.test.tsx` | Pass — one cart callback, one order creation, order number remains visible |
| 7.12-TC05 | No private customer/payment data enters discovery | Security | Inspect discovery request and rendered cards | Only checkout context and public catalog products are used; customer/payment details are not passed into discovery | `CheckoutPage.test.tsx` + SAST | Pass — discovery invoked with checkout context only; no PII/payment props passed |
| 7.12-TC06 | Purchased products remain excluded after basket clear | Regression/security | Complete an order, then rerender with an empty basket | Purchased product stays excluded while other recommendations render | `CheckoutPage.test.tsx` | Pass — purchased rose omitted while another product remained |

## Security validation

- Changed assets/trust boundaries and plausible abuse: public product discovery is rendered next to private order confirmation; Quick Add runs after a completed order.
- Applicable controls and linked negative test IDs: use only existing public discovery payload; keep payment/session/order data out of product-card props and URLs (7.12-TC05); Quick Add must call the existing cart flow and cannot alter the completed order (7.12-TC04).
- API/database work: None planned; reuse the existing authenticated/guest-safe discovery and cart APIs.
- Commands/target/results and evidence (redacted): focused frontend suite 24/24, TypeScript, production build budgets, SAST 0 findings, Docker API/storefront health and local Playwright checkout confirmation pass.
- Disposition: Pass for frontend scope
- Findings, severity, remediation owner, and blockers: None known.

## Acceptance checks

- [x] Local order confirmation shows the existing layered recommendation template with database/API products.
- [x] Checkout/payment success stays visible if discovery is loading or unavailable.
- [x] Quick Add after order placement does not modify the placed order.
- [x] Focused tests and applicable security validation pass; local desktop/mobile render is checked at 390×844 and desktop.
- [x] Peer review is recorded as self-review or independent review.

## Handoff back

The confirmation/recommendation update is local and ready for owner review. No push or deployment performed. Cashfree preprod still depends on Gemini 7.2.4.1 and the separate sandbox acceptance gate.

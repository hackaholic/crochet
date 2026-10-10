# Work 017 — Customer and guest shipment tracking

**Owner:** Codex (work lead)
**Status:** Pending

## Objective
Customers and guest purchasers can securely view their own order shipment details and status timeline.

## Current state
Account shipment action/view and guest tracking route/recovery UI implemented and locally verified (17.2/17.3). Backend GET /orders/{id-or-number}/tracking returns courierName, trackingNumber, estimatedDelivery and timeline. Account orders enforce exact user ownership. Guest orders currently skip ownership checks: knowing an order identifier is sufficient. Gemini17.1 added verified guest tokens;17.7 email-link/response safety follow-up remains before release. Automatic courier updates are not verified.

## Scope and architecture
Extend existing modular application, without redesign: typed frontend API service, reusable tracking view, account entry point and guest access page; backend routes delegate access rules and queries to cohesive service/repository modules. Data stays database-driven. No invented courier URLs or delivery dates.

## Dependencies/constraints
Existing order/auth/email services; Gemini contract17.1; courier audit17.4. Local tests and browser/API checks before any preprod deployment; same code/configurable environment parity. No deployment authorized by this plan.

## Definition of done
Authorized account and guest access work end-to-end; unauthorized disclosure prevented; shipment absence and errors handled honestly; automatic courier update capability audited and its limitations documented; tests and desktop/mobile local acceptance recorded.

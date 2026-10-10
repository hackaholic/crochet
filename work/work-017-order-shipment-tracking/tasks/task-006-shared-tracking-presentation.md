# Task 17.6 — Shared tracking presentation

**Owner:** Codex
**Status:** Completed
**Work item:** Work 017

## Objective and scope
Build a reusable data-only tracking component from existing OrderTrackingOut schema. No API fetching, guest credentials or routes; those remain dependent on17.1. Both17.2/17.3 reuse it after secure API return. No demo runtime data.

## Dependencies/relevant files
Existing backend schemas/order.py OrderTrackingOut verified. Add src/components/orders/ShipmentTracking.tsx and tests, src/lib/api/orderTrackingTypes.ts. No backend dependency for presentation alone.

## Test cases
| ID | Category | Action | Expected | Evidence |
| --- | --- | --- | --- | --- |
|17.6-TC01|Success|Persisted courier/tracking/ETA/timeline|Fields rendered as data with semantic headings/time|Passed component test|
|17.6-TC02|Boundary|Null courier/number/date and empty timeline|Honest unavailable states; no fake shipment|Passed component test|
|17.6-TC03|Failure|Invalid timestamps|No Invalid Date or crash|Passed component test|
|17.6-TC04|Security|HTML-like note/status/number|Escaped text, no executable markup/links|Passed component test|
|17.6-TC05|Regression|Replace first order with second|No old order detail remains|Passed component test|
|17.6-TC06|Security|Long untrusted strings|Wrapping constraints, no constructed external URL|Passed component test|

## Security validation
Untrusted API strings reach React text nodes only. No HTML injection, provider URLs, credentials, logging or persistence. Access authorization stays backend responsibility17.1; this component never fetches. Security disposition pending tests/self-review.

## Acceptance/handoff
Component tests/typecheck pass; record self-review. Rebuild affected Docker service; actual routed browser acceptance belongs to17.2/17.3 and cannot be claimed for unused component. Update tasks/notes/coordination. No push/deployment.

## Return — 2026-10-10
Added typed OrderTracking payload and presentation-only ShipmentTracking component.6/6 tests passed in frontend Docker; TypeScript passed. Frontend image rebuilt/restarted and local storefront API-driven Most Loved Creations loads. No tracking route connected, so this is component preparation only: real customer/guest tracking browser acceptance remains17.2/17.3/17.5, including actual mobile wrapping.

Security disposition: Pass for this component scope. API strings are React text nodes; no HTML injection, external link construction, fetch, credential storage or logging. Source inspection and malicious-text test confirm these properties. Self-review completed; no independent peer claimed. API authorization remains unresolved17.1; not marked secure end-to-end. No backend edits, push or deployment.

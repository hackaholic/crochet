# Task 18.4 — Order lifecycle progress contract

**Owner:** Gemini
**Status:** Completed
**Work item:** Work 018

## Objective and context
Audit current Work017 tracking/history and admin lifecycle transitions. Return a documented controlled milestone schema (stable code, completion/current/pending state, nullable timestamp) derived from actual status history; reuse existing tracking endpoint additively. Use existing READY_TO_SHIP semantics; expose processing/out-for-delivery without pretending they are shipped/delivered. Explain cancelled/refunded states. Verify placed event exists on checkout and admin changes record real history; do not backfill invented events. Reuse Work017 auth and guest token controls.

## Scope
In scope: existing account/order feature enhancement and its frontend/backend contract tests. Out of scope: architecture redesign, carrier integration, production deployment, password/OTP authentication, deleting completed work.

## Dependencies and relevant files
Depends on: Work017 existing secure tracking API; inspect returned 17.1/17.7; no repetition of guest auth setup.
Inspect/edit: `backend/app/api/v1/orders.py`; `backend/app/schemas/order.py`; `backend/app/models/order.py`; `src/lib/api/orderTrackingTypes.ts`; `backend/tests/test_tracking_security.py`; `backend/tests/test_orders.py`; `src/lib/api/tracking.test.ts`

## Milestone Schema Design (DEC018-4)

Additive payload in `OrderTrackingOut`:
```json
{
  "orderNumber": "SLC-...",
  "status": "PROCESSING",
  "paymentStatus": "PAID",
  "trackingNumber": "SLC-...",
  "courierName": "...",
  "estimatedDelivery": "...",
  "timeline": [
    { "id": 1, "status": "CONFIRMED", "note": "Order confirmed", "timestamp": "2026-10-10T..." }
  ],
  "milestones": [
    { "code": "PLACED", "label": "Order Placed", "state": "COMPLETED", "timestamp": "2026-10-10T..." },
    { "code": "CONFIRMED", "label": "Confirmed", "state": "COMPLETED", "timestamp": "2026-10-10T..." },
    { "code": "PROCESSING", "label": "Processing", "state": "CURRENT", "timestamp": "2026-10-10T..." },
    { "code": "READY_TO_SHIP", "label": "Ready for Shipment", "state": "PENDING", "timestamp": null },
    { "code": "SHIPPED", "label": "Shipped", "state": "PENDING", "timestamp": null },
    { "code": "OUT_FOR_DELIVERY", "label": "Out for Delivery", "state": "PENDING", "timestamp": null },
    { "code": "DELIVERED", "label": "Delivered", "state": "PENDING", "timestamp": null }
  ],
  "terminalState": null
}
```
For terminal states (`CANCELLED`, `REFUNDED`):
- `terminalState`: `{ "code": "CANCELLED", "label": "Order Cancelled", "explanation": "This order was cancelled...", "timestamp": "..." }`
- Standard forward milestones do not falsely claim progress.

## Test cases (define before implementation)

| ID | Requirement/subtask | Category | Setup/actor and action | Expected response and state | Test file/command or manual procedure | Result/evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 18.4-TC01 | Placed/Confirmed checkout order returns initial milestones | Success | Checkout creates order; query `/orders/{number}/tracking` | `milestones` returned with PLACED/CONFIRMED marked COMPLETED/CURRENT; timestamps present | `backend/tests/test_orders.py` | Pass (`test_order_tracking_and_cancellation`) |
| 18.4-TC02 | Sequential forward transitions advance milestone states | Lifecycle | Admin transitions order through PROCESSING -> READY_TO_SHIP -> SHIPPED -> OUT_FOR_DELIVERY -> DELIVERED | Each step marks previous as COMPLETED, active step as CURRENT, future as PENDING with exact history timestamps | `backend/tests/test_tracking_security.py` | Pass (`test_18_4_lifecycle_milestone_progression`) |
| 18.4-TC03 | Skipping intermediate statuses does not invent fake timestamps | Integrity/DEC018-4 | Order transitions straight from CONFIRMED to SHIPPED | SHIPPED is CURRENT with timestamp; PROCESSING/READY_TO_SHIP completed or skipped without fabricated timestamps | `backend/tests/test_tracking_security.py` | Pass (`test_18_4_lifecycle_milestone_progression`) |
| 18.4-TC04 | Cancelled order populates terminalState without false delivery | Terminal/Integrity | Order cancelled by customer or admin | `terminalState.code == "CANCELLED"`, explanation provided; DELIVERED is NOT marked COMPLETED | `backend/tests/test_tracking_security.py` | Pass (`test_18_4_terminal_state_cancelled_and_refunded`) |
| 18.4-TC05 | Refunded order populates terminalState with refund explanation | Terminal/Integrity | Order transitioned to REFUNDED | `terminalState.code == "REFUNDED"`, explanation provided; paymentStatus distinct | `backend/tests/test_tracking_security.py` | Pass (`test_18_4_terminal_state_cancelled_and_refunded`) |
| 18.4-TC06 | Re-visiting status preserves earliest/truthful timestamps | Determinism | Multiple duplicate history updates | Timestamps reflect actual event occurrences without crash or corruption | `backend/tests/test_tracking_security.py` | Pass (`test_18_4_lifecycle_milestone_progression`) |
| 18.4-TC07 | IDOR & guest token security controls preserved | Security | Foreign user or invalid/expired guest token requests `/orders/{number}/tracking` | HTTP 404 (Work017 security invariants maintained) | `backend/tests/test_tracking_security.py` | Pass (`test_tc02_account_isolation_denies_wrong_user_and_anonymous`) |
| 18.4-TC08 | Frontend type & transport contract verification | Frontend contract | `getOrderTracking` in `src/lib/api/tracking.ts` returns `milestones` and `terminalState` | TypeScript types match; vitest tests pass | `src/lib/api/tracking.test.ts` | Pass (4 vitest tests pass) |

## Security validation

- Object & Field Authorization: Strictly enforces owner (`user_id == user.id`) or valid order-scoped guest token; foreign requests return 404 without leaking order existence.
- Integrity: No fake timestamps backfilled. Timestamps originate only from actual `OrderStatusHistory` rows.
- State Isolation: Payment status remains completely separate from fulfillment status. Terminal cancellation never flags delivery milestones as completed.

## Acceptance checks
- [x] Contract and validation policy documented; dependency readiness recorded.
- [x] Relevant frontend and backend tests identified, executed or explicitly pending dependent UI acceptance.
- [x] Required behavior, failure and security checks pass with evidence.
- [x] Self/independent review labeled; no unresolved release blocker concealed.

## Handoff back
Update this exact contract, tasks.md, notes.md and coordination.md. Return changed files, schema/error examples without personal data, test commands/counts, blockers and exact Codex integration needs. No push or deployment. Preserve completed task history.

## Pickup checklist
- [x] Read work/INDEX.md and Work018 README/tasks/decisions/coordination.
- [x] Gemini reads work/GEMINI_WORKFLOW_PROMPT.md before pickup.
- [x] Confirm ownership and mark only this task In Progress.

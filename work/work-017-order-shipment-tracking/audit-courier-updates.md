# Audit Report — Automatic Courier Updates & Shipment Automation (Task 17.4)

**Auditor:** Gemini  
**Date:** 2026-10-10  
**Work Item:** Work 017 — Customer and guest shipment tracking  
**Status:** Completed  

---

## 1. Executive Summary

This audit assesses the current state of courier tracking updates, tracking number generation (`SLC-LOCAL-...`), and carrier integrations within the Sulocraft backend (`backend/app`).

### Key Findings:
1. **Updates are 100% Manual / Simulated**: There are currently **no automated carrier integrations, webhook receivers, or scheduled polling background jobs** for order tracking status.
2. **`SLC-LOCAL-...` is an internal synthetic placeholder**: Generated automatically at order creation time (`orders.py:507`) with a default courier name `"Sulocraft Local Express"` and an estimated delivery of `now + 5 days`.
3. **Admin manual transitions drive lifecycle**: The order status, courier name, and tracking number are updated manually by administrators via `PATCH /api/v1/admin/orders/{id}/status`.
4. **Transition to `SHIPPED` triggers customer email/SMS**: When an administrator updates an order to `SHIPPED`, `dispatch_order_status_background` sends out notifications via the configured `NotificationService` / `EmailService`. If no courier was set, it defaults to `"Bluedart / Delhivery"`.
5. **No courier webhook endpoints exist**: Existing webhook infrastructure in `backend/app/api/v1/payments.py` handles payment providers (Razorpay) with HMAC signature verification, but no equivalent webhook endpoint or service exists for logistics/courier providers.

---

## 2. Detailed Technical Audit

### 2.1 Tracking Number Generation (`SLC-LOCAL`)
- **Location**: [`backend/app/api/v1/orders.py`](file:///home/anu/git/crochet/backend/app/api/v1/orders.py) lines 506–508:
  ```python
  courier_name="Sulocraft Local Express",
  tracking_number=f"SLC-LOCAL-{secrets.token_hex(3).upper()}",
  estimated_delivery=now + timedelta(days=5),
  ```
- **Nature**: Synthetic placeholder assigned at checkout time. It does not map to any external carrier system.
- **Risk / Observation**: Because this number is assigned before fulfillment, customers might mistake it for an active third-party carrier tracking code. Per **DEC-017-002**, frontend UI must display courier info honestly and avoid presenting `SLC-LOCAL` as a clickable third-party carrier link.

### 2.2 Admin Status Updates
- **Location**: [`backend/app/api/v1/admin.py`](file:///home/anu/git/crochet/backend/app/api/v1/admin.py) lines 1224–1290 (`update_order_status`).
- **Mechanism**:
  - Validates `status` against `OrderStatus` enum values (`PENDING_PAYMENT`, `PAID`, `CONFIRMED`, `PROCESSING`, `READY_TO_SHIP`, `SHIPPED`, `OUT_FOR_DELIVERY`, `DELIVERED`, `CANCELLED`, `REFUNDED`).
  - Allows admin to update `courier_name` and `tracking_number`.
  - Appends an entry to `OrderStatusHistory`.
  - Dispatches `dispatch_order_status_background(order.id, target_status, order.courier_name, order.tracking_number)`.

### 2.3 Webhook Infrastructure Audit
- **Payments**: `POST /api/v1/payments/webhook/{provider}` verifies HMAC SHA256 signatures (`x-razorpay-signature`) and processes events idempotently.
- **Logistics**: **No logistics webhooks exist**. There is no endpoint registered under `/api/v1/webhooks/shipping` or `/api/v1/shipping`.

### 2.4 Scheduled Jobs / Polling Audit
- There are no Celery, APScheduler, or cron jobs for polling external logistics tracking APIs. The application runs as a lightweight FastAPI service with asynchronous FastAPI `BackgroundTasks` for transactional email/SMS dispatch.

---

## 3. Integration Gap Analysis for Real Providers (Delhivery / Shiprocket / Blue Dart)

When Sulocraft integrates with a real logistics provider, the following architectural controls must be implemented:

| Requirement | Current State | Required Architecture |
| --- | --- | --- |
| **Provider Selection** | None (simulated local) | Shiprocket, Delhivery, or Blue Dart API client module |
| **Shipment Creation** | None | Admin action `POST /admin/orders/{id}/fulfill` to push order dimensions and pickup request to carrier |
| **Carrier Tracking Number** | Generated locally (`SLC-LOCAL-...`) | Saved from carrier API response (e.g., AWB / Waybill number) |
| **Webhook Receiver** | None | `POST /api/v1/shipping/webhook/{carrier}` with secret signature verification (e.g. HMAC or bearer token) |
| **Status Mapping** | Manual enum update | Mapping carrier status codes (e.g., `In Transit`, `Out for Delivery`, `Delivered`) to `OrderStatus` |
| **Idempotency** | Manual DB updates | Verify carrier event ID and skip already applied transitions to prevent duplicate history records |
| **Retry & Failure Handling** | None | Nonce/replay protection and webhook signature failure returning 400 |

---

## 4. Recommendations & Follow-Up Tasks

1. **Immediate (Work 017 Scope)**:
   - Keep status transitions admin-driven.
   - In frontend tracking UI (Tasks 17.2 & 17.3), render courier details directly from API without inventing external tracking URLs or pretending `SLC-LOCAL` is an external carrier AWB.
2. **Future Work Item (Automated Logistics Integration)**:
   - Propose a separate work item (e.g., `Work 018 — Logistics and automated carrier integration`):
     - Subtask 1: Select preferred provider (Shiprocket / Delhivery) and obtain sandbox API credentials via SOPS/age secrets.
     - Subtask 2: Implement carrier client for automated manifest creation upon `READY_TO_SHIP`.
     - Subtask 3: Implement authenticated, idempotent webhook receiver for carrier status events.

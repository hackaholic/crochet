# API Contract: Payment Abstraction & Gateway Flow

> **Status**: Approved & Published  
> **Source of Truth**: FastAPI backend (`/api/v1/payments`) and [`docs/openapi.yaml`](openapi.yaml)  
> **Backend Owner**: Gemini  
> **Frontend Consumer**: ChatGPT / Codex  

---

## 1. Overview & Payment Architecture

Conforming to **Section 25 (Payment Architecture)**, **Milestone 7**, and **DEC-007-6** of the [Multi-Agent Implementation Specification](SPECIFICATION.md):

* **Decoupled Architecture**: Orders are never tightly coupled to a single payment vendor. The `Payment` entity sits behind a `BasePaymentProvider` interface, supporting **Cashfree** (primary hosted web checkout & elements), **Mock** (local/CI), **Razorpay** (retained compatibility), and Cash on Delivery seamlessly.
* **Dual Currency Representation**: All payment amounts provide both integer rupees (`amount: 2599`) and integer paise (`amountPaise: 259900`) with `currency: "INR"`.
* **Zero-Credential Mock Gateway**: During local frontend development and CI/CD tests, the backend runs with the `MockPaymentProvider` by default. Any `provider_payment_id` (e.g. `pay_mock_12345`) verifies successfully, allowing the complete checkout experience without needing live gateway keys.
* **Selected Hosted Checkout Gateway (Cashfree)**: Setting `PAYMENT_PROVIDER=cashfree`, `CASHFREE_ENVIRONMENT=sandbox|production`, `CASHFREE_APP_ID`, and `CASHFREE_SECRET_KEY` (via secret-file/vault or environment) activates `CashfreePaymentProvider`. Orders are created server-side via Cashfree PG API (`v2023-08-01`), returning `paymentSessionId` and `environment` (`"sandbox"` | `"production"`) for Cashfree's JS SDK (`@cashfreepayments/cashfree-js` / `cashfree.checkout()` or Web Elements). Browser redirects alone never mark an order paid; `POST /api/v1/payments/verify` queries Cashfree server-side (`GET /pg/orders/{order_id}` and `/payments`) and only confirms the order when `order_status === "PAID"` with matching amount and currency. Webhooks at `POST /api/v1/payments/webhook/cashfree` verify `x-webhook-signature` and `x-webhook-timestamp` (`Base64(HMAC-SHA256(secret, timestamp + raw_body))`).
* **Retained Gateway (Razorpay)**: Setting `PAYMENT_PROVIDER=razorpay` with `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` remains supported for regression compatibility.
* **Order State Progression**:
  1. Customer checks out with an online payment method (`UPI`, `CARD`, `NETBANKING`).
  2. Order is created in `PENDING_PAYMENT` status with `payment_status: "PENDING"`.
  3. Frontend requests a payment intent via `POST /api/v1/payments/intent`.
  4. Customer completes payment via Cashfree Hosted Checkout / Web Elements (`paymentSessionId`), Razorpay modal, or Mock modal.
  5. Frontend invokes `POST /api/v1/payments/verify` with `{ "paymentId": intent.paymentId, "providerOrderId": intent.providerOrderId }` (for Cashfree, `providerPaymentId` is resolved server-side from Cashfree; for Mock/Razorpay, `providerPaymentId` and `providerSignature` are passed).
  6. Backend verifies payment status/signature, updates `Payment.status = "SUCCESS"`, transitions `Order.payment_status = "PAID"`, updates `Order.status = "CONFIRMED"`, and appends to `OrderStatusHistory`.

---

## 2. Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/payments/intent` | Create a gateway order/intent for an order in `PENDING_PAYMENT` status. |
| `POST` | `/api/v1/payments/verify` | Verify payment server-side (Cashfree) or client callback signature (Razorpay/Mock). Transitions order to `PAID` / `CONFIRMED`. |
| `POST` | `/api/v1/payments/webhook/{provider}` | Asynchronous webhook receiver for payment capture/failure events (`cashfree`, `razorpay`, `mock`). |
| `GET` | `/api/v1/payments/{payment_id}` | Retrieve payment status and details. |

---

## 3. TypeScript Interfaces for Frontend

```typescript
export interface PaymentIntentCreate {
  /** Database ID of the order */
  orderId?: number | null;
  /** Readable order number (e.g. "CB-20260930-84AF") */
  orderNumber?: string | null;
  /** Optional provider override ('cashfree', 'mock', or 'razorpay') */
  provider?: string | null;
}

export interface PaymentIntentOut {
  paymentId: number;
  orderId: number;
  orderNumber: string;
  provider: 'cashfree' | 'mock' | 'razorpay' | string;
  providerOrderId?: string | null;
  /** Cashfree payment_session_id passed to cashfree.checkout({ paymentSessionId }) */
  paymentSessionId?: string | null;
  /** Cashfree SDK mode ('sandbox' | 'production') */
  environment?: 'sandbox' | 'production' | string | null;
  /** Configured post-payment return URL (${FRONTEND_URL}/checkout?orderNumber=...&paymentId=...&cfOrderId=...) */
  returnUrl?: string | null;
  amount: number;
  amountPaise: number;
  currency: 'INR' | string;
  /** Public Gateway Key ID (used by Razorpay/Mock; null for Cashfree) */
  keyId?: string | null;
  notes: Record<string, any>;
}

export interface PaymentVerifyRequest {
  paymentId: number;
  /** Gateway payment ID (optional for Cashfree server-side verification; required for Mock/Razorpay) */
  providerPaymentId?: string | null;
  /** Gateway order ID */
  providerOrderId?: string | null;
  /** Signature returned by gateway modal callback (required for Razorpay) */
  providerSignature?: string | null;
  /** Optional payment method label, e.g. "UPI / Google Pay", "Visa ending in 4242" */
  paymentMethodDetail?: string | null;
}

export interface PaymentOut {
  id: number;
  orderId: number;
  provider: string;
  providerPaymentId?: string | null;
  providerOrderId?: string | null;
  amount: number;
  amountPaise: number;
  currency: string;
  status: 'PENDING' | 'SUCCESS' | 'FAILED' | 'REFUNDED';
  paymentMethodDetail?: string | null;
  createdAt: string;
  updatedAt: string;
}
```

---

## 4. End-to-End Frontend Integration Flow

### Step 1: Create Order with Online Payment
When placing order via `POST /api/v1/orders`:
```json
{
  "shippingAddress": {
    "name": "Sarah Connor",
    "phone": "9999977002",
    "line1": "Flat 402, Lotus Orchid",
    "city": "Bengaluru",
    "state": "Karnataka",
    "postalCode": "560038"
  },
  "paymentMethod": "UPI"
}
```
**Response returns order with status `PENDING_PAYMENT`:**
```json
{
  "id": 42,
  "orderNumber": "CB-20260930-84AF",
  "status": "PENDING_PAYMENT",
  "paymentStatus": "PENDING",
  "totalAmount": 2599,
  "totalAmountPaise": 259900
}
```

### Step 2: Request Payment Intent
Call `POST /api/v1/payments/intent` with credentials included:
```json
{
  "orderNumber": "CB-20260930-84AF"
}
```
**Cashfree Response (`201 Created`):**
```json
{
  "paymentId": 10,
  "orderId": 42,
  "orderNumber": "CB-20260930-84AF",
  "provider": "cashfree",
  "providerOrderId": "CB-20260930-84AF-10",
  "paymentSessionId": "session_cf_sandbox_a8b9c0d1e2f3",
  "environment": "sandbox",
  "returnUrl": "http://localhost:8080/checkout?orderNumber=CB-20260930-84AF&paymentId=10&cfOrderId=CB-20260930-84AF-10",
  "amount": 2599,
  "amountPaise": 259900,
  "currency": "INR",
  "keyId": null,
  "notes": {
    "orderNumber": "CB-20260930-84AF",
    "environment": "sandbox",
    "returnUrl": "http://localhost:8080/checkout?orderNumber=CB-20260930-84AF&paymentId=10&cfOrderId=CB-20260930-84AF-10"
  }
}
```

### Step 3: Trigger Gateway Checkout
* **Cashfree Hosted Checkout / Web Elements (`provider === "cashfree"`)**:
  Initialize the Cashfree v3 SDK using `load({ mode: intent.environment })` (`"sandbox"` | `"production"`), then call `cashfree.checkout({ paymentSessionId: intent.paymentSessionId, redirectTarget: "_self" })` (or `_modal` / Web Elements).
* **Mock / Local Development (`provider === "mock"`)**:
  Show the explicit local simulation modal with "Simulate Success" or "Simulate Failure" buttons.
* **Razorpay Compatibility (`provider === "razorpay"`)**:
  Open `new window.Razorpay(options).open()` with `options.key = intent.keyId`, `options.order_id = intent.providerOrderId`, `options.amount = intent.amountPaise`.

### Step 4: Verify Payment Server-Side (`POST /api/v1/payments/verify`)
* **Cashfree Verification Request** (after return redirect or modal completion — no client-invented transaction ID required):
```json
{
  "paymentId": 10,
  "providerOrderId": "CB-20260930-84AF-10"
}
```
* **Mock / Razorpay Verification Request**:
```json
{
  "paymentId": 10,
  "providerPaymentId": "pay_mock_success_12345",
  "providerOrderId": "mock_order_a8b9c0d1e2f3",
  "providerSignature": "mock_sig_valid",
  "paymentMethodDetail": "UPI / Google Pay"
}
```
**Verified Response (`200 OK`):**
```json
{
  "id": 10,
  "orderId": 42,
  "orderNumber": "CB-20260930-84AF",
  "provider": "cashfree",
  "providerPaymentId": "8877665544",
  "providerOrderId": "CB-20260930-84AF-10",
  "amount": 2599,
  "amountPaise": 259900,
  "currency": "INR",
  "status": "SUCCESS",
  "paymentMethodDetail": "Cashfree (UPI)",
  "createdAt": "2026-09-30T12:30:00Z",
  "updatedAt": "2026-09-30T12:30:05Z"
}
```
The order is now updated to `paymentStatus: "PAID"` and `status: "CONFIRMED"`, redirecting the customer to the Order Success / Tracking screen (`/orders/CB-20260930-84AF`). If Cashfree reports the order is still `ACTIVE` (pending), `POST /api/v1/payments/verify` returns `HTTP 400` and keeps `payment.status = "PENDING"` and `order.status = "PENDING_PAYMENT"`.

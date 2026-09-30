# API Contract: Payment Abstraction & Gateway Flow

> **Status**: Approved & Published  
> **Source of Truth**: FastAPI backend (`/api/v1/payments`) and [`docs/openapi.yaml`](openapi.yaml)  
> **Backend Owner**: Gemini  
> **Frontend Consumer**: ChatGPT / Codex  

---

## 1. Overview & Payment Architecture

Conforming to **Section 25 (Payment Architecture)** and **Milestone 7** of the [Multi-Agent Implementation Specification](SPECIFICATION.md):

* **Decoupled Architecture**: Orders are never tightly coupled to a single payment vendor. The `Payment` entity sits behind a `BasePaymentProvider` interface, supporting Razorpay, UPI, Netbanking, Cards, Cash on Delivery, and mock testing seamlessly.
* **Dual Currency Representation**: All payment amounts provide both integer rupees (`amount: 2599`) and integer paise (`amountPaise: 259900`) with `currency: "INR"`.
* **Zero-Credential Mock Gateway**: During local frontend development and CI/CD tests, the backend runs with the `MockPaymentProvider` by default. Any `provider_payment_id` (e.g. `pay_mock_12345`) verifies successfully, allowing the complete checkout experience without needing live gateway keys.
* **Production Gateway (Razorpay)**: Setting `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in the backend environment automatically activates the `RazorpayPaymentProvider` with cryptographic HMAC-SHA256 signature verification.
* **Order State Progression**:
  1. Customer checks out with an online payment method (`UPI`, `CARD`, `NETBANKING`).
  2. Order is created in `PENDING_PAYMENT` status with `payment_status: "PENDING"`.
  3. Frontend requests a payment intent via `POST /api/v1/payments/intent`.
  4. Customer completes payment via Razorpay modal (or mock modal).
  5. Frontend invokes `POST /api/v1/payments/verify` with gateway transaction ID & signature.
  6. Backend verifies signature, updates `Payment.status = "SUCCESS"`, transitions `Order.payment_status = "PAID"`, updates `Order.status = "CONFIRMED"`, and appends to `OrderStatusHistory`.

---

## 2. Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/payments/intent` | Create a gateway order/intent for an order in `PENDING_PAYMENT` status. |
| `POST` | `/api/v1/payments/verify` | Verify client callback payload/signature. Transitions order to `PAID` / `CONFIRMED`. |
| `POST` | `/api/v1/payments/webhook/{provider}` | Asynchronous webhook receiver for payment capture/failure events. |
| `GET` | `/api/v1/payments/{payment_id}` | Retrieve payment status and details. |

---

## 3. TypeScript Interfaces for Frontend

```typescript
export interface PaymentIntentCreate {
  /** Database ID of the order */
  orderId?: number | null;
  /** Readable order number (e.g. "CB-20260930-84AF") */
  orderNumber?: string | null;
  /** Optional provider override ('mock' or 'razorpay') */
  provider?: string | null;
}

export interface PaymentIntentOut {
  paymentId: number;
  orderId: number;
  orderNumber: string;
  provider: 'mock' | 'razorpay' | string;
  providerOrderId?: string | null;
  amount: number;
  amountPaise: number;
  currency: 'INR' | string;
  /** Public Gateway Key ID (e.g. Razorpay key id) for client checkout script */
  keyId?: string | null;
  notes: Record<string, any>;
}

export interface PaymentVerifyRequest {
  paymentId: number;
  /** Gateway payment ID (e.g. "pay_XXXXX" or "pay_mock_12345") */
  providerPaymentId: string;
  /** Gateway order ID */
  providerOrderId?: string | null;
  /** Signature returned by gateway modal callback */
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
**Response (`201 Created`):**
```json
{
  "paymentId": 10,
  "orderId": 42,
  "orderNumber": "CB-20260930-84AF",
  "provider": "mock",
  "providerOrderId": "mock_order_a8b9c0d1e2f3",
  "amount": 2599,
  "amountPaise": 259900,
  "currency": "INR",
  "keyId": "mock_key_crochet_bloom",
  "notes": {
    "orderNumber": "CB-20260930-84AF"
  }
}
```

### Step 3: Trigger Gateway Modal
* **Razorpay Production**: Open `new window.Razorpay(options).open()` with `options.key = intent.keyId`, `options.order_id = intent.providerOrderId`, `options.amount = intent.amountPaise`.
* **Mock / Development**: Show a local modal with "Simulate Success" or "Simulate Failure" buttons.

### Step 4: Verify Payment Callback
Upon successful modal callback:
```json
{
  "paymentId": 10,
  "providerPaymentId": "pay_mock_success_12345",
  "providerOrderId": "mock_order_a8b9c0d1e2f3",
  "providerSignature": "mock_sig_valid",
  "paymentMethodDetail": "UPI / Google Pay"
}
```
**Response (`200 OK`):**
```json
{
  "id": 10,
  "orderId": 42,
  "provider": "mock",
  "providerPaymentId": "pay_mock_success_12345",
  "providerOrderId": "mock_order_a8b9c0d1e2f3",
  "amount": 2599,
  "amountPaise": 259900,
  "currency": "INR",
  "status": "SUCCESS",
  "paymentMethodDetail": "UPI / Google Pay",
  "createdAt": "2026-09-30T12:30:00Z",
  "updatedAt": "2026-09-30T12:30:05Z"
}
```
The order is now updated to `paymentStatus: "PAID"` and `status: "CONFIRMED"`, redirecting the customer to the Order Success / Tracking screen (`/orders/CB-20260930-84AF`).

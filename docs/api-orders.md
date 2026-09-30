# API Contract: Addresses, Checkout & Order Tracking

> **Status**: Approved & Published  
> **Source of Truth**: FastAPI backend (`/api/v1/orders`, `/api/v1/addresses`) and [`docs/openapi.yaml`](openapi.yaml)  
> **Backend Owner**: Gemini  
> **Frontend Consumer**: ChatGPT / Codex  

---

## 1. Overview & Order Architecture

Conforming to **Sections 18, 20, 21, 22, and 26** of the [Multi-Agent Implementation Specification](SPECIFICATION.md):

* **Single-Step Checkout**: `POST /api/v1/orders` checks out the active shopping cart (anonymous guest or authenticated user), validating stock, computing server-side totals, snapshotting delivery address & line items, decrementing inventory, and converting the cart.
* **Price & Data Snapshots (Section 21)**: Order line items snapshot product name, slug, variant SKU, variant name, image, and unit price in integer rupees and paise. Even if products or prices change in the catalogue later, the historical order retains exact purchase-time prices.
* **Controlled Order State Model (Section 20)**:
  - `PENDING_PAYMENT`: Awaiting online payment confirmation.
  - `CONFIRMED`: Order confirmed (default for Cash on Delivery / COD).
  - `PROCESSING`: Handcrafted item being crocheted / prepared.
  - `READY_TO_SHIP`: Packaged and awaiting courier pickup.
  - `SHIPPED`: In transit with courier tracking number.
  - `OUT_FOR_DELIVERY`: Out for final delivery.
  - `DELIVERED`: Delivered to recipient.
  - `CANCELLED`: Cancelled before dispatch (inventory automatically restored).
  - `REFUNDED`: Payment returned to customer.
* **Address Architecture (Section 26)**: Users can save multiple addresses (`home`, `office`) with a default address flag. Orders snapshot the shipping address at checkout time, ensuring future address edits do not mutate past orders.
* **Dual Currency Representation**: All order amounts provide dual integer representation: `subtotal`, `subtotalPaise`, `shippingFee`, `shippingFeePaise`, `totalAmount`, `totalAmountPaise` (`currency: "INR"`).
* **Customer Authorization Security (Section 22)**: Private orders and tracking endpoints verify customer ownership (`order.user_id == current_user.id`), returning safe 404 responses for unauthorized attempts.

---

## 2. Endpoints Summary

### Address Management

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/addresses` | List saved delivery addresses for the logged-in customer. |
| `POST` | `/api/v1/addresses` | Save a new delivery address. |
| `PATCH` | `/api/v1/addresses/{id}` | Update an existing saved address. |
| `DELETE` | `/api/v1/addresses/{id}` | Delete a saved address. |
| `POST` | `/api/v1/addresses/{id}/default` | Set address as the default delivery address. |

### Checkout & Orders

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/orders` | Place order from active cart. Snapshots items, decrements stock, clears cart. |
| `GET` | `/api/v1/orders` | List order history for the logged-in customer with pagination. |
| `GET` | `/api/v1/orders/{order_id_or_number}` | Get full order details. Supports integer DB ID or order number string (`CB-YYYYMMDD-XXXX`). |
| `GET` | `/api/v1/orders/{order_id_or_number}/tracking` | Track order status and chronological timeline. |
| `POST` | `/api/v1/orders/{order_id_or_number}/cancel` | Cancel order before shipment. Restores variant inventory. |

---

## 3. TypeScript Interfaces for Frontend

```typescript
export interface AddressCreate {
  name: string;
  phone: string;
  line1: string;
  line2?: string | null;
  landmark?: string | null;
  city: string;
  state: string;
  postalCode: string;
  country?: string;
  isDefault?: boolean;
}

export interface AddressUpdate {
  name?: string;
  phone?: string;
  line1?: string;
  line2?: string | null;
  landmark?: string | null;
  city?: string;
  state?: string;
  postalCode?: string;
  country?: string;
  isDefault?: boolean;
}

export interface AddressOut {
  id: number;
  userId: number;
  name: string;
  phone: string;
  line1: string;
  line2?: string | null;
  landmark?: string | null;
  city: string;
  state: string;
  postalCode: string;
  country: string;
  isDefault: boolean;
  createdAt: string;
}

export interface OrderCreate {
  addressId?: number | null;
  shippingAddress?: AddressCreate | null;
  paymentMethod?: 'COD' | 'UPI' | 'CARD' | 'NETBANKING';
  customerName?: string | null;
  customerPhone?: string | null;
  customerEmail?: string | null;
  notes?: string | null;
}

export interface OrderItemOut {
  id: number;
  orderId: number;
  productId?: number | null;
  productVariantId?: number | null;
  productName: string;
  productSlug?: string | null;
  sku: string;
  variantName: string;
  productImage?: string | null;
  unitPrice: number;
  unitPricePaise: number;
  quantity: number;
  lineTotal: number;
  lineTotalPaise: number;
  personalization: Record<string, any>;
}

export interface OrderStatusHistoryOut {
  id: number;
  status: string;
  note?: string | null;
  timestamp: string;
}

export interface OrderOut {
  id: number;
  orderNumber: string;
  userId?: number | null;
  customerName: string;
  customerPhone: string;
  customerEmail?: string | null;
  shippingAddress: Record<string, any>;
  billingAddress?: Record<string, any> | null;
  status: 'PENDING_PAYMENT' | 'PAID' | 'CONFIRMED' | 'PROCESSING' | 'READY_TO_SHIP' | 'SHIPPED' | 'OUT_FOR_DELIVERY' | 'DELIVERED' | 'CANCELLED' | 'REFUNDED';
  paymentStatus: 'PENDING' | 'PAID' | 'FAILED' | 'REFUNDED';
  paymentMethod: string;
  currency: string;
  subtotal: number;
  subtotalPaise: number;
  shippingFee: number;
  shippingFeePaise: number;
  discountAmount: number;
  discountAmountPaise: number;
  taxAmount: number;
  taxAmountPaise: number;
  totalAmount: number;
  totalAmountPaise: number;
  notes?: string | null;
  items: OrderItemOut[];
  statusHistory: OrderStatusHistoryOut[];
  trackingNumber?: string | null;
  courierName?: string | null;
  estimatedDelivery?: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface OrderTrackingOut {
  orderNumber: string;
  status: string;
  paymentStatus: string;
  trackingNumber?: string | null;
  courierName?: string | null;
  estimatedDelivery?: string | null;
  timeline: OrderStatusHistoryOut[];
}
```

---

## 4. Request / Response Examples

### 1. `POST /api/v1/orders` (Checkout)

**Request with saved address:**
```json
{
  "addressId": 1,
  "paymentMethod": "COD",
  "notes": "Handle with care - fragile handmade gift"
}
```

**Request with inline address:**
```json
{
  "shippingAddress": {
    "name": "Sarah Connor",
    "phone": "9999900002",
    "line1": "Flat 402, Lotus Orchid",
    "city": "Bengaluru",
    "state": "Karnataka",
    "postalCode": "560038"
  },
  "paymentMethod": "COD"
}
```

**Response (`201 Created`):**
```json
{
  "id": 1,
  "orderNumber": "CB-20260930-84AF",
  "userId": 1,
  "customerName": "Sarah Connor",
  "customerPhone": "9999900002",
  "customerEmail": null,
  "shippingAddress": {
    "name": "Sarah Connor",
    "phone": "9999900002",
    "line1": "Flat 402, Lotus Orchid",
    "line2": null,
    "landmark": null,
    "city": "Bengaluru",
    "state": "Karnataka",
    "postalCode": "560038",
    "country": "IN"
  },
  "billingAddress": {
    "name": "Sarah Connor",
    "phone": "9999900002",
    "line1": "Flat 402, Lotus Orchid",
    "line2": null,
    "landmark": null,
    "city": "Bengaluru",
    "state": "Karnataka",
    "postalCode": "560038",
    "country": "IN"
  },
  "status": "CONFIRMED",
  "paymentStatus": "PENDING",
  "paymentMethod": "COD",
  "currency": "INR",
  "subtotal": 2599,
  "subtotalPaise": 259900,
  "shippingFee": 0,
  "shippingFeePaise": 0,
  "discountAmount": 0,
  "discountAmountPaise": 0,
  "taxAmount": 0,
  "taxAmountPaise": 0,
  "totalAmount": 2599,
  "totalAmountPaise": 259900,
  "notes": "Handle with care - fragile handmade gift",
  "items": [
    {
      "id": 1,
      "orderId": 1,
      "productId": 1,
      "productVariantId": 1,
      "productName": "Forever Crochet Rose Bouquet",
      "productSlug": "forever-crochet-rose-bouquet",
      "sku": "FLR-ROSE-RED-5S",
      "variantName": "5 Roses / Deep Crimson",
      "productImage": "https://images.unsplash.com/photo-1700171518313-5dd219beaaa6?w=600&h=600&fit=crop&auto=format",
      "unitPrice": 2599,
      "unitPricePaise": 259900,
      "quantity": 1,
      "lineTotal": 2599,
      "lineTotalPaise": 259900,
      "personalization": {
        "gift_message": "Happy 5th Anniversary!"
      }
    }
  ],
  "statusHistory": [
    {
      "id": 1,
      "status": "CONFIRMED",
      "note": "Order confirmed with Cash on Delivery.",
      "timestamp": "2026-09-30T12:00:00Z"
    }
  ],
  "trackingNumber": null,
  "courierName": null,
  "estimatedDelivery": "2026-10-05T12:00:00Z",
  "createdAt": "2026-09-30T12:00:00Z",
  "updatedAt": "2026-09-30T12:00:00Z"
}
```

### 2. `GET /api/v1/orders/{order_number}/tracking`

**Response (`200 OK`):**
```json
{
  "orderNumber": "CB-20260930-84AF",
  "status": "CONFIRMED",
  "paymentStatus": "PENDING",
  "trackingNumber": null,
  "courierName": null,
  "estimatedDelivery": "2026-10-05T12:00:00Z",
  "timeline": [
    {
      "id": 1,
      "status": "CONFIRMED",
      "note": "Order confirmed with Cash on Delivery.",
      "timestamp": "2026-09-30T12:00:00Z"
    }
  ]
}
```

### 3. `POST /api/v1/orders/{order_number}/cancel`

Cancels the order, returns inventory to stock, and adds cancellation to status history.
**Response (`200 OK`):**
```json
{
  "orderNumber": "CB-20260930-84AF",
  "status": "CANCELLED",
  "statusHistory": [
    {
      "id": 1,
      "status": "CONFIRMED",
      "note": "Order confirmed with Cash on Delivery.",
      "timestamp": "2026-09-30T12:00:00Z"
    },
    {
      "id": 2,
      "status": "CANCELLED",
      "note": "Order cancelled by customer.",
      "timestamp": "2026-09-30T12:15:00Z"
    }
  ]
}
```

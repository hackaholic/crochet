# Promotions, Coupons & Product Reviews API Guide

> **Source of Truth**: FastAPI backend (`/api/v1/cart`, `/api/v1/orders`, `/api/v1/products`, `/api/v1/admin`) and [`docs/openapi.yaml`](openapi.yaml)  
> **Status**: Ready for Integration  
> **Currency Handling**: Dual representation across all monetary values: integer INR Rupees (e.g. `discountAmount: 200`) and integer paise (e.g. `discountAmountPaise: 20000`).

---

## 1. Overview & Flow

Milestone 10 introduces:
1. **Promo Coupons Engine**:
   - Customers apply coupons directly in the shopping cart (`POST /api/v1/cart/apply-coupon`) to preview discounts.
   - Removing coupons from the cart session (`DELETE /api/v1/cart/coupon`).
   - Checkout integration (`POST /api/v1/orders` with `couponCode`): validates coupon, computes discount, snapshots `discountAmount` and `discountAmountPaise`, and increments the coupon's `usageCount`.
   - Admin coupon management (`/api/v1/admin/coupons`): create, list, inspect, update, and delete coupons.
2. **Customer Reviews & Moderation**:
   - Authenticated customers can submit product reviews (`POST /api/v1/products/{slug_or_id}/reviews`).
   - Dynamic aggregate rating and reviews count recalculation on every submission.
   - Admin moderation (`/api/v1/admin/reviews`): list all reviews across products with star-rating filters, and permanently remove abusive/spam reviews.

---

## 2. TypeScript Contracts

```typescript
// -----------------------------------------------------------------------------
// Coupons (Customer & Admin)
// -----------------------------------------------------------------------------

export type DiscountType = 'PERCENTAGE' | 'FLAT';

export interface CouponApplyRequest {
  code: string; // e.g. "SAVE10" or "WELCOME100"
}

export interface CouponApplyResponse {
  code: string;
  discountType: DiscountType;
  discountValue: number;
  discountAmount: number; // In INR Rupees
  discountAmountPaise: number; // In Paise
  subtotalBeforeDiscount: number;
  subtotalAfterDiscount: number;
  subtotalAfterDiscountPaise: number;
  message: string;
}

export interface AdminCouponCreate {
  code: string;
  description?: string | null;
  discountType: DiscountType;
  discountValue: number; // % value or INR Rupee value
  minOrderAmount?: number; // In INR Rupees (default: 0)
  maxDiscountAmount?: number | null; // Cap for percentage discount in INR Rupees
  usageLimit?: number | null; // Maximum lifetime usage count
  validUntil?: string | null; // ISO 8601 UTC timestamp
  isActive?: boolean; // Default: true
}

export interface AdminCouponUpdate {
  description?: string | null;
  discountType?: DiscountType;
  discountValue?: number;
  minOrderAmount?: number;
  maxDiscountAmount?: number | null;
  usageLimit?: number | null;
  validUntil?: string | null;
  isActive?: boolean;
}

export interface AdminCouponOut {
  id: number;
  code: string;
  description?: string | null;
  discountType: DiscountType;
  discountValue: number;
  minOrderAmount: number;
  maxDiscountAmount?: number | null;
  usageLimit?: number | null;
  usageCount: number;
  validFrom: string;
  validUntil?: string | null;
  isActive: boolean;
  createdAt: string;
}

// -----------------------------------------------------------------------------
// Reviews (Customer & Admin)
// -----------------------------------------------------------------------------

export interface ReviewCreateRequest {
  rating: number; // 1 to 5
  text: string; // Customer testimonial or feedback
  authorName?: string | null; // Optional override display name
  location?: string | null; // City or region, e.g. "Bengaluru"
}

export interface ReviewOut {
  id: number;
  productId?: number | null;
  productName?: string | null;
  authorName: string;
  name: string; // Compatibility alias for frontend components
  location?: string | null;
  rating: number;
  text: string;
  image?: string | null;
  avatarUrl?: string | null;
  date?: string | null;
}

export interface AdminReviewOut {
  id: number;
  productId?: number | null;
  productName?: string | null;
  productSlug?: string | null;
  authorName: string;
  location?: string | null;
  rating: number;
  text: string;
  avatarUrl?: string | null;
  date?: string | null;
}
```

---

## 3. Customer Endpoints

### 3.1 Apply Coupon to Cart
- **Endpoint**: `POST /api/v1/cart/apply-coupon`
- **Auth**: Optional (works for both Guest Cart cookies and Authenticated sessions)
- **Request Body**:
  ```json
  {
    "code": "SAVE10"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "code": "SAVE10",
    "discountType": "PERCENTAGE",
    "discountValue": 10,
    "discountAmount": 200,
    "discountAmountPaise": 20000,
    "subtotalBeforeDiscount": 2599,
    "subtotalAfterDiscount": 2399,
    "subtotalAfterDiscountPaise": 239900,
    "message": "Coupon 'SAVE10' applied: ₹200 discount"
  }
  ```
- **Error Codes**:
  - `400 Bad Request`: Cart is empty, coupon has expired, usage limit reached, or cart subtotal does not meet `minOrderAmount`.
  - `404 Not Found`: Coupon code does not exist or is inactive.

### 3.2 Remove Coupon from Cart
- **Endpoint**: `DELETE /api/v1/cart/coupon`
- **Response** (`200 OK`):
  ```json
  {
    "message": "Coupon removed from cart"
  }
  ```

### 3.3 Checkout with Coupon
- **Endpoint**: `POST /api/v1/orders`
- **Request Body**: Include optional `couponCode`:
  ```json
  {
    "paymentMethod": "COD",
    "couponCode": "SAVE10",
    "shippingAddress": {
      "name": "Ananya Sharma",
      "phone": "9999911005",
      "line1": "123 Residency Road",
      "city": "Bengaluru",
      "state": "Karnataka",
      "postalCode": "560025"
    }
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "orderNumber": "CB-20260930-A1B2",
    "subtotal": 2599,
    "subtotalPaise": 259900,
    "discountAmount": 200,
    "discountAmountPaise": 20000,
    "shippingFee": 0,
    "totalAmount": 2399,
    "totalAmountPaise": 239900,
    "currency": "INR",
    "paymentMethod": "COD"
  }
  ```

### 3.4 Submit Product Review
- **Endpoint**: `POST /api/v1/products/{slug_or_id}/reviews`
- **Auth**: Required (`session_token` cookie, `credentials: 'include'`)
- **Request Body**:
  ```json
  {
    "rating": 5,
    "text": "The craftsmanship on this forever rose is genuinely unmatched!",
    "location": "Mumbai"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "id": 7,
    "productId": 1,
    "productName": "Forever Crochet Rose Bouquet",
    "authorName": "Ananya Sharma",
    "name": "Ananya Sharma",
    "location": "Mumbai",
    "rating": 5,
    "text": "The craftsmanship on this forever rose is genuinely unmatched!",
    "avatarUrl": null,
    "image": null,
    "date": "Sep 2026"
  }
  ```

---

## 4. Admin Management Endpoints

All admin endpoints require `role == "ADMIN"` and `credentials: 'include'`.

### 4.1 Admin Coupon Management
- **List Coupons**: `GET /api/v1/admin/coupons?active_only=false&search=SAVE`
- **Create Coupon**: `POST /api/v1/admin/coupons`
- **Get Coupon**: `GET /api/v1/admin/coupons/{id}`
- **Update Coupon**: `PATCH /api/v1/admin/coupons/{id}`
- **Delete Coupon**: `DELETE /api/v1/admin/coupons/{id}`

### 4.2 Admin Review Moderation
- **List Reviews**: `GET /api/v1/admin/reviews?product_id=1&min_rating=1`
- **Delete Review**: `DELETE /api/v1/admin/reviews/{id}` (automatically decrements review count and recalculates product average star rating).

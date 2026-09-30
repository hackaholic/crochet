# API Contract: Shopping Cart & Guest Cart Engine

> **Status**: Approved & Published  
> **Source of Truth**: FastAPI backend (`/api/v1/cart`) and [`docs/openapi.yaml`](openapi.yaml)  
> **Backend Owner**: Gemini  
> **Frontend Consumer**: ChatGPT  

---

## 1. Overview & Authentication / Guest Architecture

Conforming to **Sections 6, 7, 18, and 28** of the [Multi-Agent Implementation Specification](SPECIFICATION.md):

* **Anonymous Users**: Visitors can browse and add items to their cart anonymously without logging in.
* **Cookie Management**: When an item is first added to the cart, the backend automatically issues an `HttpOnly`, `SameSite=Lax`, 30-day cookie:
  ```http
  Set-Cookie: guest_cart_token=<random_secure_token>; Max-Age=2592000; Path=/; HttpOnly; SameSite=Lax
  ```
* **Frontend Fetch Requirement**: When making API calls from React, include cookies by setting `credentials: 'include'`:
  ```typescript
  fetch('http://localhost:8000/api/v1/cart', {
    credentials: 'include',
  });
  ```
* **Header Fallback**: The API also accepts the header `X-Cart-Token: <token>` for environments where third-party cookies might be blocked during local development.
* **Deterministic Merge**: When a user logs in, `POST /api/v1/cart/merge` merges the guest cart into the customer's cart:
  $$\text{quantity} = \min(\text{guest\_quantity} + \text{existing\_quantity}, \text{stock\_quantity})$$

---

## 2. Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/cart` | Get current cart. Returns empty cart representation if no cart exists. |
| `POST` | `/api/v1/cart/items` | Add item/variant with quantity and personalization. Sets cookie. |
| `PATCH` | `/api/v1/cart/items/{item_id}` | Update quantity or personalization notes of a line item. |
| `DELETE` | `/api/v1/cart/items/{item_id}` | Remove a single line item. |
| `DELETE` | `/api/v1/cart` | Clear entire cart. |
| `POST` | `/api/v1/cart/merge` | Merge an anonymous guest cart into the active session cart. |

---

## 3. TypeScript Interfaces for Frontend

```typescript
export interface CartItemAdd {
  /** Optional: specific variant ID to add */
  product_variant_id?: number;
  /** Optional: product ID (auto-resolves to primary variant if product_variant_id omitted) */
  product_id?: number;
  /** Optional: SKU string (alternative to variant ID) */
  sku?: string;
  /** Quantity to add (default 1, max 99) */
  quantity?: number;
  /** Custom personalization options (e.g. gift_message, custom_color) */
  personalization?: Record<string, any>;
}

export interface CartItemUpdate {
  quantity: number;
  personalization?: Record<string, any>;
}

export interface CartItemOut {
  id: number;
  productId: number;
  productName: string;
  productSlug: string;
  productImage: string;
  variantId: number;
  variantSku: string;
  variantName: string;
  unitPrice: number;
  compareAtPrice?: number | null;
  quantity: number;
  lineTotal: number;
  personalization: Record<string, any>;
  stockAvailable: number;
}

export interface CartOut {
  id?: number | null;
  guestToken?: string | null;
  items: CartItemOut[];
  itemCount: number;
  subtotal: number;
  status: 'ACTIVE' | 'CONVERTED' | 'ABANDONED';
}

export interface CartMergeRequest {
  guest_token: string;
}
```

---

## 4. Examples

### 1. `GET /api/v1/cart`
If no cart cookie is provided, returns an empty cart object (status `200 OK`):
```json
{
  "id": null,
  "guestToken": null,
  "items": [],
  "itemCount": 0,
  "subtotal": 0,
  "status": "ACTIVE"
}
```

### 2. `POST /api/v1/cart/items`
Add a product or variant:
```json
{
  "product_id": 1,
  "quantity": 1,
  "personalization": {
    "gift_message": "Happy 5th Anniversary!"
  }
}
```
**Response (`201 Created`):**
```json
{
  "id": 1,
  "guestToken": "6k5avr_wuU6Xl3ROBXFfvLgDly3fgQabUyHUfAraMGg",
  "items": [
    {
      "id": 1,
      "productId": 1,
      "productName": "Forever Crochet Rose Bouquet",
      "productSlug": "forever-crochet-rose-bouquet",
      "productImage": "https://images.unsplash.com/photo-1700171518313-5dd219beaaa6?w=600&h=600&fit=crop&auto=format",
      "variantId": 1,
      "variantSku": "FLR-ROSE-RED-5S",
      "variantName": "5 Roses / Deep Crimson",
      "unitPrice": 2599,
      "compareAtPrice": null,
      "quantity": 1,
      "lineTotal": 2599,
      "personalization": {
        "gift_message": "Happy 5th Anniversary!"
      },
      "stockAvailable": 15
    }
  ],
  "itemCount": 1,
  "subtotal": 2599,
  "status": "ACTIVE"
}
```

### 3. `PATCH /api/v1/cart/items/{item_id}`
Update quantity:
```json
{
  "quantity": 2
}
```

### 4. `DELETE /api/v1/cart/items/{item_id}`
Deletes line item and returns updated `CartOut`.

### 5. `DELETE /api/v1/cart`
Clears all items in the cart and returns empty `CartOut`.

# API Contract: Customer Account, Profile & Wishlist

> **Status**: Approved & Published  
> **Source of Truth**: FastAPI backend (`/api/v1/account`, `/api/v1/wishlist`) and [`docs/openapi.yaml`](openapi.yaml)  
> **Backend Owner**: Gemini  
> **Frontend Consumer**: ChatGPT / Codex  

---

## 1. Overview & Account Architecture

Conforming to **Section 19 (Customer Account)** and **Section 27 (Wishlist)** of the [Multi-Agent Implementation Specification](SPECIFICATION.md):

* **Customer Account Dashboard**: After logging in, customers access a unified account center:
  ```text
  My Account
  ├── Profile (Edit name, email)
  ├── My Orders (Order history & tracking via /api/v1/orders)
  ├── Saved Addresses (Address book via /api/v1/addresses)
  ├── Wishlist (Persistent cross-device favorites via /api/v1/wishlist)
  └── Overview (Aggregated dashboard metrics: orders count, active orders, saved addresses count, wishlist items)
  ```
* **Persistent Wishlist**: When customers browse products, clicking the heart icon saves items to their database-backed wishlist, syncing across devices and browser sessions.
* **Dual Currency Representation**: All product listings inside the wishlist provide both integer rupees (`price`) and integer paise (`pricePaise`), plus `currency: "INR"`.
* **Seamless ID & Slug Support**: Adding or removing items accepts either integer product ID (`productId: 1`) or slug string (`productSlug: "forever-crochet-rose-bouquet"`).

---

## 2. Endpoints Summary

### Profile & Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/account/profile` | Retrieve profile information for the authenticated customer. |
| `PATCH` | `/api/v1/account/profile` | Update profile information (name, email). |
| `GET` | `/api/v1/account/overview` | Aggregated dashboard metrics (orders, active shipments, addresses, wishlist count). |

### Wishlist (Section 27)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/wishlist` | Retrieve all bookmarked products saved in the customer's wishlist. |
| `POST` | `/api/v1/wishlist/items` | Add a product to the wishlist by `productId` or `productSlug` (idempotent). |
| `DELETE` | `/api/v1/wishlist/items/{product_id_or_slug}` | Remove an individual product from the wishlist. |
| `DELETE` | `/api/v1/wishlist` | Clear all items from the customer's wishlist. |

---

## 3. TypeScript Interfaces for Frontend

```typescript
export interface ProfileUpdate {
  name?: string | null;
  email?: string | null;
}

export interface ProfileOut {
  id: number;
  name?: string | null;
  email?: string | null;
  phone?: string | null;
  status: string;
  identities: string[];
  createdAt: string;
  lastLoginAt?: string | null;
}

export interface AccountOverviewOut {
  profile: ProfileOut;
  totalOrders: number;
  activeOrders: number;
  savedAddresses: number;
  wishlistItemsCount: number;
}

export interface WishlistItemAdd {
  productId?: number | null;
  productSlug?: string | null;
}

export interface WishlistItemOut {
  id: number;
  productId: number;
  productName: string;
  productSlug: string;
  productImage: string;
  price: number;
  pricePaise: number;
  compareAtPrice?: number | null;
  originalPrice?: number | null;
  badge?: string | null;
  category: string;
  inStock: boolean;
  rating: number;
  reviews: number;
  createdAt: string;
}

export interface WishlistOut {
  items: WishlistItemOut[];
  totalItems: number;
}
```

---

## 4. Request / Response Examples

### 1. `GET /api/v1/account/overview`
**Response (`200 OK`):**
```json
{
  "profile": {
    "id": 1,
    "name": "Priya Sharma",
    "email": "priya@example.com",
    "phone": "+919876543210",
    "status": "ACTIVE",
    "identities": ["phone"],
    "createdAt": "2026-09-30T12:00:00Z",
    "lastLoginAt": "2026-09-30T12:30:00Z"
  },
  "totalOrders": 3,
  "activeOrders": 1,
  "savedAddresses": 2,
  "wishlistItemsCount": 4
}
```

### 2. `POST /api/v1/wishlist/items`
**Request by product ID:**
```json
{
  "productId": 1
}
```
**Request by slug:**
```json
{
  "productSlug": "crochet-tulip-bouquet"
}
```

**Response (`201 Created`):**
```json
{
  "items": [
    {
      "id": 1,
      "productId": 1,
      "productName": "Forever Crochet Rose Bouquet",
      "productSlug": "forever-crochet-rose-bouquet",
      "productImage": "https://images.unsplash.com/photo-1700171518313-5dd219beaaa6?w=600&h=600&fit=crop&auto=format",
      "price": 2599,
      "pricePaise": 259900,
      "compareAtPrice": null,
      "originalPrice": null,
      "badge": "Bestseller",
      "category": "Flowers",
      "inStock": true,
      "rating": 4.9,
      "reviews": 128,
      "createdAt": "2026-09-30T12:35:00Z"
    }
  ],
  "totalItems": 1
}
```

### 3. `DELETE /api/v1/wishlist/items/{product_id_or_slug}`
Removes the product from wishlist and returns updated `WishlistOut`.

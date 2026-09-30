# Admin API Integration Guide

> **Source of Truth**: FastAPI backend (`/api/v1/admin`) and [`docs/openapi.yaml`](openapi.yaml)  
> **Status**: Ready for Integration  
> **Security**: Role-Based Access Control (`role == "ADMIN"`). Unauthenticated calls return `401`, non-admin users return `403`.

---

## 1. Authentication & RBAC

All routes mounted under `/api/v1/admin` require an authenticated session belonging to a user with administrative privileges (`role == "ADMIN"`).

### Development Admin Credentials
For testing and frontend integration in local/staging environments, use the seeded admin phone number:
- **Phone**: `9999900000`
- **OTP**: `123456`
- **Endpoint**: `POST /api/v1/auth/phone/verify-otp`

Browser sessions will automatically receive the `session_token` cookie with `HttpOnly; SameSite=Lax`. All fetch requests must include `credentials: 'include'`.

---

## 2. TypeScript Contracts

```typescript
// -----------------------------------------------------------------------------
// Products & Variants
// -----------------------------------------------------------------------------

export interface AdminVariantCreate {
  sku: string;
  name?: string; // Default: 'Default'
  price: number; // In INR Rupees
  compareAtPrice?: number | null;
  cost?: number | null;
  stockQuantity?: number; // Default: 10
  weight?: number | null;
  attributes?: Record<string, any>;
}

export interface AdminVariantUpdate {
  sku?: string;
  name?: string;
  price?: number;
  compareAtPrice?: number | null;
  cost?: number | null;
  stockQuantity?: number | null;
  weight?: number | null;
  status?: string;
  attributes?: Record<string, any>;
}

export interface AdminVariantOut {
  id: number;
  productId: number;
  sku: string;
  name: string;
  price: number;
  pricePaise: number;
  compareAtPrice?: number | null;
  compareAtPricePaise?: number | null;
  cost?: number | null;
  stockQuantity: number;
  weight?: number | null;
  status: string; // ACTIVE, INACTIVE
  attributes: Record<string, any>;
  createdAt?: string;
  updatedAt?: string;
}

export interface AdminProductCreate {
  name: string;
  slug?: string; // Auto-generated if omitted
  shortDescription?: string;
  description?: string;
  brand?: string; // Default: 'Crochet Bloom'
  primaryImage: string;
  badge?: string; // 'Bestseller', 'New', 'Limited Edition', etc.
  customizable?: boolean;
  categoryIds?: number[];
  tagIds?: number[];
  galleryImages?: string[];
  variants?: AdminVariantCreate[];
  metadata?: Record<string, any>;
}

export interface AdminProductUpdate {
  name?: string;
  slug?: string;
  shortDescription?: string;
  description?: string;
  status?: string; // ACTIVE, DRAFT, ARCHIVED
  brand?: string;
  primaryImage?: string;
  badge?: string;
  customizable?: boolean;
  categoryIds?: number[];
  tagIds?: number[];
  galleryImages?: string[];
  metadata?: Record<string, any>;
}

export interface AdminProductOut {
  id: number;
  name: string;
  slug: string;
  shortDescription?: string;
  description?: string;
  status: string; // ACTIVE, DRAFT, ARCHIVED
  brand: string;
  primaryImage: string;
  badge?: string;
  customizable: boolean;
  rating: number;
  reviewsCount: number;
  categoryIds: number[];
  categoryNames: string[];
  tagIds: number[];
  tagNames: string[];
  galleryImages: string[];
  variants: AdminVariantOut[];
  totalStock: number;
  minPrice: number;
  minPricePaise: number;
  createdAt?: string;
  updatedAt?: string;
}

export interface AdminProductListOut {
  items: AdminProductOut[];
  total: number;
  page: number;
  pageSize: number;
}

// -----------------------------------------------------------------------------
// Inventory Adjustment
// -----------------------------------------------------------------------------

export interface AdminInventoryAdjustRequest {
  stockQuantity?: number; // Absolute override
  adjustment?: number; // Relative delta (+5, -2)
  reason?: string;
}

// -----------------------------------------------------------------------------
// Orders Administration
// -----------------------------------------------------------------------------

export type OrderStatus =
  | 'PENDING_PAYMENT'
  | 'PAID'
  | 'CONFIRMED'
  | 'PROCESSING'
  | 'READY_TO_SHIP'
  | 'SHIPPED'
  | 'OUT_FOR_DELIVERY'
  | 'DELIVERED'
  | 'CANCELLED'
  | 'REFUNDED';

export interface AdminOrderStatusUpdate {
  status: OrderStatus;
  trackingNumber?: string;
  courierName?: string;
  note?: string;
}

export interface AdminOrderItemOut {
  id: number;
  productId?: number;
  variantId?: number;
  productName: string;
  productSlug?: string;
  sku: string;
  variantName: string;
  productImage?: string;
  unitPrice: number;
  unitPricePaise: number;
  quantity: number;
  lineTotal: number;
  lineTotalPaise: number;
  personalization: Record<string, any>;
}

export interface AdminOrderDetailOut {
  id: number;
  orderNumber: string;
  customerName: string;
  customerPhone: string;
  customerEmail?: string;
  status: OrderStatus;
  paymentStatus: string;
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
  shippingAddress: Record<string, any>;
  billingAddress?: Record<string, any>;
  trackingNumber?: string;
  courierName?: string;
  notes?: string;
  items: AdminOrderItemOut[];
  statusHistory: Array<{
    id: number;
    status: string;
    note?: string;
    timestamp?: string;
  }>;
  createdAt: string;
  updatedAt: string;
}

export interface AdminOrderListOut {
  items: AdminOrderDetailOut[];
  total: number;
  page: number;
  pageSize: number;
}

// -----------------------------------------------------------------------------
// Store Analytics & Dashboard
// -----------------------------------------------------------------------------

export interface AdminLowStockItem {
  variantId: number;
  productId: number;
  productName: string;
  sku: string;
  variantName: string;
  stockQuantity: number;
}

export interface AdminTopSellingProduct {
  productId: number;
  productName: string;
  totalSold: number;
  totalRevenue: number;
  totalRevenuePaise: number;
}

export interface AdminAnalyticsOut {
  totalRevenue: number;
  totalRevenuePaise: number;
  totalOrders: number;
  pendingOrders: number;
  deliveredOrders: number;
  cancelledOrders: number;
  totalCustomers: number;
  totalProducts: number;
  lowStockCount: number;
  lowStockItems: AdminLowStockItem[];
  recentOrders: AdminOrderDetailOut[];
  topSellingProducts: AdminTopSellingProduct[];
}
```

---

## 3. Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/admin/products` | List products with pagination, search, status, and category filtering |
| `POST` | `/api/v1/admin/products` | Create a new product with variants and images |
| `GET` | `/api/v1/admin/products/{id}` | Get product details |
| `PATCH` | `/api/v1/admin/products/{id}` | Update product details |
| `DELETE` | `/api/v1/admin/products/{id}` | Soft delete product (`status="ARCHIVED"`) |
| `POST` | `/api/v1/admin/products/{id}/variants` | Add variant to product |
| `PATCH` | `/api/v1/admin/variants/{id}` | Update variant pricing, SKU, or attributes |
| `PATCH` | `/api/v1/admin/variants/{id}/inventory` | Adjust variant inventory (absolute or delta) |
| `DELETE` | `/api/v1/admin/variants/{id}` | Delete variant |
| `POST` | `/api/v1/admin/categories` | Create taxonomy category |
| `PATCH` | `/api/v1/admin/categories/{id}` | Update taxonomy category |
| `DELETE` | `/api/v1/admin/categories/{id}` | Delete taxonomy category |
| `GET` | `/api/v1/admin/orders` | List all orders across customers with filters |
| `GET` | `/api/v1/admin/orders/{orderNumber}` | Full order details with audit timeline |
| `PATCH` | `/api/v1/admin/orders/{orderNumber}/status` | Controlled status transition (adds tracking, restores inventory on cancellation) |
| `GET` | `/api/v1/admin/analytics` | Store KPI dashboard metrics, revenue, and stock alerts |

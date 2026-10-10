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

## 2A. Figma Dashboard API Expansion (Gemini implementation handoff)

The following endpoints are the agreed target for the Figma-generated dashboard integration. Existing analytics, orders, catalog, and status routes remain supported; these additions must remain admin-RBAC protected. All amounts are INR rupees with paise fields where the existing API provides them. Date ranges use ISO-8601 calendar dates interpreted in `Asia/Kolkata`; responses must state the effective range. Do not seed or return the Figma export's sample data.

| Endpoint | Dashboard use | Required behavior |
| --- | --- | --- |
| `GET /api/v1/admin/dashboard/summary?from=&to=&compareFrom=&compareTo=` | KPI cards, statuses, recent orders, inventory and attention | Aggregate persisted orders/payments/inventory only; return a comparison only when both ranges are valid; bound recent orders to 10; expose unavailable values explicitly. |
| `GET /api/v1/admin/dashboard/sales?from=&to=&interval=daily\|weekly\|monthly` | Sales chart | Return ordered buckets for the requested range, including empty buckets as zero only for recorded sales series; define eligible paid/completed statuses in the contract. |
| `GET /api/v1/admin/finance/summary?from=&to=` | Finance cards and breakdown | Return gross sales, discounts, shipping, stored tax, refunds, adjustments, fees, net and taxable values with per-field availability where the source is not recorded. No frontend tax/accounting calculations. |
| `GET /api/v1/admin/finance/sales?from=&to=&interval=` | Finance trend chart | Same range/bucket rules as dashboard sales; amounts must reconcile to the summary and document exclusions. |
| `GET /api/v1/admin/orders` | Orders table | Preserve existing pagination/response compatibility and add validated date, order/payment/shipping status, country, min/max value, SKU, and allow-listed sort filters where data exists. |
| `GET /api/v1/admin/dashboard/attention?page=&pageSize=` | Action-needed list | Return only persisted, explainable conditions, with severity, reason, order reference, and the threshold/rule that triggered each item. |
| `GET /api/v1/admin/search?q=&page=&pageSize=` | Global admin search | Bounded, paginated search over orders, customers, products, and SKU; return typed result kinds and only necessary customer PII. |
| `GET /api/v1/admin/returns` and return detail/actions | Returns/refunds screen | Requires a persisted return/refund model, audit history, and safe state transitions. Never report a refund complete without a successful persisted provider result. |

This is a target contract, not a claim that these routes already exist. Gemini should add precise Pydantic response schemas/examples here and in OpenAPI while implementing. If the current payment/order model cannot substantiate an accounting field, represent it as `null` with an availability/reason field, and record the gap instead of estimating it. Codex will consume only fields backed by the finalized schema and will show a clear empty/unavailable state for incomplete capabilities.

## 3. TypeScript Contracts

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
  primaryImage: string; // Storage key, preserved on edits
  primaryImageUrl: string; // Backend-resolved display URL
  galleryImageUrls: string[]; // Backend-resolved display URLs
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

// -----------------------------------------------------------------------------
// Figma Dashboard, Finance, Attention, Search & Returns Contracts
// -----------------------------------------------------------------------------

export interface AdminDashboardComparison {
  revenueGrowthPct: number | null;
  ordersGrowthPct: number | null;
  aovGrowthPct: number | null;
}

export interface AdminDashboardSummaryOut {
  from: string; // ISO date YYYY-MM-DD
  to: string; // ISO date YYYY-MM-DD
  effectiveFrom: string; // ISO-8601 UTC
  effectiveTo: string; // ISO-8601 UTC
  totalRevenue: number;
  totalRevenuePaise: number;
  totalOrders: number;
  averageOrderValue: number;
  averageOrderValuePaise: number;
  pendingOrders: number;
  deliveredOrders: number;
  cancelledOrders: number;
  returnedOrders: number;
  recentOrders: AdminOrderDetailOut[];
  lowStockCount: number;
  actionRequiredCount: number;
  comparison: AdminDashboardComparison | null;
}

export interface AdminSalesBucket {
  bucketStart: string;
  bucketEnd: string;
  ordersCount: number;
  grossSales: number;
  netSales: number;
}

export interface AdminSalesSeriesOut {
  from: string;
  to: string;
  interval: "daily" | "weekly" | "monthly";
  buckets: AdminSalesBucket[];
}

export interface AdminFinanceSummaryOut {
  from: string;
  to: string;
  effectiveFrom: string;
  effectiveTo: string;
  grossSales: number;
  grossSalesPaise: number;
  discounts: number;
  discountsPaise: number;
  shippingCollected: number;
  shippingCollectedPaise: number;
  storedTax: number;
  storedTaxPaise: number;
  taxRecordedAvailable: boolean;
  refunds: number;
  refundsPaise: number;
  netRevenue: number;
  netRevenuePaise: number;
  gatewayFees: number | null;
  gatewayFeesAvailable: boolean; // false until provider ledger webhook is integrated
  gatewayFeesNote: string | null;
}

export interface AdminFinanceSalesBucket {
  bucketStart: string;
  bucketEnd: string;
  ordersCount: number;
  grossSales: number;
  discounts: number;
  shippingCollected: number;
  refunds: number;
  netRevenue: number;
}

export interface AdminFinanceSeriesOut {
  from: string;
  to: string;
  interval: "daily" | "weekly" | "monthly";
  buckets: AdminFinanceSalesBucket[];
}

export interface AdminAttentionItem {
  id: string;
  kind: "ORDER" | "RETURN" | "STOCK";
  severity: "URGENT" | "ATTENTION" | "INFO";
  title: string;
  description: string;
  orderNumber?: string | null;
  returnNumber?: string | null;
  sku?: string | null;
  createdAt: string;
}

export interface AdminAttentionListOut {
  items: AdminAttentionItem[];
  total: number;
  page: number;
  pageSize: number;
}

export interface AdminSearchResultItem {
  kind: "order" | "product" | "customer";
  id: string;
  title: string;
  subtitle: string;
  status: string;
  amount?: number | null;
  href: string;
}

export interface AdminGlobalSearchOut {
  query: string;
  total: number;
  page: number;
  pageSize: number;
  items: AdminSearchResultItem[];
}

export interface AdminReturnItemIn {
  orderItemId: number;
  quantity: number;
}

export interface AdminReturnCreateIn {
  orderNumber: string;
  reason: string;
  reasonDetails?: string | null;
  items?: AdminReturnItemIn[] | null;
  adminNotes?: string | null;
}

export interface AdminReturnStatusUpdateIn {
  status: "REQUESTED" | "APPROVED" | "ITEMS_RECEIVED" | "INSPECTED" | "REJECTED" | "CANCELLED";
  note?: string | null;
}

export interface AdminReturnRefundIn {
  amount?: number | null;
  note?: string | null;
}

export interface AdminReturnItemOut {
  orderItemId: number;
  productName: string;
  sku: string;
  quantity: number;
  unitPrice: number;
  lineTotal: number;
}

export interface AdminReturnDetailOut {
  id: number;
  returnNumber: string;
  orderId: number;
  orderNumber: string;
  customerName: string;
  customerEmail: string;
  customerPhone?: string | null;
  status: string;
  reason: string;
  reasonDetails?: string | null;
  items: AdminReturnItemOut[];
  refundAmount: number;
  refundAmountPaise: number;
  refundStatus: string;
  adminNotes?: string | null;
  history: Array<{ status: string; actor: string; note: string; timestamp: string }>;
  createdAt: string;
  updatedAt: string;
}

export interface AdminReturnListOut {
  items: AdminReturnDetailOut[];
  total: number;
  page: number;
  pageSize: number;
}

// -----------------------------------------------------------------------------
// Occasions Administration
// -----------------------------------------------------------------------------

export interface AdminOccasionIn {
  id: string; // Unique slug identifier (e.g. 'birthday', 'valentine')
  name: string;
  icon?: string | null;
  imageKey?: string | null;
  imageUrl?: string | null;
  description?: string | null;
  displayOrder?: number;
  isEnabled?: boolean;
  startsAt?: string | null; // ISO 8601 string in Asia/Kolkata
  endsAt?: string | null;
  productIds?: number[];
}

export interface AdminOccasionUpdateIn {
  name?: string | null;
  icon?: string | null;
  imageKey?: string | null;
  imageUrl?: string | null;
  description?: string | null;
  displayOrder?: number | null;
  isEnabled?: boolean | null;
  startsAt?: string | null;
  endsAt?: string | null;
  productIds?: number[] | null;
}

export interface AdminOccasionOut {
  id: string;
  name: string;
  icon?: string | null;
  imageKey?: string | null;
  imageUrl?: string | null;
  description?: string | null;
  displayOrder: number;
  isEnabled: boolean;
  isEvergreen: boolean; // Backend-derived; evergreen occasions stay visible year-round and cannot be hidden/scheduled.
  startsAt?: string | null;
  endsAt?: string | null;
  productCount: number;
  productIds: number[];
  createdAt?: string | null;
  updatedAt?: string | null;
}

// -----------------------------------------------------------------------------
// Tags Administration
// -----------------------------------------------------------------------------

export interface AdminTagCreate {
  name: string; // 1 to 50 chars, trimmed, non-empty
}

export interface AdminTagOut {
  id: number;
  name: string;
}

// -----------------------------------------------------------------------------
// Customers (Task 1.9.1)
// -----------------------------------------------------------------------------

export interface AdminCustomerOut {
  id: number;
  name: string | null;
  email: string | null;
  phone: string | null;
  status: string;
  createdAt: string | null;
  lastLoginAt: string | null;
  orderCount: number;
}

export interface AdminCustomerListOut {
  items: AdminCustomerOut[];
  total: number;
  page: number;
  pageSize: number;
}
```

---

## 4. Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/admin/dashboard/summary` | KPI cards, status counts, bounded recent orders (10), low-stock count, action-required count, and optional date-range comparison |
| `GET` | `/api/v1/admin/dashboard/sales` | Ordered sales trend buckets (daily, weekly, monthly) in Asia/Kolkata timezone with zero-filled gaps |
| `GET` | `/api/v1/admin/finance/summary` | Persisted gross sales, discounts, shipping, stored tax, refunds, and net revenue with explicit availability flags |
| `GET` | `/api/v1/admin/finance/sales` | Finance sales trend series reconciling directly to finance summary definitions |
| `GET` | `/api/v1/admin/dashboard/attention` | Persisted action items: unshipped orders, pending returns, and low stock variants |
| `GET` | `/api/v1/admin/search` | Paginated global search across orders (number/customer), products (name/SKU), and customers |
| `GET` | `/api/v1/admin/returns` | List returns with status, orderNumber, date range filters, and pagination |
| `GET` | `/api/v1/admin/returns/{id}` | Full return details, audit timeline, and associated order item breakdown |
| `POST` | `/api/v1/admin/returns` | Create return request against an existing order |
| `PATCH` | `/api/v1/admin/returns/{id}/status` | Transition return lifecycle status (`APPROVED`, `ITEMS_RECEIVED`, `INSPECTED`, `REJECTED`, `CANCELLED`) |
| `POST` | `/api/v1/admin/returns/{id}/refund` | Issue persisted refund via active payment provider (Mock/Razorpay) and update return + order status |
| `GET` | `/api/v1/admin/occasions` | List all curated occasions with display order, product counts, and active status |
| `POST` | `/api/v1/admin/occasions` | Create a curated gift occasion with slug, distinct image key, schedule, and product associations |
| `GET` | `/api/v1/admin/occasions/{id}` | Retrieve details of a single curated occasion |
| `PUT` | `/api/v1/admin/occasions/{id}` | Update occasion details, distinct image, active dates, or product associations (also accepts `PATCH`) |
| `DELETE` | `/api/v1/admin/occasions/{id}` | Delete occasion configuration and association mappings |
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
| `GET` | `/api/v1/admin/tags` | List all available tags ordered by name/id for admin product discovery |
| `POST` | `/api/v1/admin/tags` | Create a new tag or return existing tag if duplicate (case-insensitive duplicate check, concurrency safe) |
| `GET` | `/api/v1/admin/customers` | Paginated customer list (`q`, `page`, `pageSize`) with total order counts, excluding admin users |
| `GET` | `/api/v1/admin/customers/{id}` | Customer profile details with order count; 404 for missing or non-customer user |
| `GET` | `/api/v1/admin/customers/{id}/orders` | Paginated order history strictly linked to customer by user_id |
| `GET` | `/api/v1/admin/orders` | List all orders across customers with extended filters (`from`, `to`, `paymentStatus`, `country`, `sku`, `minTotal`, `maxTotal`, `sortBy`) |
| `GET` | `/api/v1/admin/orders/{orderNumber}` | Full order details with audit timeline |
| `PATCH` | `/api/v1/admin/orders/{orderNumber}/status` | Controlled status transition (adds tracking, restores inventory on cancellation) |
| `GET` | `/api/v1/admin/analytics` | Store KPI dashboard metrics, revenue, and stock alerts |

### Customer Administration Rules (Task 1.9.1)
- **Authentication**: `GET` on `/api/v1/admin/customers*` requires `ADMIN` role. Unauthenticated requests return `401`, non-admin users return `403`.
- **Role Scope**: Only users with role `CUSTOMER` are returned; admins are excluded. Requests for missing IDs or non-customer accounts return `404 Not Found`.
- **Search Bounds**: Parameterized case-insensitive matching across `name`, `email`, and `phone` with a 200-character maximum query bound (`422 Unprocessable Entity` for oversized queries).
- **Strict Order Ownership**: Customer order history only returns orders where `Order.user_id == customer.id`. Guest orders remain in the general Orders screen and are never attached by matching email or phone.
- **Privacy & Safety**: Passwords, sessions, auth identity subjects/tokens, magic links, and delivery addresses are never exposed in customer list or profile responses.

### Tag Management & Product Association Rules
- **Authentication**: `GET` and `POST` on `/api/v1/admin/tags` require `ADMIN` role. Unauthenticated requests return `401`, non-admin users return `403`.
- **Validation**: Tag name must be trimmed, non-empty, and bounded between 1 and 50 characters (`422 Unprocessable Entity` for empty, whitespace-only, or oversized strings). Quotes and SQL-like characters are safely parameterized.
- **Idempotency & Concurrency**: Creating an existing tag (case-insensitive comparison, e.g. `handmade` vs `Handmade`) returns the existing tag (`200 OK`) rather than creating a duplicate (`201 Created`). Handled concurrency-safely via database savepoints.
- **Product Association Validation**: `POST /api/v1/admin/products` and `PATCH`/`PUT /api/v1/admin/products/{id}` strictly validate all `tagIds` against persisted tags. Any unknown tag ID triggers an immediate `400 Bad Request` (`detail: "Invalid tagIds: [...]"`). On failed save, existing product associations and attributes remain completely intact.

// ─── Order lifecycle ───────────────────────────────────────────────────────────
export type OrderStatus =
  | 'PENDING_PAYMENT' | 'PAID' | 'CONFIRMED' | 'PROCESSING'
  | 'READY_TO_SHIP' | 'SHIPPED' | 'OUT_FOR_DELIVERY' | 'DELIVERED'
  | 'CANCELLED' | 'REFUNDED';

export type PaymentStatus = 'PENDING' | 'PAID' | 'FAILED' | 'PARTIALLY_REFUNDED' | 'REFUNDED';

export type ReturnStatus =
  | 'REQUESTED' | 'APPROVED' | 'ITEMS_RECEIVED' | 'INSPECTED'
  | 'REJECTED' | 'CANCELLED' | 'REFUNDED';

export type IssueSeverity = 'info' | 'warning' | 'critical';

// ─── API response shapes ───────────────────────────────────────────────────────
export interface DashboardSummary {
  period: string;
  totalSales: number;
  totalRevenue: number;
  netRevenue: number;
  orders: number;
  avgOrderValue: number;
  refunds: number;
  statusCounts: Partial<Record<OrderStatus, number>>;
  comparison: { salesGrowthPercent: number | null; orderGrowthPercent: number | null } | null;
}

export interface OrderStatusCount {
  status: OrderStatus;
  count: number;
}

export interface AttentionItem {
  id: string;
  orderId: string;
  orderNumber?: string;
  issueType: string;
  description: string;
  ageInStatusHours: number;
  severity: IssueSeverity;
  currentStatus?: OrderStatus;
}

export interface OrderCustomer {
  name: string;
  email: string;
  phone: string;
}

export interface ShippingAddress {
  line1: string;
  line2?: string;
  city: string;
  state: string;
  pinCode: string;
  country: string;
}

export interface OrderItem {
  id: string;
  productName: string;
  sku: string;
  variant?: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  finalAmount: number;
  image?: string;
  customization?: Record<string, string>;
}

export interface Shipment {
  id: string;
  courier: string;
  trackingId: string;
  trackingUrl?: string;
  createdDate: string;
  shippedDate?: string;
  estimatedDelivery?: string;
  currentState: string;
  history: { event: string; timestamp: string; location?: string }[];
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  status: string;
  label: string;
  actor: string;
  note?: string;
}

export interface Order {
  id: string;
  orderNumber: string;
  date: string;
  customer: OrderCustomer;
  shippingAddress: ShippingAddress;
  items: OrderItem[];
  subtotal: number;
  shipping: number;
  discount: number;
  gst: number;
  total: number;
  paymentStatus: PaymentStatus;
  paymentMethod: string;
  orderStatus: OrderStatus;
  shippingStatus?: string;
  deliveryEta?: string;
  issueFlag?: string;
  shipment?: Shipment;
  timeline: TimelineEvent[];
  notes?: string;
}

export interface OrdersListResponse {
  orders: Order[];
  total: number;
  page: number;
  pageSize: number;
}

export interface FinanceSummary {
  grossSales: number;
  discounts: number;
  shippingCollected: number;
  gstCollected: number;
  refunds: number;
  paymentFees: number | null;
  netRevenue: number;
  taxableSales: number;
  orderCount: number;
  refundCount: number;
  gatewayFeesAvailable: boolean;
  gatewayFeesNote: string | null;
}

export interface SalesDataPoint {
  label: string;
  revenue: number;
  orders: number;
  avgOrderValue: number;
}

export interface Return {
  id: string;
  orderId: string;
  orderNumber: string;
  customer: { name: string; email: string };
  productName: string;
  reason: string;
  requestedDate: string;
  status: ReturnStatus;
  refundAmount: number;
  notes?: string;
}

export interface AdminOccasion {
  id: string;
  name: string;
  icon?: string | null;
  imageKey?: string | null;
  imageUrl?: string | null;
  description?: string | null;
  displayOrder: number;
  isEnabled: boolean;
  /** Backend-owned business rule. Null means the API has not supplied this contract yet. */
  isEvergreen: boolean | null;
  startsAt?: string | null;
  endsAt?: string | null;
  productCount: number;
  productIds: number[];
}

export interface InventoryAlert {
  id: string;
  productName: string;
  sku: string;
  type: 'ready_stock' | 'made_to_order';
  readyStock: number;
  reserved: number;
  available: number;
  alertLevel: 'low' | 'out';
}

export interface ActivityItem {
  id: string;
  type: 'order_placed' | 'order_updated' | 'order_shipped' | 'return_requested' | 'refund_completed' | 'low_stock' | 'payment_failed' | 'order_delivered';
  message: string;
  timestamp: string;
  orderNumber?: string;
  severity?: IssueSeverity;
}

export type DateRangePreset = 'today' | 'yesterday' | '7d' | '30d' | 'this_month' | 'prev_month';

export interface DateRange {
  preset: DateRangePreset;
  label: string;
  from: string;
  to: string;
}

export type AdminPage =
  | 'dashboard' | 'orders' | 'order-detail'
  | 'products' | 'inventory' | 'customers'
  | 'finance' | 'returns' | 'occasions' | 'settings';

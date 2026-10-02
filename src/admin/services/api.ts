import { apiUrl } from '../../lib/api/client';
import type {
  ActivityItem, AdminOccasion, AttentionItem, DashboardSummary, FinanceSummary, InventoryAlert,
  Order, OrderStatus, OrderStatusCount, OrdersListResponse, Return, ReturnStatus,
  SalesDataPoint,
} from '../types';

type Json = Record<string, any>;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(path), {
    ...init,
    credentials: 'include',
    headers: { ...(init?.body ? { 'Content-Type': 'application/json' } : {}), ...init?.headers },
  });
  if (!response.ok) throw new Error(`Admin request failed (${response.status})`);
  return response.json() as Promise<T>;
}

function dateRange(preset: string) {
  const today = new Date();
  const end = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()));
  const start = new Date(end);
  if (preset === 'today') { /* same day */ }
  else if (preset === 'yesterday') start.setUTCDate(start.getUTCDate() - 1);
  else if (preset === '7d') start.setUTCDate(start.getUTCDate() - 6);
  else if (preset === 'this_month') start.setUTCDate(1);
  else if (preset === 'prev_month') {
    start.setUTCMonth(start.getUTCMonth() - 1, 1);
    end.setUTCDate(0);
  } else start.setUTCDate(start.getUTCDate() - 29);
  const iso = (value: Date) => value.toISOString().slice(0, 10);
  return { from: iso(start), to: iso(end) };
}

const status = (value: string): OrderStatus => value as OrderStatus;

function mapOrder(raw: Json): Order {
  const customerName = raw.customerName || '';
  const address = raw.shippingAddress || {};
  const history = Array.isArray(raw.statusHistory) ? raw.statusHistory : [];
  const items = Array.isArray(raw.items) ? raw.items : [];
  return {
    id: String(raw.id),
    orderNumber: raw.orderNumber,
    date: raw.createdAt,
    customer: { name: customerName, email: raw.customerEmail || '', phone: raw.customerPhone || '' },
    shippingAddress: {
      line1: [address.line1, address.addressLine1, address.street].find(Boolean) || '',
      line2: [address.line2, address.addressLine2].find(Boolean) || undefined,
      city: address.city || '', state: address.state || '',
      pinCode: address.pinCode || address.postalCode || address.pincode || '',
      country: address.country || '',
    },
    items: items.map((item: Json) => ({
      id: String(item.id), productName: item.productName, sku: item.sku,
      variant: item.variantName || undefined, quantity: item.quantity,
      unitPrice: item.unitPrice, discount: 0, finalAmount: item.lineTotal,
      image: item.productImage || undefined,
      customization: item.personalization && Object.keys(item.personalization).length ? item.personalization : undefined,
    })),
    subtotal: raw.subtotal, shipping: raw.shippingFee, discount: raw.discountAmount,
    gst: raw.taxAmount, total: raw.totalAmount,
    paymentStatus: raw.paymentStatus, paymentMethod: raw.paymentMethod,
    orderStatus: status(raw.status), shippingStatus: raw.trackingNumber ? 'Tracking recorded' : undefined,
    shipment: undefined,
    timeline: history.map((event: Json) => ({
      id: String(event.id), timestamp: event.timestamp, status: event.status,
      label: String(event.status).replaceAll('_', ' '), actor: 'Recorded order history', note: event.note || undefined,
    })),
    notes: raw.notes || undefined,
  };
}

export interface OrdersQuery {
  page?: number; pageSize?: number; status?: OrderStatus | 'ALL'; search?: string;
  dateFrom?: string; dateTo?: string; paymentStatus?: string; sortBy?: string;
  sortDir?: 'asc' | 'desc';
}

export async function getDashboardSummary(preset = '30d'): Promise<DashboardSummary> {
  const range = dateRange(preset);
  const previousStart = new Date(`${range.from}T00:00:00Z`);
  const previousEnd = new Date(`${range.to}T00:00:00Z`);
  const span = Math.max(1, Math.round((previousEnd.getTime() - previousStart.getTime()) / 86400000) + 1);
  previousStart.setUTCDate(previousStart.getUTCDate() - span);
  previousEnd.setUTCDate(previousEnd.getUTCDate() - span);
  const params = new URLSearchParams({ ...range, compareFrom: previousStart.toISOString().slice(0, 10), compareTo: previousEnd.toISOString().slice(0, 10) });
  const raw = await request<Json>(`/admin/dashboard/summary?${params}`);
  const counts = raw.statusCounts || {};
  const summary: DashboardSummary = {
    period: `${raw.effectiveRange?.from || range.from} – ${raw.effectiveRange?.to || range.to}`,
    totalSales: raw.totalSales, totalRevenue: raw.totalSales, netRevenue: raw.netRevenue,
    orders: raw.orderCount, avgOrderValue: raw.averageOrderValue,
    refunds: Math.max(0, raw.totalSales - raw.netRevenue),
    statusCounts: counts,
    comparison: raw.comparison ? { salesGrowthPercent: raw.comparison.salesGrowthPercent, orderGrowthPercent: raw.comparison.orderGrowthPercent } : null,
  };
  return summary;
}

export async function getOrderStatusCounts(): Promise<OrderStatusCount[]> {
  return getOrderStatusCountsForPeriod('30d');
}

export async function getOrderStatusCountsForPeriod(period: string): Promise<OrderStatusCount[]> {
  const { from, to } = dateRange(period);
  const raw = await request<Json>(`/admin/dashboard/summary?from=${from}&to=${to}`);
  return Object.entries(raw.statusCounts || {}).map(([key, count]) => ({ status: status(key), count: Number(count) }));
}

export async function getAttentionItems(): Promise<AttentionItem[]> {
  const raw = await request<Json>('/admin/dashboard/attention?page=1&pageSize=50');
  return (raw.items || []).map((item: Json) => ({
    id: item.id, orderId: String(item.orderId || item.variantId || item.id),
    orderNumber: item.orderNumber || item.sku || undefined,
    issueType: item.title || item.rule, description: item.message,
    ageInStatusHours: 0,
    severity: ['CRITICAL', 'URGENT', 'HIGH'].includes(item.severity) ? 'critical' : item.severity === 'INFO' ? 'info' : 'warning',
  }));
}

export async function getActivityFeed(): Promise<ActivityItem[]> {
  const { from, to } = dateRange('30d');
  const summary = await request<Json>(`/admin/dashboard/summary?from=${from}&to=${to}`);
  return (summary.recentOrders || []).flatMap((order: Json) => (order.statusHistory || []).map((event: Json) => ({
    id: `${order.id}-${event.id}`, type: 'order_updated' as const,
    message: `Order status recorded: ${String(event.status).replaceAll('_', ' ').toLowerCase()}`,
    timestamp: event.timestamp || order.updatedAt, orderNumber: order.orderNumber,
  }))).slice(0, 12);
}

export async function getInventoryAlerts(): Promise<InventoryAlert[]> {
  const { from, to } = dateRange('30d');
  const summary = await request<Json>(`/admin/dashboard/summary?from=${from}&to=${to}`);
  const items = summary.inventoryAlerts?.lowStockItems || [];
  return items.map((item: Json) => ({
    id: String(item.variantId), productName: item.productName, sku: item.sku,
    type: 'ready_stock', readyStock: item.stockQuantity, reserved: 0,
    available: item.stockQuantity, alertLevel: item.stockQuantity <= 0 ? 'out' : 'low',
  }));
}

export async function getSalesChart(period: '7d' | '30d' = '30d'): Promise<SalesDataPoint[]> {
  const range = dateRange(period);
  const params = new URLSearchParams({ ...range, interval: 'daily' });
  const raw = await request<Json>(`/admin/dashboard/sales?${params}`);
  return (raw.buckets || []).map((bucket: Json) => ({
    label: bucket.date, revenue: bucket.sales, orders: bucket.orderCount,
    avgOrderValue: bucket.orderCount ? bucket.sales / bucket.orderCount : 0,
  }));
}

export async function getOrders(query: OrdersQuery = {}): Promise<OrdersListResponse> {
  const params = new URLSearchParams();
  if (query.page) params.set('page', String(query.page));
  if (query.pageSize) params.set('pageSize', String(query.pageSize));
  if (query.status && query.status !== 'ALL') params.set('status', query.status);
  if (query.search) params.set('q', query.search);
  if (query.dateFrom) params.set('from', query.dateFrom);
  if (query.dateTo) params.set('to', query.dateTo);
  if (query.paymentStatus) params.set('paymentStatus', query.paymentStatus);
  if (query.sortBy) {
    const sortMap: Record<string, string> = {
      'date-desc': 'created_at_desc', 'date-asc': 'created_at_asc',
      'total-desc': 'total_desc', 'total-asc': 'total_asc',
    };
    params.set('sortBy', sortMap[`${query.sortBy}-${query.sortDir || 'desc'}`] || 'created_at_desc');
  }
  const raw = await request<Json>(`/admin/orders?${params}`);
  return { orders: (raw.items || []).map(mapOrder), total: raw.total, page: raw.page, pageSize: raw.pageSize };
}

export async function getOrder(id: string): Promise<Order | null> {
  try { return mapOrder(await request<Json>(`/admin/orders/${encodeURIComponent(id)}`)); }
  catch (error) { if (error instanceof Error && /404/.test(error.message)) return null; throw error; }
}

export async function updateOrderStatus(id: string, nextStatus: OrderStatus, note?: string, trackingNumber?: string): Promise<void> {
  await request(`/admin/orders/${encodeURIComponent(id)}/status`, {
    method: 'PATCH', body: JSON.stringify({ status: nextStatus, note, trackingNumber }),
  });
}

export async function getFinanceSummary(preset = '30d'): Promise<FinanceSummary> {
  const params = new URLSearchParams(dateRange(preset));
  const raw = await request<Json>(`/admin/finance/summary?${params}`);
  return {
    grossSales: raw.grossSales, discounts: raw.discounts, shippingCollected: raw.shippingCollected,
    gstCollected: raw.storedTax, refunds: raw.refunds,
    paymentFees: raw.gatewayFees, netRevenue: raw.netRevenue, taxableSales: raw.taxableSales,
    orderCount: raw.orderCount, refundCount: raw.refundCount,
    gatewayFeesAvailable: raw.gatewayFeesAvailable, gatewayFeesNote: raw.gatewayFeesNote ?? null,
  };
}

export async function getSalesChartFinance(period: '7d' | '30d' = '30d'): Promise<SalesDataPoint[]> {
  const params = new URLSearchParams({ ...dateRange(period), interval: 'daily' });
  const raw = await request<Json>(`/admin/finance/sales?${params}`);
  return (raw.buckets || []).map((bucket: Json) => ({
    label: bucket.date, revenue: bucket.netRevenue, orders: bucket.orderCount,
    avgOrderValue: bucket.orderCount ? bucket.netRevenue / bucket.orderCount : 0,
  }));
}

function mapReturn(raw: Json): Return {
  const firstItem = raw.items?.[0];
  const mapStatus: Record<string, ReturnStatus> = { ITEMS_RECEIVED: 'ITEMS_RECEIVED' };
  const returnStatus = raw.refundStatus === 'COMPLETED' ? 'REFUNDED' : (mapStatus[raw.status] || raw.status);
  return {
    id: String(raw.returnNumber), orderId: String(raw.orderId), orderNumber: raw.orderNumber,
    customer: { name: raw.customerName, email: raw.customerEmail || '' },
    productName: firstItem?.productName || 'Multiple items', reason: raw.reasonDetails || raw.reason,
    requestedDate: raw.createdAt, status: returnStatus,
    refundAmount: raw.refundAmount, notes: raw.adminNotes || undefined,
  };
}

export async function getReturns(): Promise<Return[]> {
  const raw = await request<Json>('/admin/returns?page=1&pageSize=100');
  return (raw.items || []).map(mapReturn);
}

export async function approveReturn(id: string): Promise<void> {
  await request(`/admin/returns/${encodeURIComponent(id)}/status`, { method: 'PATCH', body: JSON.stringify({ status: 'APPROVED' }) });
}

export async function rejectReturn(id: string): Promise<void> {
  await request(`/admin/returns/${encodeURIComponent(id)}/status`, { method: 'PATCH', body: JSON.stringify({ status: 'REJECTED' }) });
}

export async function processReturnRefund(id: string): Promise<void> {
  await request(`/admin/returns/${encodeURIComponent(id)}/refund`, { method: 'POST', body: JSON.stringify({}) });
}

export async function getAdminOccasions(): Promise<AdminOccasion[]> {
  const rows = await request<Json[]>('/admin/occasions');
  return rows.map(row => ({
    id: String(row.id), name: String(row.name), icon: row.icon ?? null,
    imageKey: row.imageKey ?? null, imageUrl: row.imageUrl ?? null,
    description: row.description ?? null,
    displayOrder: Number(row.displayOrder ?? 0), isEnabled: Boolean(row.isEnabled),
    isEvergreen: typeof row.isEvergreen === 'boolean' ? row.isEvergreen : null,
    startsAt: row.startsAt ?? null, endsAt: row.endsAt ?? null,
    productCount: Number(row.productCount ?? 0), productIds: row.productIds ?? [],
  }));
}

export async function updateAdminOccasion(id: string, patch: Partial<Pick<AdminOccasion, 'isEnabled' | 'startsAt' | 'endsAt'>>): Promise<AdminOccasion> {
  const row = await request<Json>(`/admin/occasions/${encodeURIComponent(id)}`, {
    method: 'PATCH', body: JSON.stringify(patch),
  });
  return {
    id: String(row.id), name: String(row.name), icon: row.icon ?? null,
    imageKey: row.imageKey ?? null, imageUrl: row.imageUrl ?? null,
    description: row.description ?? null,
    displayOrder: Number(row.displayOrder ?? 0), isEnabled: Boolean(row.isEnabled),
    isEvergreen: typeof row.isEvergreen === 'boolean' ? row.isEvergreen : null,
    startsAt: row.startsAt ?? null, endsAt: row.endsAt ?? null,
    productCount: Number(row.productCount ?? 0), productIds: row.productIds ?? [],
  };
}

// No CSV export route exists yet; export actions stay disabled until the API contract includes one.

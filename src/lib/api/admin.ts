import { apiUrl } from './client';

export interface AdminLowStockItem {
  variantId: number;
  productId: number;
  productName: string;
  sku: string;
  variantName: string;
  stockQuantity: number;
}

export interface AdminOrderItem {
  id: number;
  productId: number | null;
  variantId: number | null;
  productName: string;
  productSlug: string | null;
  sku: string;
  variantName: string;
  productImage: string | null;
  unitPrice: number;
  quantity: number;
  lineTotal: number;
  personalization: Record<string, unknown>;
}

export interface AdminOrder {
  id: number;
  orderNumber: string;
  customerName: string;
  customerPhone: string;
  customerEmail: string | null;
  status: string;
  paymentStatus: string;
  paymentMethod: string;
  subtotal: number;
  shippingFee: number;
  discountAmount: number;
  taxAmount: number;
  totalAmount: number;
  shippingAddress: Record<string, unknown>;
  trackingNumber: string | null;
  courierName: string | null;
  notes: string | null;
  items: AdminOrderItem[];
  statusHistory: Array<{ id: number; status: string; note: string | null; timestamp: string | null }>;
  createdAt: string;
  updatedAt: string;
}

export interface AdminOrderList {
  items: AdminOrder[];
  total: number;
  page: number;
  pageSize: number;
}

export interface AdminAnalytics {
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
  recentOrders: AdminOrder[];
  topSellingProducts: Array<{ productId: number; productName: string; totalSold: number; totalRevenue: number; totalRevenuePaise: number }>;
}

export interface AdminProductVariant {
  id: number;
  sku: string;
  name: string;
  price: number;
  stockQuantity: number;
  status: string;
}

export interface AdminProduct {
  id: number;
  name: string;
  slug: string;
  status: string;
  primaryImage: string;
  primaryImageUrl?: string;
  totalStock: number;
  minPrice: number;
  variants: AdminProductVariant[];
  categoryNames: string[];
}

export interface AdminProductList {
  items: AdminProduct[];
  total: number;
  page: number;
  pageSize: number;
}

export interface AdminOccasion {
  id: string;
  name: string;
  icon: string | null;
  imageKey: string | null;
  imageUrl: string | null;
  description: string | null;
  displayOrder: number;
  isEnabled: boolean;
  startsAt: string | null;
  endsAt: string | null;
  productCount: number;
  productIds: number[];
  createdAt: string | null;
  updatedAt: string | null;
}

export interface AdminOccasionCreateIn {
  id: string;
  name: string;
  icon?: string | null;
  imageKey?: string | null;
  imageUrl?: string | null;
  description?: string | null;
  displayOrder?: number;
  isEnabled?: boolean;
  startsAt?: string | null;
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

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(apiUrl(path), {
    ...init,
    credentials: 'include',
    headers: { ...(init?.body && !(init.body instanceof FormData) ? { 'Content-Type': 'application/json' } : {}), ...init?.headers },
  });
  if (!response.ok) throw new Error(`Admin request failed (${response.status})`);
  return response.json() as Promise<T>;
}

export function getAdminAnalytics(): Promise<AdminAnalytics> {
  return request('/admin/analytics');
}

export function getAdminOrders(options: { q?: string; status?: string; paymentStatus?: string; page?: number; pageSize?: number } = {}): Promise<AdminOrderList> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(options)) {
    if (value !== undefined && value !== '') params.set(key, String(value));
  }
  return request(`/admin/orders?${params.toString()}`);
}

export function getAdminOrder(id: string | number): Promise<AdminOrder> {
  return request(`/admin/orders/${encodeURIComponent(String(id))}`);
}

export function updateAdminOrderStatus(id: string | number, payload: { status: string; note?: string; trackingNumber?: string; courierName?: string }): Promise<AdminOrder> {
  return request(`/admin/orders/${encodeURIComponent(String(id))}/status`, { method: 'PATCH', body: JSON.stringify(payload) });
}

export function getAdminProducts(options: { q?: string; status?: string; categoryId?: number; lowStock?: boolean; page?: number; pageSize?: number } = {}, signal?: AbortSignal): Promise<AdminProductList> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(options)) {
    if (value !== undefined && value !== '') params.set(key, String(value));
  }
  return request(`/admin/products?${params.toString()}`, { signal });
}

export function getAdminOccasions(): Promise<AdminOccasion[]> {
  return request('/admin/occasions');
}

export function getAdminOccasion(id: string): Promise<AdminOccasion> {
  return request(`/admin/occasions/${encodeURIComponent(id)}`);
}

export function createAdminOccasion(payload: AdminOccasionCreateIn): Promise<AdminOccasion> {
  return request('/admin/occasions', { method: 'POST', body: JSON.stringify(payload) });
}

export function updateAdminOccasion(id: string, payload: AdminOccasionUpdateIn): Promise<AdminOccasion> {
  return request(`/admin/occasions/${encodeURIComponent(id)}`, { method: 'PUT', body: JSON.stringify(payload) });
}

export function deleteAdminOccasion(id: string): Promise<{ status: string; message: string }> {
  return request(`/admin/occasions/${encodeURIComponent(id)}`, { method: 'DELETE' });
}

export { request as adminRequest };

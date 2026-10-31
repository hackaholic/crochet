import { accountResponseError } from './validationErrors';
export interface AddressCreate { name: string; phone: string; line1: string; line2?: string; landmark?: string; city: string; state: string; postalCode: string; country?: string; }
export interface OrderCreate { shippingAddress: AddressCreate; paymentMethod: 'UPI' | 'CARD' | 'NETBANKING'; customerEmail?: string; couponCode?: string; }
export interface OrderLine { id: number; productName: string; productSlug?: string | null; productImage?: string | null; unitPrice?: number; quantity: number; lineTotal: number; }
export interface OrderOut { items?: OrderLine[]; guestTrackingToken?: string | null; id: number; orderNumber: string; status: string; paymentStatus: string; paymentMethod: string; totalAmount: number; totalAmountPaise: number; }
export interface AddressOut { id: number; name: string; phone: string; line1: string; line2?: string | null; country?: string; city: string; state: string; postalCode: string; isDefault: boolean; }
import { apiUrl } from './client';

export async function createOrder(payload: OrderCreate): Promise<OrderOut> {
  const response = await fetch(apiUrl('/orders'), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  if (!response.ok) throw new Error(`Order request failed (${response.status})`);
  return response.json() as Promise<OrderOut>;
}

async function get<T>(path: string): Promise<T> { const response = await fetch(apiUrl(path), { credentials: 'include' }); if (!response.ok) throw await accountResponseError(response); return response.json() as Promise<T>; }
async function post<T>(path: string, body: unknown): Promise<T> { const response = await fetch(apiUrl(path), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }); if (!response.ok) throw await accountResponseError(response); return response.json() as Promise<T>; }
export interface AddressUpdate {
  name?: string;
  phone?: string;
  line1?: string;
  line2?: string;
  landmark?: string;
  city?: string;
  state?: string;
  postalCode?: string;
  country?: string;
  isDefault?: boolean;
}

async function patch<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(apiUrl(path), {
    method: 'PATCH',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw await accountResponseError(response);
  return response.json() as Promise<T>;
}

async function del(path: string): Promise<void> {
  const response = await fetch(apiUrl(path), {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!response.ok) throw await accountResponseError(response);
}

export const accountApi = {
  addresses: () => get<AddressOut[]>('/addresses'),
  order: (orderNumber: string) => get<OrderOut>(`/orders/${encodeURIComponent(orderNumber)}`),
  orders: () => get<OrderOut[]>('/orders'),
  createAddress: (address: AddressCreate) => post<AddressOut>('/addresses', address),
  updateAddress: (id: number, address: AddressUpdate) => patch<AddressOut>(`/addresses/${id}`, address),
  deleteAddress: (id: number) => del(`/addresses/${id}`),
  setDefaultAddress: (id: number) => post<AddressOut>(`/addresses/${id}/default`, {}),
};

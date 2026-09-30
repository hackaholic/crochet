export interface AddressCreate { name: string; phone: string; line1: string; line2?: string; landmark?: string; city: string; state: string; postalCode: string; country?: string; }
export interface OrderCreate { shippingAddress: AddressCreate; paymentMethod: 'COD' | 'UPI' | 'CARD' | 'NETBANKING'; customerEmail?: string; }
export interface OrderOut { id: number; orderNumber: string; status: string; paymentStatus: string; paymentMethod: string; totalAmount: number; totalAmountPaise: number; }
export interface AddressOut { id: number; name: string; phone: string; line1: string; line2?: string | null; city: string; state: string; postalCode: string; isDefault: boolean; }
import { apiUrl } from './client';

export async function createOrder(payload: OrderCreate): Promise<OrderOut> {
  const response = await fetch(apiUrl('/orders'), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  if (!response.ok) throw new Error(`Order request failed (${response.status})`);
  return response.json() as Promise<OrderOut>;
}

async function get<T>(path: string): Promise<T> { const response = await fetch(apiUrl(path), { credentials: 'include' }); if (!response.ok) throw new Error(String(response.status)); return response.json() as Promise<T>; }
async function post<T>(path: string, body: unknown): Promise<T> { const response = await fetch(apiUrl(path), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }); if (!response.ok) throw new Error(String(response.status)); return response.json() as Promise<T>; }
export const accountApi = { addresses: () => get<AddressOut[]>('/addresses'), orders: () => get<OrderOut[]>('/orders'), createAddress: (address: AddressCreate) => post<AddressOut>('/addresses', address) };

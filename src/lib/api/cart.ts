export interface CartItemPayload {
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
  personalization: Record<string, unknown>;
  stockAvailable: number;
}

export interface CartPayload {
  id?: number | null;
  guestToken?: string | null;
  items: CartItemPayload[];
  itemCount: number;
  subtotal: number;
  status: 'ACTIVE' | 'CONVERTED' | 'ABANDONED';
}

import { apiUrl } from './client';

async function requestCart(path: string, init?: RequestInit): Promise<CartPayload> {
  const response = await fetch(apiUrl(`/cart${path}`), {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  });
  if (!response.ok) throw new Error(`Cart request failed (${response.status})`);
  return response.json() as Promise<CartPayload>;
}

export const cartApi = {
  get: () => requestCart(''),
  add: (productId: number, quantity: number) => requestCart('/items', { method: 'POST', body: JSON.stringify({ product_id: productId, quantity }) }),
  update: (itemId: number, quantity: number) => requestCart(`/items/${itemId}`, { method: 'PATCH', body: JSON.stringify({ quantity }) }),
  remove: (itemId: number) => requestCart(`/items/${itemId}`, { method: 'DELETE' }),
};

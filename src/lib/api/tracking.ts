import { apiUrl } from './client';
import type { OrderTracking } from './orderTrackingTypes';

export async function getOrderTracking(orderNumber: string, signal: AbortSignal, guestToken?: string): Promise<OrderTracking> {
  const response = await fetch(apiUrl(`/orders/${encodeURIComponent(orderNumber)}/tracking`), {
    credentials: 'include', cache: 'no-store', signal,
    headers: guestToken ? { 'X-Guest-Order-Token': guestToken } : undefined,
  });
  if (!response.ok) throw new Error('Tracking unavailable');
  return response.json() as Promise<OrderTracking>;
}

export async function requestTrackingLink(orderNumber: string, email: string): Promise<void> {
  const response = await fetch(apiUrl('/orders/tracking/request-link'), {
    method: 'POST', credentials: 'include', cache: 'no-store',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ orderNumber: orderNumber.trim(), email: email.trim() }),
  });
  if (!response.ok) throw new Error('Link request unavailable');
  // Deliberately ignore provider/development link fields: always show the same generic message.
}

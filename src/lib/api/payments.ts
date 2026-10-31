export interface PaymentIntent { paymentId: number; orderId: number; orderNumber: string; provider: string; providerOrderId?: string | null; paymentSessionId?: string | null; environment?: 'sandbox' | 'production' | null; returnUrl?: string | null; amount: number; amountPaise: number; currency: string; }
export interface PaymentVerification { id: number; orderId: number; orderNumber?: string | null; orderStatus?: string | null; orderPaymentStatus?: string | null; provider: string; providerOrderId?: string | null; amount: number; amountPaise: number; currency: string; status: string; verificationState?: string | null; canRetry?: boolean; errorMessage?: string | null; }
import { apiUrl } from './client';

const GUEST_PAYMENT_CAPABILITY_PREFIX = 'sulocraft:guest-payment-capability:';

export function rememberGuestPaymentCapability(orderNumber: string, token?: string | null): void {
  if (!token || !/^[A-Za-z0-9_-]{1,64}$/.test(orderNumber) || token.length > 256) return;
  try { window.sessionStorage.setItem(`${GUEST_PAYMENT_CAPABILITY_PREFIX}${orderNumber}`, token); } catch { /* Storage may be unavailable; the current checkout can still proceed. */ }
}

export function getGuestPaymentCapability(orderNumber?: string | null): string | undefined {
  if (!orderNumber || !/^[A-Za-z0-9_-]{1,64}$/.test(orderNumber)) return undefined;
  try { return window.sessionStorage.getItem(`${GUEST_PAYMENT_CAPABILITY_PREFIX}${orderNumber}`) ?? undefined; } catch { return undefined; }
}

export function forgetGuestPaymentCapability(orderNumber?: string | null): void {
  if (!orderNumber || !/^[A-Za-z0-9_-]{1,64}$/.test(orderNumber)) return;
  try { window.sessionStorage.removeItem(`${GUEST_PAYMENT_CAPABILITY_PREFIX}${orderNumber}`); } catch { /* Best effort cleanup. */ }
}

export async function createPaymentIntent(orderNumber: string, guestOrderToken?: string): Promise<PaymentIntent> {
  const response = await fetch(apiUrl('/payments/intent'), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ orderNumber, ...(guestOrderToken ? { guestOrderToken } : {}) }) });
  if (!response.ok) throw new Error(`Payment intent request failed (${response.status})`);
  return response.json() as Promise<PaymentIntent>;
}

export async function retryCashfreePayment(paymentId: number, guestOrderToken?: string): Promise<PaymentIntent> {
  if (!Number.isSafeInteger(paymentId) || paymentId <= 0 || paymentId > 2_147_483_647) throw new Error('Payment retry details are invalid.');
  const response = await fetch(apiUrl(`/payments/${paymentId}/retry`), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(guestOrderToken ? { guestOrderToken } : {}) });
  if (!response.ok) throw new Error(`Payment retry request failed (${response.status})`);
  return response.json() as Promise<PaymentIntent>;
}

export async function verifyMockPayment(intent: PaymentIntent, detail: string): Promise<void> {
  if (intent.provider !== 'mock') throw new Error('This payment requires secure gateway checkout. Mock verification is unavailable.');
  const response = await fetch(apiUrl('/payments/verify'), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ paymentId: intent.paymentId, providerPaymentId: `pay_mock_${Date.now()}`, providerOrderId: intent.providerOrderId, providerSignature: 'mock_sig_valid', paymentMethodDetail: detail }) });
  if (!response.ok) throw new Error(`Payment verification failed (${response.status})`);
}

export async function verifyCashfreePayment(paymentId: number, providerOrderId: string): Promise<PaymentVerification> {
  if (!Number.isSafeInteger(paymentId) || paymentId <= 0 || paymentId > 2_147_483_647 || !providerOrderId.trim() || providerOrderId.length > 128) {
    throw new Error('Payment verification details are invalid.');
  }
  const response = await fetch(apiUrl('/payments/verify'), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ paymentId, providerOrderId }) });
  const result: unknown = await response.json().catch(() => null);
  if (!result || typeof result !== 'object' || !('id' in result) || typeof result.id !== 'number' || !('status' in result) || typeof result.status !== 'string') {
    throw new Error(`Payment verification failed (${response.status})`);
  }
  return result as PaymentVerification;
}

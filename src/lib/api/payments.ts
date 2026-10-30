export interface PaymentIntent { paymentId: number; orderId: number; orderNumber: string; provider: string; providerOrderId?: string | null; paymentSessionId?: string | null; environment?: 'sandbox' | 'production' | null; returnUrl?: string | null; amount: number; amountPaise: number; currency: string; }
export interface PaymentVerification { id: number; orderId: number; orderNumber?: string; provider: string; providerOrderId?: string | null; amount: number; amountPaise: number; currency: string; status: string; }
import { apiUrl } from './client';

export async function createPaymentIntent(orderNumber: string): Promise<PaymentIntent> {
  const response = await fetch(apiUrl('/payments/intent'), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ orderNumber }) });
  if (!response.ok) throw new Error(`Payment intent request failed (${response.status})`);
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
  if (!response.ok) throw new Error(`Payment verification failed (${response.status})`);
  return response.json() as Promise<PaymentVerification>;
}

export interface PaymentIntent { paymentId: number; orderId: number; orderNumber: string; provider: string; providerOrderId?: string | null; amount: number; amountPaise: number; currency: string; }
import { apiUrl } from './client';

export async function createPaymentIntent(orderNumber: string): Promise<PaymentIntent> {
  const response = await fetch(apiUrl('/payments/intent'), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ orderNumber }) });
  if (!response.ok) throw new Error(`Payment intent request failed (${response.status})`);
  return response.json() as Promise<PaymentIntent>;
}

export async function verifyMockPayment(intent: PaymentIntent, detail: string): Promise<void> {
  const response = await fetch(apiUrl('/payments/verify'), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ paymentId: intent.paymentId, providerPaymentId: `pay_mock_${Date.now()}`, providerOrderId: intent.providerOrderId, providerSignature: 'mock_sig_valid', paymentMethodDetail: detail }) });
  if (!response.ok) throw new Error(`Payment verification failed (${response.status})`);
}

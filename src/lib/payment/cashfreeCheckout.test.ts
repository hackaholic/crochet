import { afterEach, expect, it, vi } from 'vitest';
import { openCashfreeCheckout } from './cashfreeCheckout';
import type { PaymentIntent } from '../api/payments';

afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks(); document.getElementById('cashfree-checkout-sdk')?.remove(); });

const intent: PaymentIntent = { paymentId: 4, orderId: 8, orderNumber: 'SLC-TEST-8', provider: 'cashfree', providerOrderId: 'cf-8', paymentSessionId: 'opaque-session', environment: 'sandbox', amount: 600, amountPaise: 60000, currency: 'INR' };

it('opens the server-provided session in the matching Cashfree environment', async () => {
  const checkout = vi.fn().mockResolvedValue({ redirect: true });
  const factory = vi.fn().mockReturnValue({ checkout });
  vi.stubGlobal('Cashfree', factory);
  await openCashfreeCheckout(intent);
  expect(factory).toHaveBeenCalledWith({ mode: 'sandbox' });
  expect(checkout).toHaveBeenCalledWith({ paymentSessionId: 'opaque-session', redirectTarget: '_self' });
});

it('supports production only when the server response explicitly selects it', async () => {
  const checkout = vi.fn().mockResolvedValue({ redirect: true });
  const factory = vi.fn().mockReturnValue({ checkout });
  vi.stubGlobal('Cashfree', factory);
  await openCashfreeCheckout({ ...intent, environment: 'production' });
  expect(factory).toHaveBeenCalledWith({ mode: 'production' });
});

it('fails closed for wrong provider, missing session or unknown environment', async () => {
  const factory = vi.fn(); vi.stubGlobal('Cashfree', factory);
  await expect(openCashfreeCheckout({ ...intent, provider: 'mock' })).rejects.toThrow('not configured for Cashfree');
  await expect(openCashfreeCheckout({ ...intent, paymentSessionId: null })).rejects.toThrow('valid payment session');
  await expect(openCashfreeCheckout({ ...intent, providerOrderId: null })).rejects.toThrow('valid order reference');
  await expect(openCashfreeCheckout({ ...intent, environment: 'preview' as 'sandbox' })).rejects.toThrow('missing or invalid');
  expect(factory).not.toHaveBeenCalled();
});

it('surfaces SDK-reported failure without leaking provider response data', async () => {
  const checkout = vi.fn().mockResolvedValue({ error: { secret: 'sensitive-provider-text' } });
  vi.stubGlobal('Cashfree', vi.fn().mockReturnValue({ checkout }));
  await expect(openCashfreeCheckout(intent)).rejects.toThrow('Cashfree checkout could not be opened');
});

it('redacts SDK promise rejection details', async () => {
  vi.stubGlobal('Cashfree', vi.fn().mockReturnValue({ checkout: vi.fn().mockRejectedValue(new Error('opaque-session leaked')) }));
  let thrown: unknown;
  try { await openCashfreeCheckout(intent); } catch (error) { thrown = error; }
  expect(thrown).toBeInstanceOf(Error);
  expect((thrown as Error).message).toBe('Cashfree checkout could not be opened. Please try again.');
});

it('fails safely and allows retry when the Cashfree SDK script cannot load', async () => {
  const append = vi.spyOn(document.head, 'appendChild').mockImplementation(node => {
    queueMicrotask(() => (node as HTMLScriptElement).onerror?.(new Event('error')));
    return node;
  });
  await expect(openCashfreeCheckout(intent)).rejects.toThrow('Cashfree checkout could not be loaded');
  expect(append).toHaveBeenCalledOnce();
  expect(document.getElementById('cashfree-checkout-sdk')).toBeNull();
});

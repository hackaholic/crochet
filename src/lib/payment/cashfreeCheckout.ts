import type { PaymentIntent } from '../api/payments';

const CASHFREE_SDK_URL = 'https://sdk.cashfree.com/js/v3/cashfree.js';
const CASHFREE_SCRIPT_ID = 'cashfree-checkout-sdk';

interface CashfreeCheckoutResult {
  error?: unknown;
  redirect?: boolean;
}

interface CashfreeInstance {
  checkout(options: { paymentSessionId: string; redirectTarget: '_self' }): Promise<CashfreeCheckoutResult> | CashfreeCheckoutResult;
}

declare global {
  interface Window {
    Cashfree?: (options: { mode: 'sandbox' | 'production' }) => CashfreeInstance;
  }
}

let sdkLoad: Promise<void> | undefined;

function loadCashfreeSdk(): Promise<void> {
  if (window.Cashfree) return Promise.resolve();
  if (sdkLoad) return sdkLoad;

  const loading = new Promise<void>((resolve, reject) => {
    const existing = document.getElementById(CASHFREE_SCRIPT_ID) as HTMLScriptElement | null;
    const script = existing ?? document.createElement('script');
    script.id = CASHFREE_SCRIPT_ID;
    script.src = CASHFREE_SDK_URL;
    script.async = true;
    script.onload = () => window.Cashfree ? resolve() : reject(new Error('Cashfree checkout is unavailable.'));
    script.onerror = () => reject(new Error('Cashfree checkout could not be loaded. Please try again.'));
    if (!existing) document.head.appendChild(script);
  }).catch(error => {
    document.getElementById(CASHFREE_SCRIPT_ID)?.remove();
    sdkLoad = undefined;
    throw error;
  });

  sdkLoad = loading;
  return loading;
}

export async function openCashfreeCheckout(intent: PaymentIntent): Promise<void> {
  if (intent.provider !== 'cashfree') throw new Error('This payment is not configured for Cashfree checkout.');
  if (typeof intent.paymentSessionId !== 'string' || !intent.paymentSessionId.trim() || intent.paymentSessionId.length > 4096) throw new Error('Cashfree did not provide a valid payment session.');
  if (typeof intent.providerOrderId !== 'string' || !intent.providerOrderId.trim() || intent.providerOrderId.length > 128) throw new Error('Cashfree did not provide a valid order reference.');
  if (intent.environment !== 'sandbox' && intent.environment !== 'production') throw new Error('Cashfree environment is missing or invalid.');

  await loadCashfreeSdk();
  const cashfree = window.Cashfree?.({ mode: intent.environment });
  if (!cashfree) throw new Error('Cashfree checkout is unavailable. Please try again.');
  try {
    const result = await cashfree.checkout({ paymentSessionId: intent.paymentSessionId, redirectTarget: '_self' });
    if (result?.error) throw new Error('checkout-error');
  } catch {
    throw new Error('Cashfree checkout could not be opened. Please try again.');
  }
}

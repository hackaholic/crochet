import { apiUrl } from './client';

export interface CouponApplication { code: string; discountAmount: number; discountAmountPaise: number; subtotalBeforeDiscount: number; subtotalAfterDiscount: number; subtotalAfterDiscountPaise: number; message: string; }

export async function applyCoupon(code: string): Promise<CouponApplication> {
  const response = await fetch(apiUrl('/cart/apply-coupon'), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code }) });
  if (!response.ok) throw new Error(`Coupon request failed (${response.status})`);
  return response.json() as Promise<CouponApplication>;
}

export async function removeCoupon(): Promise<void> {
  const response = await fetch(apiUrl('/cart/coupon'), { method: 'DELETE', credentials: 'include' });
  if (!response.ok) throw new Error(`Coupon request failed (${response.status})`);
}

export async function submitReview(product: string | number, review: { rating: number; text: string; location?: string }): Promise<void> {
  const response = await fetch(apiUrl(`/products/${product}/reviews`), { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(review) });
  if (!response.ok) throw new Error(`Review request failed (${response.status})`);
}

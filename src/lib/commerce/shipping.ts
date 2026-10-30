/** Mirrors the backend's authoritative order pricing policy for pre-order estimates. */
export const FREE_SHIPPING_THRESHOLD = 999;
export const STANDARD_SHIPPING_FEE = 99;

export function calculateShippingFee(subtotal: number): number {
  if (!Number.isFinite(subtotal) || subtotal < 0) return STANDARD_SHIPPING_FEE;
  return subtotal >= FREE_SHIPPING_THRESHOLD ? 0 : STANDARD_SHIPPING_FEE;
}

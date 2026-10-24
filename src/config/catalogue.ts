export interface PriceBounds { min: number; max: number }

/** Public UI configuration; never used as authority for checkout pricing. */
export function readPriceBounds(env: Record<string, string | undefined>): PriceBounds {
  const min = Number(env.VITE_CATALOGUE_PRICE_MIN ?? 0);
  const max = Number(env.VITE_CATALOGUE_PRICE_MAX ?? 100000);
  if (!Number.isSafeInteger(min) || !Number.isSafeInteger(max) || min < 0 || max <= min) {
    throw new Error('Catalogue price bounds must be whole nonnegative rupees with max greater than min');
  }
  return { min, max };
}

export const cataloguePriceBounds = readPriceBounds(import.meta.env);

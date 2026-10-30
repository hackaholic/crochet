import { describe, expect, it } from 'vitest';
import { calculateShippingFee } from './shipping';

describe('checkout shipping estimate', () => {
  it('matches the server fee below the free-shipping threshold', () => {
    expect(calculateShippingFee(799)).toBe(99);
    expect(799 + calculateShippingFee(799)).toBe(898);
  });

  it('uses free shipping at and above the threshold', () => {
    expect(calculateShippingFee(999)).toBe(0);
    expect(calculateShippingFee(1000)).toBe(0);
  });

  it('does not grant free shipping for invalid subtotal values', () => {
    expect(calculateShippingFee(Number.NaN)).toBe(99);
    expect(calculateShippingFee(-1)).toBe(99);
  });
});

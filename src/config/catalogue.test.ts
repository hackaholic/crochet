import { describe, expect, it } from 'vitest';
import { readPriceBounds } from './catalogue';
describe('catalogue price configuration', () => {
  it('uses defaults and environment-specific whole rupee bounds', () => {
    expect(readPriceBounds({})).toEqual({ min: 0, max: 100000 });
    expect(readPriceBounds({ VITE_CATALOGUE_PRICE_MIN: '100', VITE_CATALOGUE_PRICE_MAX: '50000' })).toEqual({ min: 100, max: 50000 });
  });
  it.each([['-1', '100'], ['2', '2'], ['100', '1'], ['0', 'Infinity'], ['bad', '100'], ['0', '10.5'], ['0', '1e30']])('rejects invalid bounds %s %s', (min, max) => {
    expect(() => readPriceBounds({ VITE_CATALOGUE_PRICE_MIN: min, VITE_CATALOGUE_PRICE_MAX: max })).toThrow(/Catalogue price bounds/);
  });
});

import { describe, expect, it } from 'vitest';
import { guestTrackingPath, pageFromPath, productPath, productSlug } from './routes';

const product = { id: 1, name: 'Fallback name', slug: 'forever-crochet-rose-bouquet', price: 2599, rating: 5, reviews: 0, image: '', category: 'Flowers' };

describe('storefront routes', () => {
  it('uses the catalogue slug for product URLs', () => {
    expect(productSlug(product)).toBe('forever-crochet-rose-bouquet');
    expect(productPath(product)).toBe('/products/forever-crochet-rose-bouquet');
  });

  it('maps supported and unknown paths', () => {
    expect(pageFromPath('/account')).toBe('account');
    expect(pageFromPath('/account/')).toBe('account');
    expect(pageFromPath('/shop')).toBe('shop');
    expect(pageFromPath('/shop/')).toBe('shop');
    expect(pageFromPath('/categories/flowers')).toBe('shop');
    expect(pageFromPath('/categories/amigurumi/')).toBe('shop');
    expect(pageFromPath('/collections/bestsellers')).toBe('shop');
    expect(pageFromPath('/products/forever-crochet-rose-bouquet')).toBe('product');
    expect(pageFromPath('/products/forever-crochet-rose-bouquet/')).toBe('product');
    expect(pageFromPath('/not-a-page')).toBe('notFound');
  });
});

it('recognizes guest tracking entry and scoped links only', () => {
  expect(pageFromPath('/track')).toBe('tracking');
  expect(pageFromPath('/track/TEST-1')).toBe('tracking');
  expect(pageFromPath('/track/TEST-1/extra')).toBe('notFound');
});

it('keeps checkout tracking credentials out of URL queries and encodes identifiers', () => {
  const link = new URL(guestTrackingPath('A/B', 'token+value'), 'https://example.invalid');
  expect(link.pathname).toBe('/track/A%2FB');
  expect(link.search).toBe('');
  expect(new URLSearchParams(link.hash.slice(1)).get('token')).toBe('token+value');
});

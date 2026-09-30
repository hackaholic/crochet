import { describe, expect, it } from 'vitest';
import { pageFromPath, productPath, productSlug } from './routes';

const product = { id: 1, name: 'Fallback name', slug: 'forever-crochet-rose-bouquet', price: 2599, rating: 5, reviews: 0, image: '', category: 'Flowers' };

describe('storefront routes', () => {
  it('uses the catalogue slug for product URLs', () => {
    expect(productSlug(product)).toBe('forever-crochet-rose-bouquet');
    expect(productPath(product)).toBe('/products/forever-crochet-rose-bouquet');
  });

  it('maps supported and unknown paths', () => {
    expect(pageFromPath('/account')).toBe('account');
    expect(pageFromPath('/products/forever-crochet-rose-bouquet')).toBe('product');
    expect(pageFromPath('/not-a-page')).toBe('notFound');
  });
});

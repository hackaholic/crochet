import { describe, expect, it } from 'vitest';
import { imageAttributes, sourceAttributes } from './image';
import { toProduct } from '../api/catalogue';

describe('API image attributes', () => {
  const metadata = { url: '/rose.png', altText: 'Red crochet roses in a bouquet', width: 1086, height: 1448 };
  it('preserves genuine dimensions and natural alt through catalogue mapping', () => {
    const product = toProduct({ id: 1, name: 'Rose bouquet', slug: 'rose', price: 10, currency: 'INR', category: 'Flowers', image: metadata.url, primaryImageMetadata: metadata });
    expect(imageAttributes(product.image, product.primaryImageMetadata, product.name)).toEqual({ alt: metadata.altText, width: 1086, height: 1448 });
  });
  it('picture source uses validated srcset without an alt attribute', () => {
    expect(sourceAttributes('/rose.png', { ...metadata, variants: [{ url: '/rose-small.webp', width: 480 }] })).toEqual({ width: 1086, height: 1448, srcSet: '/rose-small.webp 480w' });
  });
  it('does not apply primary metadata to a different gallery source', () => {
    expect(imageAttributes('/gallery.png', metadata, 'Rose bouquet')).toEqual({ alt: 'Rose bouquet' });
  });
  it('keeps decorative images silent and omits incomplete/invalid dimensions', () => {
    expect(imageAttributes('/rose.png', { ...metadata, height: null }, '')).toEqual({ alt: '' });
    expect(imageAttributes('/rose.png', { ...metadata, width: -1 }, 'Rose')).toEqual({ alt: metadata.altText });
    expect(imageAttributes('/rose.png', undefined, 'Rose')).toEqual({ alt: 'Rose' });
  });
  it('uses only supplied safe width variants, deduplicated and ordered', () => {
    expect(imageAttributes('/rose.png', { ...metadata, variants: [
      { url: '/rose-large.webp', width: 960, descriptor: '960w' },
      { url: 'https://images.example.com/rose.webp', width: 480 },
      { url: '/duplicate.webp', width: 480 },
      { url: 'javascript:alert(1)', width: 120 },
      { url: '//external.example/image', width: 200 },
      { url: '/injected.png,evil', width: 300 },
      { url: 'https://user:secret@example.com/image', width: 320 },
      { url: '/wrong-descriptor.png', width: 400, descriptor: '2x' },
    ] }, 'Rose').srcSet).toBe('https://images.example.com/rose.webp 480w, /rose-large.webp 960w');
  });
});

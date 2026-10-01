import { describe, expect, it } from 'vitest';
import type { Product } from '../data/products';
import type { Category, Collection } from './api/catalogue';
import { buildCategoryFilterOptions, buildCollectionFilterOptions, buildPriceFilterOptions, productMatchesCategory, sortShopProducts } from './shopFilters';

const products: Product[] = [
  { id: 1, name: 'Rose Bouquet', price: 899, rating: 5, reviews: 2, image: '/rose.webp', category: 'Bouquets', primaryCategory: { name: 'Bouquets', slug: 'bouquets' }, categories: [{ name: 'Bouquets', slug: 'bouquets' }], collections: [{ name: 'Birthday Gifts', slug: 'birthday-gifts' }] },
  { id: 2, name: 'Crochet Bunny', price: 1299, rating: 5, reviews: 3, image: '/bunny.webp', category: 'Bunny', primaryCategory: { name: 'Bunny', slug: 'bunny' }, categories: [{ name: 'Bunny', slug: 'bunny' }], collections: [{ name: 'Gifts for Kids', slug: 'gifts-for-kids' }] },
];

const categories: Category[] = [
  { id: 1, name: 'Flowers', slug: 'flowers', displayOrder: 1, isActive: true, productCount: 1, children: [
    { id: 2, name: 'Bouquets', slug: 'bouquets', parentId: 1, displayOrder: 1, isActive: true, productCount: 1, children: [] },
    { id: 3, name: 'Lilies', slug: 'lilies', parentId: 1, displayOrder: 2, isActive: true, productCount: 0, children: [] },
  ] },
];

describe('shop filter options', () => {
  it('includes descendant products in parent categories and removes empty categories', () => {
    const options = buildCategoryFilterOptions(categories, products);

    expect(options.map(option => [option.category.slug, option.productCount])).toEqual([
      ['flowers', 1],
      ['bouquets', 1],
    ]);
    expect(productMatchesCategory(products[0], options[0])).toBe(true);
  });

  it('removes empty collections and price ranges using current catalogue data', () => {
    const collections: Collection[] = [
      { id: 1, name: 'Birthday Gifts', slug: 'birthday-gifts', displayOrder: 1, productCount: 1 },
      { id: 2, name: 'Gifts for Him', slug: 'gifts-for-him', displayOrder: 2, productCount: 0 },
    ];

    expect(buildCollectionFilterOptions(collections, products).map(option => option.collection.slug)).toEqual(['birthday-gifts']);
    expect(buildPriceFilterOptions([
      { label: 'Under ₹299', min: 0, max: 299 },
      { label: '₹600 – ₹999', min: 600, max: 999 },
      { label: 'Above ₹999', min: 1000, max: Infinity },
    ], products).map(option => [option.range.label, option.productCount])).toEqual([
      ['₹600 – ₹999', 1],
      ['Above ₹999', 1],
    ]);
  });

  it('moves products carrying the backend-managed New badge to the front', () => {
    const newest = { ...products[1], badge: 'New' };
    expect(sortShopProducts([products[0], newest], 'Newest').map(product => product.id)).toEqual([2, 1]);
  });
});

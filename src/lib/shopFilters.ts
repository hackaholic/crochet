import type { Product } from '../data/products';
import type { Category, Collection } from './api/catalogue';

export interface CategoryFilterOption {
  category: Category;
  matchingSlugs: string[];
  productCount: number;
}

export interface CollectionFilterOption {
  collection: Collection;
  productCount: number;
}

export interface PriceRange {
  label: string;
  min: number;
  max: number;
}

export interface PriceFilterOption {
  index: number;
  range: PriceRange;
  productCount: number;
}

function productCategorySlugs(product: Product): Set<string> {
  return new Set([
    product.primaryCategory?.slug,
    ...(product.categories ?? []).map(category => category.slug),
  ].filter((slug): slug is string => Boolean(slug)));
}

function categoryAndDescendantSlugs(category: Category): string[] {
  return [
    category.slug,
    ...(category.children ?? []).flatMap(categoryAndDescendantSlugs),
  ];
}

export function buildCategoryFilterOptions(categories: Category[], products: Product[]): CategoryFilterOption[] {
  const productSlugs = products.map(productCategorySlugs);

  return categories.flatMap(category => {
    const matchingSlugs = categoryAndDescendantSlugs(category);
    const productCount = productSlugs.filter(slugs => matchingSlugs.some(slug => slugs.has(slug))).length;
    const children = buildCategoryFilterOptions(category.children ?? [], products);
    return productCount > 0 ? [{ category, matchingSlugs, productCount }, ...children] : children;
  });
}

export function buildCollectionFilterOptions(collections: Collection[], products: Product[]): CollectionFilterOption[] {
  return collections.flatMap(collection => {
    const productCount = products.filter(product => product.collections?.some(item => item.slug === collection.slug)).length;
    return productCount > 0 ? [{ collection, productCount }] : [];
  });
}

export function buildPriceFilterOptions(priceRanges: PriceRange[], products: Product[]): PriceFilterOption[] {
  return priceRanges.flatMap((range, index) => {
    const productCount = products.filter(product => product.price >= range.min && product.price <= range.max).length;
    return productCount > 0 ? [{ index, range, productCount }] : [];
  });
}

export function productMatchesCategory(product: Product, option: CategoryFilterOption): boolean {
  const slugs = productCategorySlugs(product);
  return option.matchingSlugs.some(slug => slugs.has(slug));
}

function slugify(value: string): string {
  return value.trim().toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

/** Match occasion IDs/slugs against backend-provided collection associations, tags, and occasions. */
export function productMatchesOccasion(product: Product, occasion: string): boolean {
  const target = slugify(occasion);
  if (!target) return false;
  return Boolean(
    product.collections?.some(collection => slugify(collection.slug) === target || slugify(collection.name) === target)
    || product.tags?.some(tag => slugify(tag) === target)
    || product.occasions?.some(occ => slugify(occ) === target)
  );
}

export function sortShopProducts(products: Product[], sortBy: string): Product[] {
  return [...products].sort((a, b) => {
    if (sortBy === 'Newest') return Number(b.badge === 'New') - Number(a.badge === 'New');
    if (sortBy === 'Price: Low to High') return a.price - b.price;
    if (sortBy === 'Price: High to Low') return b.price - a.price;
    if (sortBy === 'Best Selling') return b.reviews - a.reviews;
    return 0;
  });
}

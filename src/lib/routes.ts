import type { Product } from '../data/products';

export type AppPage = 'home' | 'shop' | 'product' | 'cart' | 'wishlist' | 'checkout' | 'account' | 'admin' | 'about' | 'contact' | 'shipping' | 'returns' | 'privacy' | 'terms' | 'notFound';

const pagePaths: Record<Exclude<AppPage, 'product' | 'notFound'>, string> = {
  home: '/',
  shop: '/shop',
  cart: '/cart',
  wishlist: '/wishlist',
  checkout: '/checkout',
  account: '/account',
  admin: '/admin',
  about: '/about',
  contact: '/contact',
  shipping: '/shipping-policy',
  returns: '/return-policy',
  privacy: '/privacy-policy',
  terms: '/terms',
};

export function pagePath(page: Exclude<AppPage, 'product' | 'notFound'>): string {
  return pagePaths[page];
}

export function productSlug(product: Product): string {
  if (product.slug) return product.slug;
  return product.name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

export function productPath(product: Product): string {
  return `/products/${productSlug(product)}`;
}

export function pageFromPath(pathname: string): AppPage {
  if (pathname.startsWith('/products/')) return 'product';
  if (pathname === '/shop') return 'shop';
  if (pathname === '/cart') return 'cart';
  if (pathname === '/wishlist') return 'wishlist';
  if (pathname === '/checkout') return 'checkout';
  if (pathname === '/account') return 'account';
  if (pathname === '/admin') return 'admin';
  if (pathname === '/about') return 'about';
  if (pathname === '/contact') return 'contact';
  if (pathname === '/shipping-policy') return 'shipping';
  if (pathname === '/return-policy') return 'returns';
  if (pathname === '/privacy-policy') return 'privacy';
  if (pathname === '/terms') return 'terms';
  if (pathname === '/') return 'home';
  return 'notFound';
}

import ProductCard from '../ProductCard';
import type { Product } from '../../data/products';
import type { ProductCollectionSection } from '../../lib/api/storefront';

export function uniqueProductsByImage(products: Product[]): Product[] {
  const seenIds = new Set<number>();
  const seenImages = new Set<string>();
  return products.filter(product => {
    const image = product.image.trim().split(/[?#]/, 1)[0].toLowerCase();
    if (seenIds.has(product.id) || (image && seenImages.has(image))) return false;
    seenIds.add(product.id);
    if (image) seenImages.add(image);
    return true;
  });
}

export default function ProductGrid({ section, wishlist, onAddToCart, onToggleWishlist, onProductClick }: { section: ProductCollectionSection; wishlist: number[]; onAddToCart: (product: Product) => void; onToggleWishlist: (product: Product) => void; onProductClick: (product: Product) => void }) {
  return <section className="bg-white py-14 sm:py-16"><div className="storefront-shell"><header className="mb-8 text-center sm:mb-10">{section.eyebrow && <p className="text-xs font-semibold uppercase tracking-widest text-[#C4622D]">{section.eyebrow}</p>}<h2 className="mt-3 text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>{section.title}</h2>{section.description && <p className="mx-auto mt-3 max-w-2xl text-[#8B6B4A]">{section.description}</p>}</header><div data-testid="product-grid" className="grid grid-cols-2 gap-4 md:grid-cols-4">{uniqueProductsByImage(section.products).map(product => <ProductCard key={product.id} product={product} isWishlisted={wishlist.includes(product.id)} onAddToCart={onAddToCart} onToggleWishlist={onToggleWishlist} onProductClick={onProductClick} />)}</div></div></section>;
}

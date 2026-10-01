import ProductCard from '../ProductCard';
import type { Product } from '../../data/products';
import type { ProductCollectionSection } from '../../lib/api/storefront';

export default function ProductGrid({ section, wishlist, onAddToCart, onToggleWishlist, onProductClick }: { section: ProductCollectionSection; wishlist: number[]; onAddToCart: (product: Product) => void; onToggleWishlist: (product: Product) => void; onProductClick: (product: Product) => void }) {
  return <section className="bg-white py-14 sm:py-16"><div className="storefront-shell"><header className="mb-8 sm:mb-10">{section.eyebrow && <p className="text-xs font-semibold uppercase tracking-widest text-[#C4622D]">{section.eyebrow}</p>}<h2 className="mt-3 text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>{section.title}</h2></header><div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 lg:gap-6 xl:grid-cols-5">{section.products.map(product => <ProductCard key={product.id} product={product} isWishlisted={wishlist.includes(product.id)} onAddToCart={onAddToCart} onToggleWishlist={onToggleWishlist} onProductClick={onProductClick} />)}</div></div></section>;
}

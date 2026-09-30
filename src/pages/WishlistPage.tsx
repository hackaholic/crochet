import ProductCard from '../components/ProductCard';
import { ArrowRightIcon } from '../components/Icons';
import type { Product } from '../data/products';
import { EmptyState } from '../components/StorefrontState';
import { useCatalogue } from '../components/CatalogueProvider';

interface WishlistPageProps {
  wishlist: number[];
  onAddToCart: (product: Product) => void;
  onToggleWishlist: (product: Product) => void;
  onProductClick: (product: Product) => void;
  onNavigate: (page: 'home' | 'shop' | 'product' | 'cart' | 'wishlist' | 'checkout' | 'about') => void;
}

export default function WishlistPage({ wishlist, onAddToCart, onToggleWishlist, onProductClick, onNavigate }: WishlistPageProps) {
  const { products } = useCatalogue();
  const items = products.filter(p => wishlist.includes(p.id));

  return (
    <div className="min-h-screen bg-[#FAF7F2] pt-28">
      <div className="max-w-7xl mx-auto px-4 py-10">
        <div className="flex items-end justify-between mb-10">
          <div>
            <h1 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>My Wishlist</h1>
            <p className="text-[#8B6B4A] mt-1">{items.length} saved item{items.length !== 1 ? 's' : ''}</p>
          </div>
          {items.length > 0 && (
            <button onClick={() => onNavigate('shop')} className="flex items-center gap-2 text-[#C4622D] font-semibold hover:gap-3 transition-all text-sm">
              Continue shopping <ArrowRightIcon size={16} />
            </button>
          )}
        </div>

        {items.length === 0 ? (
          <EmptyState icon="🤍" title="Your wishlist is empty" description="Save items you love by clicking the heart icon on any product" action={{ label: 'Explore Collection', onClick: () => onNavigate('shop') }} />
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 lg:gap-5">
            {items.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={onAddToCart}
                onToggleWishlist={onToggleWishlist}
                isWishlisted={true}
                onProductClick={onProductClick}
              />
            ))}
          </div>
        )}

        {items.length > 0 && (
          <div className="mt-12 text-center">
            <button
              onClick={() => items.forEach(p => onAddToCart(p))}
              className="px-10 py-4 bg-[#2C1810] text-white rounded-full font-semibold hover:bg-[#C4622D] transition-colors"
            >
              Add All to Basket
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

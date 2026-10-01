import { useState } from 'react';
import { HeartIcon, StarIcon } from './Icons';
import type { Product } from '../data/products';

interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
  onToggleWishlist: (product: Product) => void;
  isWishlisted: boolean;
  onProductClick: (product: Product) => void;
}

const badgeColor: Record<string, string> = {
  Bestseller: 'bg-[#C4622D] text-white',
  New: 'bg-[#8FAF8C] text-white',
  Limited: 'bg-[#C5B9D6] text-[#2C1810]',
  Handmade: 'bg-[#EDE4D0] text-[#8B6B4A]',
  Customizable: 'bg-[#F2C4CE] text-[#C4622D]',
};

export default function ProductCard({ product, onAddToCart, onToggleWishlist, isWishlisted, onProductClick }: ProductCardProps) {
  const [adding, setAdding] = useState(false);

  const handleAdd = (e: React.MouseEvent) => {
    e.stopPropagation();
    setAdding(true);
    onAddToCart(product);
    setTimeout(() => setAdding(false), 800);
  };

  const handleWishlist = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleWishlist(product);
  };

  return (
    <div
      data-testid="product-card"
      className="product-card group flex h-full cursor-pointer flex-col overflow-hidden rounded-2xl bg-white"
      style={{ boxShadow: '0 2px 16px rgba(44,24,16,0.07)', transition: 'all 0.3s ease' }}
      onClick={() => onProductClick(product)}
      onMouseEnter={e => { (e.currentTarget as HTMLElement).style.boxShadow = '0 8px 32px rgba(44,24,16,0.13)'; (e.currentTarget as HTMLElement).style.transform = 'translateY(-3px)'; }}
      onMouseLeave={e => { (e.currentTarget as HTMLElement).style.boxShadow = '0 2px 16px rgba(44,24,16,0.07)'; (e.currentTarget as HTMLElement).style.transform = 'translateY(0)'; }}
    >
      {/* Image */}
      <div data-testid="product-image-frame" className="relative aspect-[3/4] w-full shrink-0 overflow-hidden bg-[#F5EDE0]">
        <img
          src={product.image}
          alt={product.name}
          loading="lazy"
          decoding="async"
          sizes="(min-width: 1024px) 25vw, (min-width: 768px) 33vw, 50vw"
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        {/* Badge */}
        {product.badge && (
          <span className={`absolute top-3 left-3 text-xs font-semibold px-2.5 py-1 rounded-full ${badgeColor[product.badge] || 'bg-white text-[#2C1810]'}`}>
            {product.badge}
          </span>
        )}
        {/* Wishlist */}
        <button
          className="absolute top-3 right-3 w-9 h-9 rounded-full bg-white flex items-center justify-center shadow-sm transition-all duration-200 hover:scale-110"
          onClick={handleWishlist}
          aria-label="Toggle wishlist"
        >
          <HeartIcon size={16} filled={isWishlisted} className={isWishlisted ? 'text-[#C4622D]' : 'text-[#8B6B4A]'} />
        </button>
        {/* Quick add — slides up on hover */}
        <div className="quick-add-btn absolute bottom-0 left-0 right-0 opacity-0 translate-y-2 transition-all duration-300 group-hover:opacity-100 group-hover:translate-y-0">
          <button
            className={`w-full py-2.5 text-sm font-semibold transition-colors ${adding ? 'bg-[#8FAF8C] text-white' : 'bg-[#2C1810] text-white hover:bg-[#C4622D]'}`}
            onClick={handleAdd}
          >
            {adding ? '✓ Added!' : 'Quick Add'}
          </button>
        </div>
      </div>
      {/* Info */}
      <div className="flex flex-1 flex-col p-4">
        <p className="text-xs text-[#8B6B4A] font-medium mb-1">{product.category}</p>
        <h3 className="mb-2 min-h-10 line-clamp-2 text-sm font-semibold leading-snug text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>
          {product.name}
        </h3>
        <div className="flex items-center gap-1.5 mb-3">
          <div className="flex">
            {[1,2,3,4,5].map(i => (
              <StarIcon key={i} size={12} filled={i <= Math.floor(product.rating)} className="text-[#C4622D]" />
            ))}
          </div>
          <span className="text-xs text-[#8B6B4A]">({product.reviews})</span>
        </div>
        <div className="mt-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-bold text-[#2C1810]">₹{product.price}</span>
            {product.originalPrice && (
              <span className="text-xs text-[#8B6B4A] line-through">₹{product.originalPrice}</span>
            )}
          </div>
          {product.customizable && (
            <span className="text-xs text-[#C4622D] font-medium">Customizable</span>
          )}
        </div>
      </div>
    </div>
  );
}

import DestinationLink from '../components/DestinationLink';
import { imageAttributes } from '../lib/media/image';
import SeoBreadcrumbs from '../components/SeoBreadcrumbs';
import type { SeoMetadata } from '../lib/api/seo';
import ProductInformationAccordion from '../components/ProductInformationAccordion';
import { useState } from 'react';
import ProductCard from '../components/ProductCard';
import { HeartIcon, StarIcon, ChevronLeftIcon, ChevronRightIcon, CheckIcon, PackageIcon, ArrowRightIcon } from '../components/Icons';
import type { Product } from '../data/products';
import { useCatalogue } from '../components/CatalogueProvider';
import { submitReview } from '../lib/api/promotions';

interface ProductPageProps {
  seoMetadata?: SeoMetadata;
  product: Product | null;
  onAddToCart: (product: Product, quantity?: number, personalization?: Record<string, unknown>) => void;
  onToggleWishlist: (product: Product) => void;
  wishlist: number[];
  onProductClick: (product: Product) => void;
  onNavigate: (page: 'home' | 'shop' | 'product' | 'cart' | 'wishlist' | 'checkout' | 'about') => void;
}

export default function ProductPage({ seoMetadata, product: initialProduct, onAddToCart, onToggleWishlist, wishlist, onProductClick, onNavigate }: ProductPageProps) {
  const { products, categories } = useCatalogue();
  const product = initialProduct || products[0];
  if (!product) return null;
  const entity = seoMetadata?.productEntity?.id === product.id ? seoMetadata.productEntity : undefined;
  const description = entity?.description !== undefined ? entity.description : product.description;
  const rating = entity?.aggregateRating?.provenance === 'VERIFIED_REVIEWS' && entity.aggregateRating.reviewCount > 0 ? entity.aggregateRating : undefined;
  const images = product.images || [product.image, product.image, product.image, product.image];

  const [activeImg, setActiveImg] = useState(0);
  const [quantity, setQuantity] = useState(1);
  const [note, setNote] = useState('');
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewText, setReviewText] = useState('');
  const [reviewMessage, setReviewMessage] = useState('');
  const [reviewBusy, setReviewBusy] = useState(false);
  const sendReview = async () => { if (!reviewText.trim()) { setReviewMessage('Please write a short review first.'); return; } setReviewBusy(true); try { await submitReview(product.slug ?? product.id, { rating: reviewRating, text: reviewText.trim() }); setReviewText(''); setReviewMessage('Thank you — your review has been submitted.'); } catch { setReviewMessage('Please sign in before submitting a review.'); } finally { setReviewBusy(false); } };
  const [added, setAdded] = useState(false);

  const isWishlisted = wishlist.includes(product.id);

  const handleAddToCart = () => {
    onAddToCart(product, quantity, note.trim() ? {note: note.trim()} : undefined);
    setAdded(true);
    setTimeout(() => setAdded(false), 1500);
  };

  const handleBuyNow = () => {
    onAddToCart(product, quantity, note.trim() ? {note: note.trim()} : undefined);
    onNavigate('cart');
  };

  const related = products.filter(p => p.id !== product.id && (p.category === product.category || p.tags?.some(t => product.tags?.includes(t)))).slice(0, 4);

  return (
    <div className="min-h-screen bg-[#FAF7F2] pt-28 pb-24 lg:pb-0">

      <SeoBreadcrumbs metadata={seoMetadata} categories={categories} />
      <div className="storefront-shell py-8">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16">
          {/* ── Gallery ── */}
          <div>
            {/* Main image */}
            <div className="relative rounded-3xl overflow-hidden bg-[#F5EDE0] mb-4" style={{ aspectRatio: '1/1' }}>
              <img
                src={images[activeImg]}
                {...imageAttributes(images[activeImg], seoMetadata?.productEntity?.media?.find(media => media.url === images[activeImg]) ?? product.primaryImageMetadata, product.name)}
                loading="eager"
                fetchPriority="high"
                decoding="async"
                sizes="(min-width: 1024px) 50vw, 100vw"
                className="w-full h-full object-cover transition-opacity duration-300"
              />
              {/* Nav arrows */}
              <button
                onClick={() => setActiveImg(i => (i - 1 + images.length) % images.length)}
                className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/90 rounded-full flex items-center justify-center shadow-md hover:bg-white transition-colors"
                aria-label="Previous product image"
              >
                <ChevronLeftIcon size={18} className="text-[#2C1810]" />
              </button>
              <button
                onClick={() => setActiveImg(i => (i + 1) % images.length)}
                className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/90 rounded-full flex items-center justify-center shadow-md hover:bg-white transition-colors"
                aria-label="Next product image"
              >
                <ChevronRightIcon size={18} className="text-[#2C1810]" />
              </button>
              {/* Badge */}
              {product.badge && (
                <span className="absolute top-4 left-4 bg-[#C4622D] text-white text-xs font-bold px-3 py-1.5 rounded-full">
                  {product.badge}
                </span>
              )}
            </div>
            {/* Thumbnails */}
            <div className="flex gap-3">
              {images.map((img, i) => (
                <button
                  aria-label={`View product image ${i + 1}`}
                  key={i}
                  onClick={() => setActiveImg(i)}
                  className={`w-20 h-20 rounded-xl overflow-hidden border-2 transition-all shrink-0 ${i === activeImg ? 'border-[#C4622D]' : 'border-transparent opacity-60 hover:opacity-80'}`}
                >
                  <img src={img} {...imageAttributes(img, seoMetadata?.productEntity?.media?.find(media => media.url === img), '')} loading="lazy" decoding="async" sizes="80px" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          </div>

          {/* ── Product Info ── */}
          <div>
            <p className="text-xs text-[#8B6B4A] font-medium tracking-widest uppercase mb-3">{product.category}</p>
            <h1 className="text-3xl lg:text-4xl font-medium text-[#2C1810] leading-tight mb-4" style={{ fontFamily: 'var(--font-serif)' }}>
              {product.name}
            </h1>

            {/* Verified rating only; catalogue seed ratings are not review evidence. */}
            {rating && <div className="flex items-center gap-3 mb-6">
              <div className="flex">
                {[1,2,3,4,5].map(i => (
                  <StarIcon key={i} size={16} filled={i <= Math.floor(rating.ratingValue)} className="text-[#C4622D]" />
                ))}
              </div>
              <span className="text-sm font-semibold text-[#2C1810]">{rating.ratingValue}</span>
              <span className="text-sm text-[#8B6B4A]">({rating.reviewCount} reviews)</span>
            </div>}

            {/* Price */}
            <div className="flex items-baseline gap-3 mb-6">
              <span className="text-4xl font-bold text-[#2C1810]">₹{product.price}</span>
              {product.originalPrice && (
                <>
                  <span className="text-lg text-[#8B6B4A] line-through">₹{product.originalPrice}</span>
                  <span className="text-sm font-semibold text-[#8FAF8C] bg-[#EBF3EA] px-2.5 py-1 rounded-full">
                    {Math.round((1 - product.price / product.originalPrice) * 100)}% OFF
                  </span>
                </>
              )}
            </div>

            {/* Description */}
            {description?.trim() && <p className="text-[#5C3D2E] leading-relaxed whitespace-pre-line break-words mb-8">{description}</p>}

            {/* Quantity */}
            <div className="mb-6">
              <label className="text-sm font-semibold text-[#2C1810] block mb-3">Quantity</label>
              <div className="flex items-center gap-3 w-fit border border-[#EDE4D0] rounded-full px-4 py-2">
                <button
                  onClick={() => setQuantity(q => Math.max(1, q - 1))}
                  className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-[#F5EDE0] transition-colors text-[#5C3D2E] text-lg font-bold"
                >
                  −
                </button>
                <span className="w-8 text-center font-bold text-[#2C1810]">{quantity}</span>
                <button
                  onClick={() => setQuantity(q => q + 1)}
                  className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-[#F5EDE0] transition-colors text-[#5C3D2E] text-lg font-bold"
                >
                  +
                </button>
              </div>
            </div>

            {/* Personalized note */}
            <div className="mb-8">
              <label htmlFor="product-personalization-note" className="text-sm font-semibold text-[#2C1810] block mb-2">Add a Personalized Note (optional)</label>
              <textarea
                id="product-personalization-note"
                value={note}
                onChange={e => setNote(e.target.value)}
                placeholder="e.g. Happy Anniversary! With all my love..."
                rows={3}
                className="w-full px-4 py-3 border border-[#EDE4D0] rounded-xl text-sm text-[#5C3D2E] placeholder-[#C5B9D6] focus:outline-none focus:border-[#C4622D] transition-colors resize-none bg-white"
              />
            </div>

            {/* CTAs */}
            <div className="flex gap-3 mb-6">
              <button
                onClick={handleAddToCart}
                className={`flex-1 py-4 rounded-full font-semibold text-sm transition-all ${added ? 'bg-[#8FAF8C] text-white' : 'bg-[#2C1810] text-white hover:bg-[#C4622D]'}`}
              >
                {added ? '✓ Added to Basket!' : 'Add to Basket'}
              </button>
              <button
                onClick={() => onToggleWishlist(product)}
                className={`w-14 h-14 rounded-full flex items-center justify-center border-2 transition-all ${isWishlisted ? 'bg-[#F2C4CE] border-[#C4622D] text-[#C4622D]' : 'border-[#EDE4D0] text-[#8B6B4A] hover:border-[#C4622D]'}`}
                aria-label="Add to wishlist"
              >
                <HeartIcon size={20} filled={isWishlisted} />
              </button>
            </div>
            <button onClick={handleBuyNow} className="w-full py-4 bg-[#C4622D] text-white rounded-full font-semibold hover:bg-[#D4795A] transition-all mb-6">
              Buy Now
            </button>

            <ProductInformationAccordion productId={product.slug ?? product.id} initialInformation={entity} />
          </div>
        </div>

        {/* You may also like */}
        {related.length > 0 && (
          <div className="mt-20">
            <div className="flex items-end justify-between mb-8">
              <h2 className="text-3xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>You May Also Like</h2>
              <DestinationLink href="/shop" onNavigate={() => onNavigate('shop')} className="text-[#C4622D] text-sm font-semibold flex items-center gap-1 hover:gap-2 transition-all">
                View all <ArrowRightIcon size={16} />
              </DestinationLink>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 lg:gap-5">
              {related.map(p => (
                <ProductCard
                  key={p.id}
                  product={p}
                  onAddToCart={onAddToCart}
                  onToggleWishlist={onToggleWishlist}
                  isWishlisted={wishlist.includes(p.id)}
                  onProductClick={onProductClick}
                />
              ))}
            </div>
          </div>
        )}

        {/* Reviews */}
        <div className="mt-20">
          <h2 className="text-3xl font-medium text-[#2C1810] mb-8" style={{ fontFamily: 'var(--font-serif)' }}>Customer Reviews</h2>
          <div className="mb-6 rounded-2xl border border-[#EDE4D0] bg-white p-5"><p className="font-semibold text-[#2C1810]">Share your experience</p><div className="mt-3 flex gap-1">{[1,2,3,4,5].map(star => <button key={star} onClick={() => setReviewRating(star)} aria-label={`${star} stars`}><StarIcon size={18} filled={star <= reviewRating} className="text-[#C4622D]" /></button>)}</div><textarea value={reviewText} onChange={event => setReviewText(event.target.value)} placeholder="What did you love about it?" rows={3} className="mt-3 w-full rounded-xl border border-[#EDE4D0] p-3 text-sm" /><button onClick={sendReview} disabled={reviewBusy} className="mt-3 rounded-full bg-[#C4622D] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50">{reviewBusy ? 'Submitting…' : 'Submit review'}</button>{reviewMessage && <p className="mt-2 text-sm text-[#8B6B4A]" role="status">{reviewMessage}</p>}</div>

        </div>
      </div>

      <div className="fixed inset-x-0 bottom-0 z-40 border-t border-[#EDE4D0] bg-white/95 px-4 py-3 shadow-[0_-8px_24px_rgba(44,24,16,0.08)] backdrop-blur md:hidden">
        <div className="mx-auto flex max-w-md items-center gap-3">
          <div className="min-w-0">
            <p className="text-xs text-[#8B6B4A]">{quantity} item{quantity !== 1 ? 's' : ''}</p>
            <p className="font-bold text-[#2C1810]">₹{product.price * quantity}</p>
          </div>
          <button onClick={handleAddToCart} className={`ml-auto rounded-full px-5 py-3 text-sm font-semibold text-white transition-colors ${added ? 'bg-[#8FAF8C]' : 'bg-[#2C1810] active:bg-[#C4622D]'}`}>
            {added ? 'Added' : 'Add to Basket'}
          </button>
        </div>
      </div>
    </div>
  );
}

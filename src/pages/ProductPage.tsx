import { useState } from 'react';
import { reviews } from '../data/products';
import ProductCard from '../components/ProductCard';
import { HeartIcon, StarIcon, ChevronLeftIcon, ChevronRightIcon, CheckIcon, PackageIcon, ArrowRightIcon } from '../components/Icons';
import type { Product } from '../data/products';
import { useCatalogue } from '../components/CatalogueProvider';
import { submitReview } from '../lib/api/promotions';

interface ProductPageProps {
  product: Product | null;
  onAddToCart: (product: Product, quantity?: number) => void;
  onToggleWishlist: (product: Product) => void;
  wishlist: number[];
  onProductClick: (product: Product) => void;
  onNavigate: (page: 'home' | 'shop' | 'product' | 'cart' | 'wishlist' | 'checkout' | 'about') => void;
}

const colors = ['#F2C4CE', '#C4622D', '#8FAF8C', '#C5B9D6', '#EDE4D0', '#2C1810', '#F5E0D3', '#8B6B4A'];

const infoSections = [
  {
    title: 'Handmade Details',
    content: 'This piece is 100% handcrafted using traditional crochet techniques. Each stitch is placed with care and attention to detail, resulting in a unique creation that may vary slightly from the images shown — that\'s what makes it truly yours.',
  },
  {
    title: 'Materials Used',
    content: 'Premium mercerized cotton yarn (100% cotton), non-toxic stuffing (for amigurumi), and stainless steel wire for shape support where needed. All materials are child-safe and tested.',
  },
  {
    title: 'Size & Dimensions',
    content: 'Bouquet: approximately 30–35 cm height. Stems are wrapped in floral tape with crochet overlay. Each piece ships with a care card listing exact dimensions.',
  },
  {
    title: 'Processing Time',
    content: 'Standard orders: 3–5 working days. Custom orders: 7–10 working days. Bulk orders above 5 units may take up to 14 working days.',
  },
  {
    title: 'Care Instructions',
    content: 'Gently dust with a soft dry cloth. Avoid prolonged direct sunlight to prevent colour fading. Keep away from moisture. Do not machine wash.',
  },
  {
    title: 'Shipping & Delivery',
    content: 'Ships across India via reputable courier partners. Free shipping on orders above ₹999. Express delivery available at checkout. Estimated delivery: 5–7 working days.',
  },
];

export default function ProductPage({ product: initialProduct, onAddToCart, onToggleWishlist, wishlist, onProductClick, onNavigate }: ProductPageProps) {
  const { products } = useCatalogue();
  const product = initialProduct || products[0];
  if (!product) return null;
  const images = product.images || [product.image, product.image, product.image, product.image];

  const [activeImg, setActiveImg] = useState(0);
  const [selectedColor, setSelectedColor] = useState(colors[0]);
  const [quantity, setQuantity] = useState(1);
  const [note, setNote] = useState('');
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewText, setReviewText] = useState('');
  const [reviewMessage, setReviewMessage] = useState('');
  const [reviewBusy, setReviewBusy] = useState(false);
  const sendReview = async () => { if (!reviewText.trim()) { setReviewMessage('Please write a short review first.'); return; } setReviewBusy(true); try { await submitReview(product.slug ?? product.id, { rating: reviewRating, text: reviewText.trim() }); setReviewText(''); setReviewMessage('Thank you — your review has been submitted.'); } catch { setReviewMessage('Please sign in before submitting a review.'); } finally { setReviewBusy(false); } };
  const [openSection, setOpenSection] = useState<string | null>('Handmade Details');
  const [added, setAdded] = useState(false);

  const isWishlisted = wishlist.includes(product.id);

  const handleAddToCart = () => {
    onAddToCart(product, quantity);
    setAdded(true);
    setTimeout(() => setAdded(false), 1500);
  };

  const handleBuyNow = () => {
    onAddToCart(product, quantity);
    onNavigate('cart');
  };

  const related = products.filter(p => p.id !== product.id && (p.category === product.category || p.tags?.some(t => product.tags?.includes(t)))).slice(0, 4);

  return (
    <div className="min-h-screen bg-[#FAF7F2] pt-28 pb-24 lg:pb-0">
      {/* Breadcrumb */}
      <div className="storefront-shell pb-2 pt-6">
        <p className="text-xs text-[#8B6B4A]">
          <button onClick={() => onNavigate('home')} className="hover:text-[#C4622D]">Home</button>
          {' / '}
          <button onClick={() => onNavigate('shop')} className="hover:text-[#C4622D]">Shop</button>
          {' / '}
          <span className="text-[#2C1810]">{product.name}</span>
        </p>
      </div>

      <div className="storefront-shell py-8">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16">
          {/* ── Gallery ── */}
          <div>
            {/* Main image */}
            <div className="relative rounded-3xl overflow-hidden bg-[#F5EDE0] mb-4" style={{ aspectRatio: '1/1' }}>
              <img
                src={images[activeImg]}
                alt={product.name}
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
                  key={i}
                  onClick={() => setActiveImg(i)}
                  className={`w-20 h-20 rounded-xl overflow-hidden border-2 transition-all shrink-0 ${i === activeImg ? 'border-[#C4622D]' : 'border-transparent opacity-60 hover:opacity-80'}`}
                >
                  <img src={img} alt="" loading="lazy" decoding="async" sizes="80px" className="w-full h-full object-cover" />
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

            {/* Rating */}
            <div className="flex items-center gap-3 mb-6">
              <div className="flex">
                {[1,2,3,4,5].map(i => (
                  <StarIcon key={i} size={16} filled={i <= Math.floor(product.rating)} className="text-[#C4622D]" />
                ))}
              </div>
              <span className="text-sm font-semibold text-[#2C1810]">{product.rating}</span>
              <span className="text-sm text-[#8B6B4A]">({product.reviews} reviews)</span>
            </div>

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
            <p className="text-[#5C3D2E] leading-relaxed mb-8">
              {product.description || 'A beautiful handcrafted crochet creation made with premium cotton yarn. Each piece is stitched by hand with care, bringing warmth and artistry to your home or loved ones.'}
            </p>

            {/* Color selection */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <label className="text-sm font-semibold text-[#2C1810]">Flower Color</label>
                <span className="text-xs text-[#8B6B4A]">50+ options available</span>
              </div>
              <div className="flex gap-2.5 flex-wrap">
                {colors.map(color => (
                  <button
                    key={color}
                    onClick={() => setSelectedColor(color)}
                    className="w-9 h-9 rounded-full border-2 shadow-sm transition-all hover:scale-110"
                    style={{ background: color, borderColor: selectedColor === color ? '#2C1810' : 'transparent', outline: selectedColor === color ? '2px solid #2C1810' : 'none', outlineOffset: '2px' }}
                    aria-label={`Color ${color}`}
                  />
                ))}
              </div>
            </div>

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
              <label className="text-sm font-semibold text-[#2C1810] block mb-2">Add a Personalized Note (optional)</label>
              <textarea
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

            {/* Trust badges */}
            <div className="grid grid-cols-3 gap-3 py-5 border-y border-[#EDE4D0] mb-8">
              {[
                { icon: '✋', text: '100% Handmade' },
                { icon: '🚚', text: 'Free Shipping ₹999+' },
                { icon: '💝', text: 'Gift Wrapping' },
              ].map(({ icon, text }) => (
                <div key={text} className="text-center text-xs text-[#8B6B4A]">
                  <div className="text-xl mb-1">{icon}</div>
                  <span className="font-medium">{text}</span>
                </div>
              ))}
            </div>

            {/* Handmade notice */}
            <div className="bg-[#F5EDE0] rounded-xl p-4 mb-6 flex gap-3">
              <span className="text-xl shrink-0">🪡</span>
              <p className="text-xs text-[#8B6B4A] leading-relaxed italic">
                Every item is handmade, therefore small variations make each piece unique — and that's what makes it special.
              </p>
            </div>

            {/* Info accordion */}
            <div className="space-y-0">
              {infoSections.map(({ title, content }) => (
                <div key={title} className="border-b border-[#EDE4D0]">
                  <button
                    onClick={() => setOpenSection(openSection === title ? null : title)}
                    className="flex items-center justify-between w-full py-4 text-left"
                  >
                    <span className="font-semibold text-[#2C1810] text-sm">{title}</span>
                    <span className="text-[#8B6B4A] text-xl leading-none">{openSection === title ? '−' : '+'}</span>
                  </button>
                  {openSection === title && (
                    <p className="pb-4 text-sm text-[#5C3D2E] leading-relaxed">{content}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* You may also like */}
        {related.length > 0 && (
          <div className="mt-20">
            <div className="flex items-end justify-between mb-8">
              <h2 className="text-3xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>You May Also Like</h2>
              <button onClick={() => onNavigate('shop')} className="text-[#C4622D] text-sm font-semibold flex items-center gap-1 hover:gap-2 transition-all">
                View all <ArrowRightIcon size={16} />
              </button>
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
          <div className="grid md:grid-cols-2 gap-6">
            {reviews.map(review => (
              <div key={review.id} className="bg-white rounded-2xl p-6 border border-[#EDE4D0]">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <img src={review.image} alt={review.name} className="w-10 h-10 rounded-full object-cover" />
                    <div>
                      <p className="font-semibold text-[#2C1810] text-sm">{review.name}</p>
                      <p className="text-xs text-[#8B6B4A]">{review.location}</p>
                    </div>
                  </div>
                  <span className="text-xs text-[#8B6B4A]">{review.date}</span>
                </div>
                <div className="flex mb-2">
                  {[1,2,3,4,5].map(i => (
                    <StarIcon key={i} size={13} filled={i <= review.rating} className="text-[#C4622D]" />
                  ))}
                </div>
                <p className="text-sm text-[#5C3D2E] leading-relaxed italic">"{review.text}"</p>
                <p className="text-xs text-[#8B6B4A] mt-3 font-medium">Purchased: {review.product}</p>
              </div>
            ))}
          </div>
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

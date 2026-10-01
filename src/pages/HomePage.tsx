import { useEffect, useRef, useState } from 'react';
import { reviews } from '../data/products';
import ProductCard from '../components/ProductCard';
import { ArrowRightIcon, ChevronLeftIcon, ChevronRightIcon, FlowerDecor, StarIcon, ThreadCurve } from '../components/Icons';
import type { Product } from '../data/products';
import { useCatalogue } from '../components/CatalogueProvider';
import HeroCarousel from '../components/HeroCarousel';
import HomepageSections from '../components/home/HomepageSections';
import { getStorefrontHome, type HomepageCampaign, type HomepageSection } from '../lib/api/storefront';

type Page = 'home' | 'shop' | 'product' | 'cart' | 'wishlist' | 'checkout' | 'about';

interface HomePageProps {
  onNavigate: (page: Page) => void;
  onAddToCart: (product: Product) => void;
  onToggleWishlist: (product: Product) => void;
  wishlist: number[];
  onProductClick: (product: Product) => void;
}

const processSteps = [
  { icon: '🧶', step: 'Yarn', desc: 'Premium quality cotton and wool yarns in over 50 colours' },
  { icon: '✏️', step: 'Design', desc: 'Each pattern is sketched with intention and artistry' },
  { icon: '🪡', step: 'Hand Crocheting', desc: 'Stitched stitch by stitch by skilled artisans' },
  { icon: '✨', step: 'Finishing', desc: 'Every piece is inspected, trimmed and perfected' },
  { icon: '📦', step: 'Packaging', desc: 'Wrapped beautifully in tissue and branded boxes' },
  { icon: '❤️', step: 'Delivered with Love', desc: 'Dispatched with a handwritten note of care' },
];

const instagramImages = [
  'photo-1700171518313-5dd219beaaa6',
  'photo-1700171394718-2457b1190444',
  'photo-1700170447159-9d2d0da133a5',
  'photo-1700171458554-46cfd3f2a87a',
  'photo-1602773974733-b56200c8653f',
  'photo-1753370241607-5d48d8aaa70e',
  'photo-1632649027900-389e810204e6',
  'photo-1618574760337-2750f6251d20',
  'photo-1646182504823-a02b768e28b5',
];

const uniqueProducts = (items: Product[]) => Array.from(new Map(items.map(product => [product.id, product])).values());

export default function HomePage({ onNavigate, onAddToCart, onToggleWishlist, wishlist, onProductClick }: HomePageProps) {
  const { products, categories, collections } = useCatalogue();
  const bestsellers = uniqueProducts(products.filter(p => p.badge === 'Bestseller').concat(products.slice(0, 4)));
  const romantic = products.filter(p => p.tags?.includes('romantic'));
  const pooja = products.filter(p => p.category === 'Pooja');
  const amigurumi = products.filter(p => p.category === 'Amigurumi');

  const scrollRef = useRef<HTMLDivElement>(null);
  const scroll = (dir: 'l' | 'r') => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({ left: dir === 'r' ? 320 : -320, behavior: 'smooth' });
    }
  };

  const [heroCampaigns, setHeroCampaigns] = useState<HomepageCampaign[]>([]);
  const [homepageSections, setHomepageSections] = useState<HomepageSection[]>([]);
  const [heroLoading, setHeroLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    getStorefrontHome(controller.signal)
      .then(content => {
        setHeroCampaigns(content.hero.slice(0, 5));
        setHomepageSections(content.sections);
      })
      .catch(() => setHeroCampaigns([]))
      .finally(() => { if (!controller.signal.aborted) setHeroLoading(false); });
    return () => controller.abort();
  }, []);

  return (
    <div className="bg-[#FAF7F2]">
      <HeroCarousel campaigns={heroCampaigns} loading={heroLoading} onShop={() => onNavigate('shop')} onCustom={() => onNavigate('about')} />

      {heroLoading ? (
        <section className="storefront-shell py-12 sm:py-16" aria-busy="true" aria-label="Loading homepage sections">
          <div className="mb-8 h-8 w-64 animate-pulse rounded-lg bg-[#EDE4D0]" />
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {Array.from({ length: 4 }, (_, index) => <div key={index} className="aspect-[3/4] animate-pulse rounded-2xl bg-[#EDE4D0]" />)}
          </div>
        </section>
      ) : homepageSections.length > 0 ? (
        <HomepageSections
          sections={homepageSections}
          wishlist={wishlist}
          onNavigate={url => window.location.assign(url)}
          onAddToCart={onAddToCart}
          onToggleWishlist={onToggleWishlist}
          onProductClick={onProductClick}
        />
      ) : <>
      {/* ── CATEGORIES ── */}
      <section className="py-16 sm:py-20 storefront-shell">
        <div className="text-center mb-12">
          <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-3">Browse by Collection</p>
          <h2 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>Shop by Category</h2>
          <div className="flex justify-center mt-4">
            <ThreadCurve width={200} color="#C4622D" opacity={0.4} />
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => window.location.assign(`/shop?category=${encodeURIComponent(cat.slug)}`)}
              className="group relative rounded-2xl overflow-hidden text-left"
              style={{ aspectRatio: '3/4', background: '#EDE4D0' }}
            >
              {cat.imageUrl && <img src={cat.imageUrl} alt={cat.name} className="absolute inset-0 w-full h-full object-cover opacity-85 group-hover:opacity-70 group-hover:scale-105 transition-all duration-500" loading="lazy" decoding="async" />}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-4">
                <h3 className="text-white font-semibold text-sm leading-tight" style={{ fontFamily: 'var(--font-serif)' }}>{cat.name}</h3>
                <p className="text-white/70 text-xs mt-1 hidden group-hover:block transition-all">{cat.description}</p>
                <div className="mt-2 flex items-center gap-1 text-white/80 text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                  Shop now <ArrowRightIcon size={12} />
                </div>
              </div>
            </button>
          ))}
        </div>
      </section>

      {/* ── ROMANTIC COLLECTION ── */}
      <section className="py-16 sm:py-20 bg-white">
        <div className="storefront-shell">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
            <div>
              <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-3">For Someone Special</p>
              <h2 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>
                Made for Someone Special ❤️
              </h2>
              <p className="text-[#8B6B4A] mt-3 max-w-md">
                Because some feelings are too big for ordinary gifts — let handmade speak what words cannot.
              </p>
            </div>
            <button onClick={() => onNavigate('shop')} className="flex items-center gap-2 text-[#C4622D] font-semibold hover:gap-3 transition-all shrink-0">
              View all <ArrowRightIcon size={18} />
            </button>
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 lg:gap-6 xl:grid-cols-5">
            {uniqueProducts(romantic.slice(0, 4).concat(products.filter(p => p.category === 'Gifts').slice(0, 2))).slice(0, 6).map(product => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={onAddToCart}
                onToggleWishlist={onToggleWishlist}
                isWishlisted={wishlist.includes(product.id)}
                onProductClick={onProductClick}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ── BESTSELLERS (horizontal scroll) ── */}
      <section className="py-16 sm:py-20">
        <div className="storefront-shell">
          <div className="flex items-end justify-between mb-10">
            <div>
              <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-3">Community Favourites</p>
              <h2 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>Bestsellers</h2>
            </div>
            <div className="flex gap-2">
              <button onClick={() => scroll('l')} className="w-10 h-10 rounded-full border border-[#EDE4D0] flex items-center justify-center hover:bg-[#F5EDE0] text-[#5C3D2E] transition-colors">
                <ChevronLeftIcon size={18} />
              </button>
              <button onClick={() => scroll('r')} className="w-10 h-10 rounded-full border border-[#EDE4D0] flex items-center justify-center hover:bg-[#F5EDE0] text-[#5C3D2E] transition-colors">
                <ChevronRightIcon size={18} />
              </button>
            </div>
          </div>
          <div ref={scrollRef} className="flex gap-4 overflow-x-auto scrollbar-hide pb-4" style={{ scrollSnapType: 'x mandatory' }}>
            {bestsellers.map(product => (
              <div key={product.id} className="shrink-0 w-64" style={{ scrollSnapAlign: 'start' }}>
                <ProductCard
                  product={product}
                  onAddToCart={onAddToCart}
                  onToggleWishlist={onToggleWishlist}
                  isWishlisted={wishlist.includes(product.id)}
                  onProductClick={onProductClick}
                />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── POOJA COLLECTION ── */}
      <section className="py-16 sm:py-20 relative overflow-hidden" style={{ background: 'linear-gradient(135deg, #FAF7F2 0%, #F5E8D5 100%)' }}>
        {/* Decorative top border */}
        <div className="absolute top-0 left-0 right-0 h-1" style={{ background: 'linear-gradient(90deg, #C4622D, #EDE4D0, #C4622D)' }} />
        <div className="storefront-shell">
          <div className="text-center mb-12">
            <p className="text-xs text-[#8B6B4A] font-semibold tracking-widest uppercase mb-3">Crafted for Devotion</p>
            <h2 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>
              Handcrafted for Your Sacred Spaces
            </h2>
            <p className="text-[#8B6B4A] mt-3 max-w-xl mx-auto">
              Adorn your pooja room and festive spaces with crochet flowers and garlands that carry both artistry and reverence.
            </p>
            <div className="flex justify-center mt-4">
              <ThreadCurve width={200} color="#C4622D" opacity={0.4} />
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {uniqueProducts(pooja.concat(products.filter(p => p.tags?.includes('festive')))).slice(0, 4).map(product => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={onAddToCart}
                onToggleWishlist={onToggleWishlist}
                isWishlisted={wishlist.includes(product.id)}
                onProductClick={onProductClick}
              />
            ))}
          </div>
          <div className="text-center mt-10">
            <button onClick={() => onNavigate('shop')} className="px-8 py-3.5 border-2 border-[#C4622D] text-[#C4622D] rounded-full font-semibold hover:bg-[#C4622D] hover:text-white transition-all">
              View Full Pooja Collection
            </button>
          </div>
        </div>
      </section>

      {/* ── CUSTOM ORDERS ── */}
      <section className="py-16 sm:py-20 bg-[#2C1810] relative overflow-hidden">
        {/* Decorative */}
        <div className="absolute top-0 right-0 opacity-10">
          <FlowerDecor size={300} color="#F2C4CE" />
        </div>
        <div className="absolute bottom-0 left-0 opacity-10">
          <FlowerDecor size={200} color="#EDE4D0" />
        </div>
        <div className="storefront-shell text-center relative">
          <p className="text-[#F2C4CE] text-xs tracking-widest uppercase font-semibold mb-4">Bespoke Creations</p>
          <h2 className="text-4xl lg:text-5xl font-medium text-white mb-6" style={{ fontFamily: 'var(--font-serif)' }}>
            Have Something Special in Mind?
          </h2>
          <p className="text-white/60 text-lg max-w-2xl mx-auto mb-14">
            Send us an idea, photo or inspiration and we'll turn it into something handmade just for you.
          </p>
          {/* Steps */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-14">
            {[
              { n: '01', icon: '💡', title: 'Share Your Idea', desc: 'Send us a photo, sketch or description of what you have in mind' },
              { n: '02', icon: '🪡', title: 'We Design It', desc: 'Our artisans craft a one-of-a-kind piece just for you, colour by colour' },
              { n: '03', icon: '📦', title: 'Handmade & Delivered', desc: 'Beautifully packaged and delivered to your doorstep with love' },
            ].map(({ n, icon, title, desc }) => (
              <div key={n} className="text-left bg-white/5 rounded-2xl p-6 border border-white/10 hover:border-[#F2C4CE]/30 transition-colors">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-3xl">{icon}</span>
                  <span className="text-[#F2C4CE]/40 text-sm font-bold">{n}</span>
                </div>
                <h3 className="text-white font-semibold text-lg mb-2" style={{ fontFamily: 'var(--font-serif)' }}>{title}</h3>
                <p className="text-white/50 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
          <button className="px-10 py-4 bg-[#C4622D] text-white rounded-full font-bold text-lg hover:bg-[#D4795A] transition-all hover:shadow-xl hover:-translate-y-1 inline-flex items-center gap-3">
            Request a Custom Order <ArrowRightIcon size={20} />
          </button>
          <p className="text-white/30 text-sm mt-5">Usually responds within 24 hours · WhatsApp & Email</p>
        </div>
      </section>

      {/* ── AMIGURUMI ── */}
      <section className="py-16 sm:py-20 bg-white">
        <div className="storefront-shell">
          <div className="text-center mb-12">
            <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-3">Handmade Companions</p>
            <h2 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>
              Tiny Friends, Big Smiles 🐾
            </h2>
            <p className="text-[#8B6B4A] mt-3">Each little creature is stitched with personality and charm</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {uniqueProducts(amigurumi.concat(products.filter(p => p.category === 'Amigurumi'))).slice(0, 4).map(product => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={onAddToCart}
                onToggleWishlist={onToggleWishlist}
                isWishlisted={wishlist.includes(product.id)}
                onProductClick={onProductClick}
              />
            ))}
          </div>
        </div>
      </section>

      {/* ── OCCASIONS ── */}
      <section className="py-16 sm:py-20" style={{ background: '#FAF7F2' }}>
        <div className="storefront-shell">
          <div className="text-center mb-12">
            <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-3">Every Moment Counts</p>
            <h2 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>Gift by Occasion</h2>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
            {collections.map(collection => (
              <button
                key={collection.id}
                onClick={() => window.location.assign(`/shop?collection=${encodeURIComponent(collection.slug)}`)}
                className="group relative rounded-2xl overflow-hidden text-center"
                style={{ aspectRatio: '4/3' }}
              >
                {collection.imageUrl && <img src={collection.imageUrl} alt={collection.name} className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" loading="lazy" decoding="async" />}
                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-3">
                  <p className="text-white font-semibold text-xs" style={{ fontFamily: 'var(--font-serif)' }}>{collection.name}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ── PROCESS / CRAFTSMANSHIP ── */}
      <section className="py-16 sm:py-20 bg-[#2C1810] text-white relative overflow-hidden">
        <div className="absolute inset-0 opacity-5">
          <svg width="100%" height="100%">
            <defs>
              <pattern id="stitch" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M20 0 L20 40 M0 20 L40 20" stroke="white" strokeWidth="0.5" fill="none" />
                <circle cx="20" cy="20" r="2" fill="white" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#stitch)" />
          </svg>
        </div>
        <div className="storefront-shell relative">
          <div className="text-center mb-16">
            <p className="text-[#F2C4CE] text-xs tracking-widest uppercase font-semibold mb-4">Our Process</p>
            <h2 className="text-4xl lg:text-5xl font-medium" style={{ fontFamily: 'var(--font-serif)' }}>
              Not Manufactured.<br /><em>Made by Hand.</em>
            </h2>
            <p className="text-white/50 mt-4 max-w-xl mx-auto">
              Every piece in our collection goes through six stages of loving care before it reaches you.
            </p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {processSteps.map(({ icon, step, desc }, i) => (
              <div key={step} className="text-center">
                <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center text-2xl mx-auto mb-3 border border-white/10">
                  {icon}
                </div>
                {i < processSteps.length - 1 && (
                  <div className="hidden lg:block absolute" style={{ top: '50%', left: '100%' }}>→</div>
                )}
                <p className="font-semibold text-sm" style={{ fontFamily: 'var(--font-serif)' }}>{step}</p>
                <p className="text-white/40 text-xs mt-1 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── REVIEWS ── */}
      <section className="py-16 sm:py-20 bg-white">
        <div className="storefront-shell">
          <div className="text-center mb-12">
            <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-3">From Our Community</p>
            <h2 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>
              Made with Love. Loved by You.
            </h2>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {reviews.map(review => (
              <div key={review.id} className="bg-[#FAF7F2] rounded-2xl p-6 border border-[#EDE4D0]">
                <div className="flex mb-3">
                  {[1,2,3,4,5].map(i => (
                    <StarIcon key={i} size={14} filled={i <= review.rating} className="text-[#C4622D]" />
                  ))}
                </div>
                <p className="text-[#5C3D2E] text-sm leading-relaxed italic mb-4">"{review.text}"</p>
                <div className="flex items-center gap-3 pt-4 border-t border-[#EDE4D0]">
                  <img src={review.image} alt={review.name} className="w-10 h-10 rounded-full object-cover" />
                  <div>
                    <p className="font-semibold text-[#2C1810] text-sm">{review.name}</p>
                    <p className="text-xs text-[#8B6B4A]">{review.location} · {review.product}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── INSTAGRAM / SOCIAL ── */}
      <section className="py-16 sm:py-20" style={{ background: '#FAF7F2' }}>
        <div className="storefront-shell">
          <div className="text-center mb-10">
            <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-3">@crochetbloom</p>
            <h2 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>Stitched Stories</h2>
            <p className="text-[#8B6B4A] mt-3">Follow our journey — behind the scenes, in bloom</p>
          </div>
          <div className="grid grid-cols-3 lg:grid-cols-9 gap-2">
            {instagramImages.map((id, i) => (
              <div key={i} className={`relative group overflow-hidden rounded-xl ${i === 4 ? 'col-span-1 lg:col-span-3 lg:row-span-1' : ''}`} style={{ aspectRatio: '1/1' }}>
                <img
                  src={`https://images.unsplash.com/${id}?w=300&h=300&fit=crop&auto=format`}
                  alt="Instagram"
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-[#C4622D]/0 group-hover:bg-[#C4622D]/30 transition-colors duration-300 flex items-center justify-center">
                  <span className="text-white text-2xl opacity-0 group-hover:opacity-100 transition-opacity">♥</span>
                </div>
              </div>
            ))}
          </div>
          <div className="text-center mt-8">
            <button className="px-8 py-3 border-2 border-[#2C1810] text-[#2C1810] rounded-full font-semibold hover:bg-[#2C1810] hover:text-white transition-all text-sm">
              Follow @crochetbloom on Instagram
            </button>
          </div>
        </div>
      </section>

      {/* ── PERSONALIZATION ── */}
      <section className="py-16 sm:py-20 bg-white">
        <div className="storefront-shell">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-4">Make It Yours</p>
              <h2 className="text-4xl font-medium text-[#2C1810] mb-6" style={{ fontFamily: 'var(--font-serif)' }}>
                Personalize Your<br />Crochet Gift
              </h2>
              <p className="text-[#8B6B4A] mb-8 leading-relaxed">
                Make every piece uniquely theirs. Choose colors, add names, pick flower combinations — because the most meaningful gifts carry a little piece of you.
              </p>
              <div className="grid grid-cols-2 gap-3 mb-8">
                {[
                  { icon: '🎨', label: 'Select Color', desc: '50+ yarn colors available' },
                  { icon: '✍️', label: 'Add Name', desc: 'Embroidered or attached tag' },
                  { icon: '🌸', label: 'Choose Flowers', desc: 'Mix and match varieties' },
                  { icon: '💝', label: 'Gift Wrapping', desc: 'Premium branded packaging' },
                  { icon: '💌', label: 'Custom Message', desc: 'Handwritten message card' },
                  { icon: '🪡', label: 'Add Initials', desc: 'Monogram crochet detail' },
                ].map(({ icon, label, desc }) => (
                  <div key={label} className="flex gap-3 p-3 rounded-xl bg-[#FAF7F2] border border-[#EDE4D0]">
                    <span className="text-xl shrink-0">{icon}</span>
                    <div>
                      <p className="font-semibold text-[#2C1810] text-sm">{label}</p>
                      <p className="text-xs text-[#8B6B4A]">{desc}</p>
                    </div>
                  </div>
                ))}
              </div>
              <button onClick={() => onNavigate('product')} className="px-8 py-3.5 bg-[#C4622D] text-white rounded-full font-semibold hover:bg-[#D4795A] transition-all">
                Start Customizing
              </button>
            </div>
            <div className="relative">
              <div className="rounded-3xl overflow-hidden" style={{ aspectRatio: '4/5' }}>
                <img
                  src="https://images.unsplash.com/photo-1700171394718-2457b1190444?w=700&h=875&fit=crop&auto=format"
                  alt="Customizable crochet"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="absolute -bottom-4 -left-4 bg-white rounded-2xl p-5 shadow-xl border border-[#EDE4D0]">
                <p className="text-xs text-[#8B6B4A] mb-2">Color Palette</p>
                <div className="flex gap-2">
                  {['#F2C4CE','#C4622D','#8FAF8C','#C5B9D6','#EDE4D0','#2C1810'].map(color => (
                    <div key={color} className="w-7 h-7 rounded-full border-2 border-white shadow-sm cursor-pointer hover:scale-110 transition-transform" style={{ background: color }} />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      </>}
    </div>
  );
}

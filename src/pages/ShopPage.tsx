import { useState } from 'react';
import ProductCard from '../components/ProductCard';
import { FilterIcon, XIcon, ChevronDownIcon } from '../components/Icons';
import type { Product } from '../data/products';
import { useCatalogue } from '../components/CatalogueProvider';

interface ShopPageProps {
  onAddToCart: (product: Product) => void;
  onToggleWishlist: (product: Product) => void;
  wishlist: number[];
  onProductClick: (product: Product) => void;
}

const categoryFilters = ['Flowers', 'Gifts', 'Home Décor', 'Amigurumi', 'Pooja', 'Baby', 'Keychains'];
const priceRanges = [
  { label: 'Under ₹299', min: 0, max: 299 },
  { label: '₹300 – ₹599', min: 300, max: 599 },
  { label: '₹600 – ₹999', min: 600, max: 999 },
  { label: 'Above ₹999', min: 1000, max: Infinity },
];
const occasions = ['Romantic', 'Birthday', 'Wedding', 'Pooja', 'Baby Shower', 'Housewarming'];
const sortOptions = ['Featured', 'Newest', 'Price: Low to High', 'Price: High to Low', 'Best Selling'];

function FilterSection({ title, children, defaultOpen = true }: { title: string; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border-b border-[#EDE4D0] pb-5 mb-5">
      <button
        className="flex items-center justify-between w-full mb-3 group"
        onClick={() => setOpen(!open)}
      >
        <span className="font-semibold text-[#2C1810] text-sm">{title}</span>
        <ChevronDownIcon size={16} className={`text-[#8B6B4A] transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && <div>{children}</div>}
    </div>
  );
}

export default function ShopPage({ onAddToCart, onToggleWishlist, wishlist, onProductClick }: ShopPageProps) {
  const { products } = useCatalogue();
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedPriceRange, setSelectedPriceRange] = useState<number | null>(null);
  const [selectedOccasions, setSelectedOccasions] = useState<string[]>([]);
  const [customizableOnly, setCustomizableOnly] = useState(false);
  const [sortBy, setSortBy] = useState('Featured');
  const [filterOpen, setFilterOpen] = useState(false);
  const [view, setView] = useState<'grid' | 'list'>('grid');

  const toggleCategory = (cat: string) =>
    setSelectedCategories(prev => prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]);

  const filtered = products.filter(p => {
    if (selectedCategories.length > 0 && !selectedCategories.some(c =>
      p.category.toLowerCase().includes(c.toLowerCase()) ||
      (c === 'Gifts' && p.tags?.includes('romantic'))
    )) return false;
    if (selectedPriceRange !== null) {
      const r = priceRanges[selectedPriceRange];
      if (p.price < r.min || p.price > r.max) return false;
    }
    if (customizableOnly && !p.customizable) return false;
    return true;
  }).sort((a, b) => {
    if (sortBy === 'Price: Low to High') return a.price - b.price;
    if (sortBy === 'Price: High to Low') return b.price - a.price;
    if (sortBy === 'Best Selling') return b.reviews - a.reviews;
    return 0;
  });

  const clearAll = () => {
    setSelectedCategories([]);
    setSelectedPriceRange(null);
    setSelectedOccasions([]);
    setCustomizableOnly(false);
  };

  const activeFilters = selectedCategories.length + (selectedPriceRange !== null ? 1 : 0) + selectedOccasions.length + (customizableOnly ? 1 : 0);

  const FilterPanel = () => (
    <div className="space-y-0">
      <FilterSection title="Category">
        <div className="space-y-2">
          {categoryFilters.map(cat => (
            <label key={cat} className="flex items-center gap-3 cursor-pointer group">
              <div
                onClick={() => toggleCategory(cat)}
                className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors cursor-pointer shrink-0 ${selectedCategories.includes(cat) ? 'bg-[#C4622D] border-[#C4622D]' : 'border-[#D4C5B5] group-hover:border-[#C4622D]'}`}
              >
                {selectedCategories.includes(cat) && (
                  <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                    <path d="M1 4L3.5 6.5L9 1" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </div>
              <span className="text-sm text-[#5C3D2E] group-hover:text-[#2C1810] transition-colors">{cat}</span>
            </label>
          ))}
        </div>
      </FilterSection>

      <FilterSection title="Price">
        <div className="space-y-2">
          {priceRanges.map((range, i) => (
            <label key={range.label} className="flex items-center gap-3 cursor-pointer group">
              <div
                onClick={() => setSelectedPriceRange(selectedPriceRange === i ? null : i)}
                className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors cursor-pointer shrink-0 ${selectedPriceRange === i ? 'bg-[#C4622D] border-[#C4622D]' : 'border-[#D4C5B5] group-hover:border-[#C4622D]'}`}
              >
                {selectedPriceRange === i && <div className="w-2 h-2 rounded-full bg-white" />}
              </div>
              <span className="text-sm text-[#5C3D2E]">{range.label}</span>
            </label>
          ))}
        </div>
      </FilterSection>

      <FilterSection title="Occasion" defaultOpen={false}>
        <div className="flex flex-wrap gap-2">
          {occasions.map(occ => (
            <button
              key={occ}
              onClick={() => setSelectedOccasions(prev => prev.includes(occ) ? prev.filter(o => o !== occ) : [...prev, occ])}
              className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${selectedOccasions.includes(occ) ? 'bg-[#C4622D] text-white border-[#C4622D]' : 'border-[#EDE4D0] text-[#5C3D2E] hover:border-[#C4622D]'}`}
            >
              {occ}
            </button>
          ))}
        </div>
      </FilterSection>

      <FilterSection title="Availability" defaultOpen={false}>
        <label className="flex items-center gap-3 cursor-pointer">
          <div
            onClick={() => setCustomizableOnly(!customizableOnly)}
            className={`relative w-10 h-6 rounded-full transition-colors cursor-pointer ${customizableOnly ? 'bg-[#C4622D]' : 'bg-[#D4C5B5]'}`}
          >
            <div className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${customizableOnly ? 'translate-x-5' : 'translate-x-1'}`} />
          </div>
          <span className="text-sm text-[#5C3D2E]">Customizable only</span>
        </label>
      </FilterSection>

      {activeFilters > 0 && (
        <button onClick={clearAll} className="text-sm text-[#C4622D] font-medium hover:underline mt-2">
          Clear all filters ({activeFilters})
        </button>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-[#FAF7F2] pt-28">
      {/* Page header */}
      <div className="bg-white border-b border-[#EDE4D0] px-4 py-10">
        <div className="max-w-7xl mx-auto">
          <p className="text-xs text-[#8B6B4A] mb-2">
            <button className="hover:text-[#C4622D]">Home</button> / <span>Shop</span>
          </p>
          <h1 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>
            All Products
          </h1>
          <p className="text-[#8B6B4A] mt-2">{filtered.length} handmade creations</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Top bar */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          {/* Mobile filter button */}
          <button
            onClick={() => setFilterOpen(true)}
            className="lg:hidden flex items-center gap-2 px-4 py-2.5 border border-[#EDE4D0] rounded-full text-sm font-medium text-[#5C3D2E] hover:border-[#C4622D] transition-colors"
          >
            <FilterIcon size={16} />
            Filters {activeFilters > 0 && <span className="bg-[#C4622D] text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">{activeFilters}</span>}
          </button>

          {/* Active filter chips */}
          <div className="flex flex-wrap gap-2 flex-1">
            {selectedCategories.map(cat => (
              <span key={cat} className="flex items-center gap-1.5 px-3 py-1 bg-[#F2C4CE] text-[#C4622D] rounded-full text-xs font-medium">
                {cat}
                <button onClick={() => toggleCategory(cat)}><XIcon size={12} /></button>
              </span>
            ))}
          </div>

          {/* Sort */}
          <div className="flex items-center gap-3">
            <span className="text-sm text-[#8B6B4A] hidden md:block">Sort by:</span>
            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value)}
              className="px-4 py-2 border border-[#EDE4D0] rounded-full text-sm text-[#5C3D2E] bg-white focus:outline-none focus:border-[#C4622D] cursor-pointer"
            >
              {sortOptions.map(opt => <option key={opt}>{opt}</option>)}
            </select>
          </div>
        </div>

        <div className="flex gap-8">
          {/* Desktop sidebar */}
          <aside className="hidden lg:block w-60 shrink-0">
            <div className="sticky top-28">
              <h3 className="font-semibold text-[#2C1810] mb-5">Filters</h3>
              <FilterPanel />
            </div>
          </aside>

          {/* Product grid */}
          <div className="flex-1">
            {filtered.length === 0 ? (
              <div className="text-center py-20">
                <p className="text-5xl mb-4">🧶</p>
                <p className="text-[#8B6B4A] text-lg font-medium">No products match your filters</p>
                <button onClick={clearAll} className="mt-4 px-6 py-2.5 bg-[#C4622D] text-white rounded-full text-sm font-semibold">
                  Clear Filters
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-5">
                {filtered.map(product => (
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
            )}
          </div>
        </div>
      </div>

      {/* Mobile filter drawer */}
      {filterOpen && (
        <>
          <div className="fixed inset-0 bg-black/40 z-60" style={{ zIndex: 60 }} onClick={() => setFilterOpen(false)} />
          <div className="fixed left-0 top-0 bottom-0 w-80 bg-white z-70 flex flex-col" style={{ zIndex: 70 }}>
            <div className="flex items-center justify-between px-5 py-4 border-b border-[#EDE4D0]">
              <h3 className="font-semibold text-[#2C1810]">Filters</h3>
              <button onClick={() => setFilterOpen(false)} className="p-1"><XIcon size={22} className="text-[#5C3D2E]" /></button>
            </div>
            <div className="flex-1 overflow-y-auto px-5 py-4">
              <FilterPanel />
            </div>
            <div className="px-5 py-4 border-t border-[#EDE4D0]">
              <button
                onClick={() => setFilterOpen(false)}
                className="w-full py-3 bg-[#C4622D] text-white rounded-full font-semibold"
              >
                Show {filtered.length} results
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

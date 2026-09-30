import { useState } from 'react';
import { SearchIcon, XIcon } from './Icons';
import type { Product } from '../data/products';
import { useCatalogue } from './CatalogueProvider';

interface SearchOverlayProps {
  open: boolean;
  onClose: () => void;
  onProductClick: (product: Product) => void;
}

const trending = ['Crochet flowers', 'Anniversary gifts', 'Pooja garland', 'Teddy bear', 'Custom bouquet'];

export default function SearchOverlay({ open, onClose, onProductClick }: SearchOverlayProps) {
  const { products } = useCatalogue();
  const [query, setQuery] = useState('');

  const results = query.length > 1
    ? products.filter(p =>
        p.name.toLowerCase().includes(query.toLowerCase()) ||
        p.category.toLowerCase().includes(query.toLowerCase()) ||
        p.tags?.some(t => t.includes(query.toLowerCase()))
      ).slice(0, 6)
    : [];

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-80 flex flex-col" style={{ zIndex: 80 }} role="dialog" aria-modal="true" aria-label="Search products">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white w-full max-w-2xl mx-auto mt-20 rounded-2xl shadow-2xl overflow-hidden">
        {/* Input */}
        <div className="flex items-center px-6 py-4 border-b border-[#EDE4D0] gap-3">
          <SearchIcon size={22} className="text-[#8B6B4A] shrink-0" />
          <input
            autoFocus
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search flowers, gifts, décor..."
            className="flex-1 text-lg text-[#2C1810] placeholder-[#C5B9D6] focus:outline-none bg-transparent"
            style={{ fontFamily: 'var(--font-sans)' }}
          />
          <button onClick={onClose} className="p-1 text-[#8B6B4A] hover:text-[#C4622D] transition-colors">
            <XIcon size={22} />
          </button>
        </div>

        <div className="px-6 py-5 max-h-96 overflow-y-auto">
          {results.length > 0 ? (
            <div>
              <p className="text-xs text-[#8B6B4A] uppercase tracking-widest font-semibold mb-3">Results</p>
              <div className="space-y-2">
                {results.map(product => (
                  <button
                    key={product.id}
                    onClick={() => { onProductClick(product); onClose(); setQuery(''); }}
                    className="w-full flex items-center gap-4 p-3 rounded-xl hover:bg-[#F5EDE0] transition-colors text-left"
                  >
                    <img src={product.image} alt={product.name} className="w-14 h-14 rounded-lg object-cover bg-[#F5EDE0] shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-[#2C1810] text-sm" style={{ fontFamily: 'var(--font-serif)' }}>{product.name}</p>
                      <p className="text-xs text-[#8B6B4A]">{product.category}</p>
                    </div>
                    <span className="font-bold text-[#2C1810] text-sm shrink-0">₹{product.price}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : query.length === 0 ? (
            <div>
              <p className="text-xs text-[#8B6B4A] uppercase tracking-widest font-semibold mb-3">Trending Searches</p>
              <div className="flex flex-wrap gap-2">
                {trending.map(term => (
                  <button
                    key={term}
                    onClick={() => setQuery(term)}
                    className="px-4 py-2 rounded-full bg-[#F5EDE0] text-[#5C3D2E] text-sm hover:bg-[#F2C4CE] transition-colors"
                  >
                    {term}
                  </button>
                ))}
              </div>
              <div className="mt-6">
                <p className="text-xs text-[#8B6B4A] uppercase tracking-widest font-semibold mb-3">Popular Collections</p>
                <div className="grid grid-cols-3 gap-2">
                  {['Romantic Gifts', 'Pooja', 'Amigurumi'].map((cat, i) => {
                    const imgs = [
                      'photo-1700171518313-5dd219beaaa6',
                      'photo-1700170447159-9d2d0da133a5',
                      'photo-1753370241607-5d48d8aaa70e',
                    ];
                    return (
                      <button key={cat} onClick={() => { setQuery(cat); }} className="rounded-xl overflow-hidden relative group h-24">
                        <img src={`https://images.unsplash.com/${imgs[i]}?w=200&h=100&fit=crop&auto=format`} alt={cat} className="w-full h-full object-cover" />
                        <div className="absolute inset-0 bg-black/30 flex items-end p-2">
                          <span className="text-white text-xs font-semibold">{cat}</span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-[#8B6B4A]">No results for "{query}"</p>
              <p className="text-sm text-[#8B6B4A] mt-1">Try a different search term</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

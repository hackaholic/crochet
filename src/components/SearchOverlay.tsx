import { useEffect, useRef, useState, type KeyboardEvent } from 'react';
import { SearchIcon, XIcon } from './Icons';
import type { Product } from '../data/products';
import { getSearchSuggestions, recordSearchQuery, searchProducts, type SearchSuggestions } from '../lib/api/catalogue';

interface SearchOverlayProps {
  open: boolean;
  onClose: () => void;
  onProductClick: (product: Product) => void;
}

const MIN_QUERY_LENGTH = 2;
const SEARCH_DEBOUNCE_MS = 275;
const SEARCH_RESULT_LIMIT = 6;

export default function SearchOverlay({ open, onClose, onProductClick }: SearchOverlayProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [retry, setRetry] = useState(0);
  const [suggestions, setSuggestions] = useState<SearchSuggestions>({ trending_keywords: [], trending_products: [] });
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [suggestionsError, setSuggestionsError] = useState(false);
  const [suggestionsRetry, setSuggestionsRetry] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const dialogRef = useRef<HTMLDivElement>(null);
  const normalizedQuery = query.trim();

  useEffect(() => {
    if (!open || normalizedQuery.length > 0) {
      setSuggestionsLoading(false);
      return;
    }

    const controller = new AbortController();
    setSuggestionsLoading(true);
    setSuggestionsError(false);
    getSearchSuggestions(controller.signal)
      .then(data => {
        if (!controller.signal.aborted) setSuggestions(data);
      })
      .catch(() => {
        if (!controller.signal.aborted) setSuggestionsError(true);
      })
      .finally(() => {
        if (!controller.signal.aborted) setSuggestionsLoading(false);
      });

    return () => controller.abort();
  }, [open, normalizedQuery, suggestionsRetry]);

  useEffect(() => {
    if (!open || normalizedQuery.length < MIN_QUERY_LENGTH) {
      setResults([]);
      setLoading(false);
      setError(false);
      setActiveIndex(-1);
      return;
    }

    const controller = new AbortController();
    setLoading(true);
    setError(false);
    setResults([]);
    setActiveIndex(-1);

    const timer = window.setTimeout(() => {
      searchProducts(normalizedQuery, { limit: SEARCH_RESULT_LIMIT, signal: controller.signal })
        .then(products => {
          if (!controller.signal.aborted) {
            setResults(products);
            setActiveIndex(products.length > 0 ? 0 : -1);
            void recordSearchQuery(normalizedQuery).catch(() => undefined);
          }
        })
        .catch(() => {
          if (!controller.signal.aborted) setError(true);
        })
        .finally(() => {
          if (!controller.signal.aborted) setLoading(false);
        });
    }, SEARCH_DEBOUNCE_MS);

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [normalizedQuery, open, retry]);

  useEffect(() => {
    if (!open) return;
    const previouslyFocused = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    inputRef.current?.focus();
    return () => previouslyFocused?.focus();
  }, [open]);

  const close = () => {
    setQuery('');
    setResults([]);
    setError(false);
    setLoading(false);
    setActiveIndex(-1);
    onClose();
  };

  const selectProduct = (product: Product) => {
    onProductClick(product);
    close();
  };

  const handleInputKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'ArrowDown' && results.length > 0) {
      event.preventDefault();
      setActiveIndex(index => (index + 1) % results.length);
    } else if (event.key === 'ArrowUp' && results.length > 0) {
      event.preventDefault();
      setActiveIndex(index => (index <= 0 ? results.length - 1 : index - 1));
    } else if (event.key === 'Enter' && activeIndex >= 0 && results[activeIndex]) {
      event.preventDefault();
      selectProduct(results[activeIndex]);
    }
  };

  const handleDialogKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Escape') {
      close();
      return;
    }
    if (event.key !== 'Tab') return;

    const focusable = dialogRef.current?.querySelectorAll<HTMLElement>('input:not(:disabled), button:not(:disabled):not([tabindex="-1"])');
    if (!focusable?.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-80 flex flex-col"
      style={{ zIndex: 80 }}
      role="dialog"
      aria-modal="true"
      aria-label="Search products"
      onKeyDown={handleDialogKeyDown}
    >
      <button type="button" tabIndex={-1} aria-label="Close search" className="absolute inset-0 h-full w-full cursor-default bg-black/50 backdrop-blur-sm" onClick={close} />
      <div ref={dialogRef} className="relative mx-auto mt-8 w-[calc(100%-1.5rem)] max-w-2xl overflow-hidden rounded-2xl bg-white shadow-2xl sm:mt-20 sm:w-full">
        <div className="flex items-center gap-3 border-b border-[#EDE4D0] px-4 py-4 sm:px-6">
          <SearchIcon size={22} className="shrink-0 text-[#8B6B4A]" />
          <input
            ref={inputRef}
            type="search"
            value={query}
            onChange={event => setQuery(event.target.value)}
            onKeyDown={handleInputKeyDown}
            placeholder="Search flowers, gifts, décor..."
            aria-label="Search products"
            aria-autocomplete="list"
            aria-controls="product-search-results"
            aria-expanded={results.length > 0}
            aria-activedescendant={activeIndex >= 0 ? `product-search-option-${results[activeIndex]?.id}` : undefined}
            className="min-w-0 flex-1 bg-transparent text-base text-[#2C1810] placeholder-[#A89A8D] focus:outline-none sm:text-lg"
            style={{ fontFamily: 'var(--font-sans)' }}
          />
          <button type="button" onClick={close} className="shrink-0 rounded-full p-2 text-[#8B6B4A] transition-colors hover:bg-[#F5EDE0] hover:text-[#C4622D]" aria-label="Close search">
            <XIcon size={22} />
          </button>
        </div>

        <div className="max-h-[min(70vh,32rem)] overflow-y-auto px-4 py-5 sm:px-6" aria-live="polite" aria-busy={loading || suggestionsLoading}>
          {normalizedQuery.length === 0 ? (suggestionsLoading ? (
            <p role="status" className="py-8 text-center text-sm text-[#806F61]">Finding what customers are exploring…</p>
          ) : suggestionsError ? (
            <div className="py-6 text-center">
              <p role="alert" className="text-sm text-[#806F61]">Search suggestions are temporarily unavailable.</p>
              <button type="button" onClick={() => setSuggestionsRetry(value => value + 1)} className="mt-3 rounded-full px-4 py-2 text-sm font-semibold text-[#C4622D] hover:bg-[#F5EDE0]">Try again</button>
            </div>
          ) : suggestions.trending_keywords.length || suggestions.trending_products.length ? (
            <div className="space-y-6">
              {suggestions.trending_keywords.length > 0 && (
                <section aria-labelledby="trending-searches-heading">
                  <h2 id="trending-searches-heading" className="mb-3 text-xs font-semibold uppercase tracking-widest text-[#8B6B4A]">Trending searches</h2>
                  <div className="flex flex-wrap gap-2">
                    {suggestions.trending_keywords.map(({ term }) => (
                      <button key={term} type="button" onClick={() => setQuery(term)} className="rounded-full border border-[#EDE4D0] bg-[#FFFCF7] px-3 py-2 text-sm text-[#5C3D2E] transition-colors hover:border-[#C4622D] hover:bg-[#F5EDE0]">
                        {term}
                      </button>
                    ))}
                  </div>
                </section>
              )}
              {suggestions.trending_products.length > 0 && (
                <section aria-labelledby="trending-products-heading">
                  <h2 id="trending-products-heading" className="mb-3 text-xs font-semibold uppercase tracking-widest text-[#8B6B4A]">Trending products</h2>
                  <div className="space-y-1">
                    {suggestions.trending_products.map(product => (
                      <button key={product.id} type="button" onClick={() => selectProduct(product)} className="flex w-full items-center gap-3 rounded-xl p-3 text-left transition-colors hover:bg-[#F5EDE0] sm:gap-4">
                        <img src={product.image} alt="" className="h-12 w-12 shrink-0 rounded-lg bg-[#F5EDE0] object-cover sm:h-14 sm:w-14" loading="lazy" />
                        <span className="min-w-0 flex-1">
                          <span className="block truncate text-sm font-semibold text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>{product.name}</span>
                          <span className="block truncate text-xs text-[#8B6B4A]">{product.category}</span>
                        </span>
                        <span className="shrink-0 text-sm font-bold text-[#2C1810]">₹{product.price}</span>
                      </button>
                    ))}
                  </div>
                </section>
              )}
            </div>
          ) : (
            <p className="py-5 text-center text-sm text-[#806F61]">Search products by name, category, occasion, or details.</p>
          )
          ) : normalizedQuery.length < MIN_QUERY_LENGTH ? (
            <p className="py-5 text-center text-sm text-[#806F61]">Type one more character to search the catalogue.</p>
          ) : loading ? (
            <p role="status" className="py-8 text-center text-sm text-[#806F61]">Searching products…</p>
          ) : error ? (
            <div className="py-6 text-center">
              <p role="alert" className="text-sm text-[#806F61]">Search is temporarily unavailable. Please try again.</p>
              <button type="button" onClick={() => setRetry(value => value + 1)} className="mt-3 rounded-full px-4 py-2 text-sm font-semibold text-[#C4622D] hover:bg-[#F5EDE0]">Try again</button>
            </div>
          ) : results.length > 0 ? (
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-[#8B6B4A]">Products</p>
              <div id="product-search-results" role="listbox" aria-label="Product search results" className="space-y-1">
                {results.map((product, index) => (
                  <div
                    key={product.id}
                    id={`product-search-option-${product.id}`}
                    role="option"
                    aria-selected={index === activeIndex}
                    onMouseEnter={() => setActiveIndex(index)}
                    onMouseDown={event => event.preventDefault()}
                    onClick={() => selectProduct(product)}
                    className={`flex cursor-pointer items-center gap-3 rounded-xl p-3 text-left transition-colors sm:gap-4 ${index === activeIndex ? 'bg-[#F5EDE0]' : 'hover:bg-[#F5EDE0]'}`}
                  >
                    <img src={product.image} alt="" className="h-12 w-12 shrink-0 rounded-lg bg-[#F5EDE0] object-cover sm:h-14 sm:w-14" loading="lazy" />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>{product.name}</p>
                      <p className="truncate text-xs text-[#8B6B4A]">{product.category}</p>
                    </div>
                    <span className="shrink-0 text-sm font-bold text-[#2C1810]">₹{product.price}</span>
                  </div>
                ))}
              </div>
              <p className="sr-only" role="status">{results.length} search {results.length === 1 ? 'result' : 'results'} found.</p>
            </div>
          ) : (
            <div className="py-8 text-center">
              <p className="text-[#5C3D2E]">No products found for “{normalizedQuery}”.</p>
              <p className="mt-1 text-sm text-[#8B6B4A]">Try a different name, category, or occasion.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

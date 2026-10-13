import { useEffect, useRef, useState } from 'react';
import type { Product } from '../data/products';
import { recordSearchQuery, searchProducts } from '../lib/api/catalogue';

const BATCH_SIZE = 6;
const DEBOUNCE_MS = 275;

/** One cancellable request at a time; later-page failures preserve prior results. */
export function useSearchBatches(query: string, open: boolean, retry: number) {
  const [results, setResults] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [pageError, setPageError] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const session = useRef<{ query: string; offset: number; more: boolean; busy: boolean; failed: boolean; controller: AbortController } | undefined>(undefined);

  useEffect(() => {
    const current = { query, offset: 0, more: false, busy: true, failed: false, controller: new AbortController() };
    session.current = current;
    setResults([]); setError(false); setPageError(false); setHasMore(false); setLoadingMore(false);
    setLoading(open && query.length >= 2);
    if (!open || query.length < 2) return () => current.controller.abort();
    const timer = window.setTimeout(() => {
      searchProducts(query, { limit: BATCH_SIZE, offset: 0, signal: current.controller.signal })
        .then(products => {
          if (current.controller.signal.aborted) return;
          current.offset = products.length; current.more = products.length === BATCH_SIZE;
          setResults(products); setHasMore(current.more);
          void recordSearchQuery(query).catch(() => undefined);
        })
        .catch(() => { if (!current.controller.signal.aborted) setError(true); })
        .finally(() => { if (!current.controller.signal.aborted) { current.busy = false; setLoading(false); } });
    }, DEBOUNCE_MS);
    return () => { window.clearTimeout(timer); current.controller.abort(); };
  }, [query, open, retry]);

  const loadMore = (explicitRetry = false) => {
    const current = session.current;
    if (!current || current.controller.signal.aborted || current.busy || !current.more || (current.failed && !explicitRetry)) return;
    current.busy = true; current.failed = false; setPageError(false); setLoadingMore(true);
    searchProducts(current.query, { limit: BATCH_SIZE, offset: current.offset, signal: current.controller.signal })
      .then(products => {
        if (current.controller.signal.aborted) return;
        current.offset += products.length; current.more = products.length === BATCH_SIZE;
        setResults(previous => {
          const ids = new Set(previous.map(product => product.id));
          return [...previous, ...products.filter(product => {
            if (ids.has(product.id)) return false;
            ids.add(product.id);
            return true;
          })];
        });
        setHasMore(current.more);
      })
      .catch(() => { if (!current.controller.signal.aborted) { current.failed = true; setPageError(true); } })
      .finally(() => { if (!current.controller.signal.aborted) { current.busy = false; setLoadingMore(false); } });
  };
  return { results, loading, error, hasMore, loadingMore, pageError, loadMore };
}

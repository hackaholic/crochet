import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import type { Product } from '../data/products';
import { getProducts } from '../lib/api/catalogue';

interface CatalogueState {
  products: Product[];
  loading: boolean;
  error: boolean;
  retry: () => void;
}

const CatalogueContext = createContext<CatalogueState | null>(null);

export function CatalogueProvider({ children }: { children: ReactNode }) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(false);
    getProducts(controller.signal)
      .then(setProducts)
      .catch(fetchError => {
        if (fetchError.name !== 'AbortError') setError(true);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [attempt]);

  return <CatalogueContext.Provider value={{ products, loading, error, retry: () => setAttempt(value => value + 1) }}>{children}</CatalogueContext.Provider>;
}

export function useCatalogue() {
  const catalogue = useContext(CatalogueContext);
  if (!catalogue) throw new Error('useCatalogue must be used within CatalogueProvider');
  return catalogue;
}

import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { usePublicBootstrap } from '../lib/seo/bootstrap';
import type { Product } from '../data/products';
import { getCategories, getCollections, getProducts, type Category, type Collection } from '../lib/api/catalogue';

interface CatalogueState {
  products: Product[];
  categories: Category[];
  collections: Collection[];
  loading: boolean;
  error: boolean;
  retry: () => void;
}

const CatalogueContext = createContext<CatalogueState | null>(null);

export function CatalogueProvider({ children }: { children: ReactNode }) {
  const initial = usePublicBootstrap();
  const [products, setProducts] = useState<Product[]>(initial?.products ?? []);
  const [categories, setCategories] = useState<Category[]>(initial?.categories ?? []);
  const [collections, setCollections] = useState<Collection[]>(initial?.collections ?? []);
  const [loading, setLoading] = useState(!initial);
  const [error, setError] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    if (!initial) setLoading(true);
    setError(false);
    getProducts(controller.signal)
      .then(setProducts)
      .catch(fetchError => {
        if (fetchError.name !== 'AbortError') setError(true);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    getCategories(controller.signal).then(setCategories).catch(() => setCategories([]));
    getCollections(controller.signal).then(setCollections).catch(() => setCollections([]));
    return () => controller.abort();
  }, [attempt]);

  return <CatalogueContext.Provider value={{ products, categories, collections, loading, error, retry: () => setAttempt(value => value + 1) }}>{children}</CatalogueContext.Provider>;
}

export function useCatalogue() {
  const catalogue = useContext(CatalogueContext);
  if (!catalogue) throw new Error('useCatalogue must be used within CatalogueProvider');
  return catalogue;
}

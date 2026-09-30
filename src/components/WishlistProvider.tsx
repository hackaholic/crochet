import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import type { Product } from '../data/products';
import { wishlistApi } from '../lib/api/wishlist';

interface WishlistState { ids: number[]; toggle: (product: Product) => void; refresh: () => Promise<void>; }
const WishlistContext = createContext<WishlistState | null>(null);

export function WishlistProvider({ children }: { children: ReactNode }) {
  const [ids, setIds] = useState<number[]>([]);
  const refresh = useCallback(async () => { try { const response = await wishlistApi.get(); setIds(response.items.map(item => item.productId)); } catch { setIds([]); } }, []);
  useEffect(() => { void refresh(); }, [refresh]);
  const toggle = useCallback((product: Product) => { const saved = ids.includes(product.id); setIds(current => saved ? current.filter(id => id !== product.id) : [...current, product.id]); void (saved ? wishlistApi.remove(product.id) : wishlistApi.add(product.id)).catch(() => void refresh()); }, [ids, refresh]);
  return <WishlistContext.Provider value={{ ids, toggle, refresh }}>{children}</WishlistContext.Provider>;
}
export function useWishlist() { const wishlist = useContext(WishlistContext); if (!wishlist) throw new Error('useWishlist must be used within WishlistProvider'); return wishlist; }

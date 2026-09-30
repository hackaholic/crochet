import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import type { Product } from '../data/products';
import type { CartItem } from './CartDrawer';
import { cartApi, type CartPayload } from '../lib/api/cart';
import { useCatalogue } from './CatalogueProvider';

interface CartState {
  items: CartItem[];
  loading: boolean;
  add: (product: Product, quantity?: number) => Promise<void>;
  update: (lineItemId: number, quantity: number) => Promise<void>;
  remove: (lineItemId: number) => Promise<void>;
  refresh: () => Promise<void>;
}

const CartContext = createContext<CartState | null>(null);

export function CartProvider({ children }: { children: ReactNode }) {
  const { products } = useCatalogue();
  const [cart, setCart] = useState<CartPayload | null>(null);
  const [loading, setLoading] = useState(true);

  const apply = useCallback((nextCart: CartPayload) => setCart(nextCart), []);

  const refresh = useCallback(async () => {
    try { apply(await cartApi.get()); } catch { apply({ items: [], itemCount: 0, subtotal: 0, status: 'ACTIVE' }); }
  }, [apply]);

  useEffect(() => { void refresh().finally(() => setLoading(false)); }, [refresh]);

  const items = (cart?.items ?? []).map(item => {
    const catalogueProduct = products.find(product => product.id === item.productId);
    return {
      lineItemId: item.id,
      quantity: item.quantity,
      product: catalogueProduct ?? {
        id: item.productId, name: item.productName, slug: item.productSlug, price: item.unitPrice,
        originalPrice: item.compareAtPrice ?? undefined, rating: 5, reviews: 0, image: item.productImage,
        images: [item.productImage], category: '', customizable: false,
      },
    };
  });

  const add = useCallback(async (product: Product, quantity = 1) => apply(await cartApi.add(product.id, quantity)), [apply]);
  const update = useCallback(async (lineItemId: number, quantity: number) => apply(await cartApi.update(lineItemId, quantity)), [apply]);
  const remove = useCallback(async (lineItemId: number) => apply(await cartApi.remove(lineItemId)), [apply]);

  return <CartContext.Provider value={{ items, loading, add, update, remove, refresh }}>{children}</CartContext.Provider>;
}

export function useCart() {
  const cart = useContext(CartContext);
  if (!cart) throw new Error('useCart must be used within CartProvider');
  return cart;
}

import { PlusIcon, MinusIcon, TrashIcon, HeartIcon, ArrowRightIcon } from '../components/Icons';
import type { CartItem } from '../components/CartDrawer';
import type { Product } from '../data/products';
import { EmptyState } from '../components/StorefrontState';

interface CartPageProps {
  items: CartItem[];
  onUpdateQty: (id: number, qty: number) => void;
  onRemove: (id: number) => void;
  onWishlist: (product: Product) => void;
  onCheckout: () => void;
  onNavigate: (page: 'home' | 'shop' | 'product' | 'cart' | 'wishlist' | 'checkout' | 'about') => void;
}

export default function CartPage({ items, onUpdateQty, onRemove, onWishlist, onCheckout, onNavigate }: CartPageProps) {
  const subtotal = items.reduce((s, i) => s + i.product.price * i.quantity, 0);
  const shipping = subtotal >= 999 ? 0 : 79;
  const total = subtotal + shipping;

  return (
    <div className="min-h-screen bg-[#FAF7F2] pt-28">
      <div className="max-w-6xl mx-auto px-4 py-10">
        <h1 className="text-4xl font-medium text-[#2C1810] mb-2" style={{ fontFamily: 'var(--font-serif)' }}>Your Basket</h1>
        <p className="text-[#8B6B4A] mb-10">{items.length} item{items.length !== 1 ? 's' : ''}</p>

        {items.length === 0 ? (
          <EmptyState icon="🧶" title="Your basket is empty" description="Fill it with something handmade and beautiful" action={{ label: 'Browse Collection', onClick: () => onNavigate('shop') }} />
        ) : (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Items */}
            <div className="lg:col-span-2 space-y-4">
              {items.map(({ lineItemId, product, quantity }) => (
                <div key={lineItemId ?? product.id} className="bg-white rounded-2xl p-5 flex gap-5 border border-[#EDE4D0]" style={{ boxShadow: '0 2px 8px rgba(44,24,16,0.04)' }}>
                  <img
                    src={product.image}
                    alt={product.name}
                    className="w-24 h-24 object-cover rounded-xl bg-[#F5EDE0] shrink-0 cursor-pointer"
                    onClick={() => onNavigate('product')}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-xs text-[#8B6B4A] mb-0.5">{product.category}</p>
                        <h3 className="font-semibold text-[#2C1810] leading-snug cursor-pointer hover:text-[#C4622D] transition-colors" style={{ fontFamily: 'var(--font-serif)' }} onClick={() => onNavigate('product')}>
                          {product.name}
                        </h3>
                        {product.customizable && (
                          <p className="text-xs text-[#8B6B4A] mt-1">Color: Blush Pink · Gift wrapped</p>
                        )}
                      </div>
                      <div className="text-right shrink-0">
                        <p className="font-bold text-[#2C1810]">₹{product.price * quantity}</p>
                        {quantity > 1 && <p className="text-xs text-[#8B6B4A]">₹{product.price} each</p>}
                      </div>
                    </div>
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex items-center gap-2 border border-[#EDE4D0] rounded-full px-3 py-1.5">
                        <button
                          onClick={() => quantity > 1 ? onUpdateQty(lineItemId ?? product.id, quantity - 1) : onRemove(lineItemId ?? product.id)}
                          className="w-6 h-6 flex items-center justify-center text-[#5C3D2E] hover:text-[#C4622D]"
                        >
                          <MinusIcon size={14} />
                        </button>
                        <span className="w-6 text-center text-sm font-bold">{quantity}</span>
                        <button
                          onClick={() => onUpdateQty(lineItemId ?? product.id, quantity + 1)}
                          className="w-6 h-6 flex items-center justify-center text-[#5C3D2E] hover:text-[#C4622D]"
                        >
                          <PlusIcon size={14} />
                        </button>
                      </div>
                      <div className="flex items-center gap-3">
                        <button onClick={() => onWishlist(product)} className="flex items-center gap-1.5 text-xs text-[#8B6B4A] hover:text-[#C4622D] transition-colors">
                          <HeartIcon size={14} /> Save
                        </button>
                        <button onClick={() => onRemove(lineItemId ?? product.id)} className="flex items-center gap-1.5 text-xs text-[#8B6B4A] hover:text-red-500 transition-colors">
                          <TrashIcon size={14} /> Remove
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Summary */}
            <div>
              <div className="bg-white rounded-2xl p-6 border border-[#EDE4D0] sticky top-28" style={{ boxShadow: '0 2px 8px rgba(44,24,16,0.04)' }}>
                <h2 className="text-xl font-semibold text-[#2C1810] mb-5" style={{ fontFamily: 'var(--font-serif)' }}>Order Summary</h2>

                {/* Free shipping progress */}
                {subtotal < 999 && (
                  <div className="mb-5 p-3 bg-[#F5EDE0] rounded-xl">
                    <p className="text-xs text-[#8B6B4A] mb-2">
                      ₹<span className="font-bold text-[#C4622D]">{999 - subtotal}</span> more for free shipping
                    </p>
                    <div className="h-1.5 bg-[#EDE4D0] rounded-full">
                      <div className="h-full bg-[#C4622D] rounded-full" style={{ width: `${Math.min((subtotal / 999) * 100, 100)}%` }} />
                    </div>
                  </div>
                )}

                {/* Discount code */}
                <div className="flex gap-2 mb-5">
                  <input type="text" placeholder="Discount code" className="flex-1 px-3 py-2.5 border border-[#EDE4D0] rounded-xl text-sm focus:outline-none focus:border-[#C4622D] bg-[#FAF7F2]" />
                  <button className="px-4 py-2.5 border border-[#EDE4D0] rounded-xl text-sm text-[#C4622D] font-semibold hover:bg-[#C4622D] hover:text-white hover:border-[#C4622D] transition-colors">Apply</button>
                </div>

                <div className="space-y-3 mb-5 text-sm">
                  <div className="flex justify-between text-[#8B6B4A]">
                    <span>Subtotal ({items.length} items)</span>
                    <span className="text-[#2C1810] font-medium">₹{subtotal}</span>
                  </div>
                  <div className="flex justify-between text-[#8B6B4A]">
                    <span>Shipping</span>
                    <span className={`font-medium ${shipping === 0 ? 'text-[#8FAF8C]' : 'text-[#2C1810]'}`}>
                      {shipping === 0 ? 'FREE' : `₹${shipping}`}
                    </span>
                  </div>
                  <div className="flex justify-between font-bold text-[#2C1810] text-base pt-3 border-t border-[#EDE4D0]">
                    <span>Estimated Total</span>
                    <span>₹{total}</span>
                  </div>
                </div>

                <button
                  onClick={onCheckout}
                  className="w-full py-3.5 bg-[#C4622D] text-white rounded-full font-semibold hover:bg-[#D4795A] transition-colors flex items-center justify-center gap-2"
                >
                  Proceed to Checkout <ArrowRightIcon size={18} />
                </button>
                <p className="text-center text-xs text-[#8B6B4A] mt-3">Secure checkout · SSL encrypted</p>

                <div className="mt-5 pt-5 border-t border-[#EDE4D0]">
                  <p className="text-xs text-[#8B6B4A] text-center">We accept</p>
                  <div className="flex justify-center gap-2 mt-2">
                    {['UPI', 'Card', 'Net Banking', 'COD'].map(m => (
                      <span key={m} className="text-xs bg-[#F5EDE0] text-[#8B6B4A] px-2 py-1 rounded">{m}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

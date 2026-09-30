import { XIcon, PlusIcon, MinusIcon, TrashIcon, HeartIcon } from './Icons';
import type { Product } from '../data/products';

export interface CartItem {
  lineItemId?: number;
  product: Product;
  quantity: number;
}

interface CartDrawerProps {
  open: boolean;
  onClose: () => void;
  items: CartItem[];
  onUpdateQty: (id: number, qty: number) => void;
  onRemove: (id: number) => void;
  onWishlist: (product: Product) => void;
  onCheckout: () => void;
}

export default function CartDrawer({ open, onClose, items, onUpdateQty, onRemove, onWishlist, onCheckout }: CartDrawerProps) {
  const subtotal = items.reduce((sum, i) => sum + i.product.price * i.quantity, 0);
  const shipping = subtotal >= 999 ? 0 : 79;
  const total = subtotal + shipping;

  return (
    <>
      {/* Overlay */}
      <div
        className={`fixed inset-0 bg-black/40 z-60 transition-opacity duration-300 ${open ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
        onClick={onClose}
        style={{ zIndex: 60 }}
      />
      {/* Drawer */}
      <div
        className={`fixed right-0 top-0 bottom-0 w-full max-w-md bg-white z-70 flex flex-col transition-transform duration-300 ease-out ${open ? 'translate-x-0' : 'translate-x-full'}`}
        style={{ zIndex: 70 }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-[#EDE4D0]">
          <div>
            <h2 className="text-xl font-semibold text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>
              Your Basket
            </h2>
            <p className="text-xs text-[#8B6B4A] mt-0.5">{items.length} item{items.length !== 1 ? 's' : ''}</p>
          </div>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-[#F5EDE0] text-[#5C3D2E] transition-colors">
            <XIcon size={22} />
          </button>
        </div>

        {/* Free shipping bar */}
        {subtotal < 999 && (
          <div className="px-6 py-3 bg-[#F5EDE0]">
            <p className="text-xs text-[#8B6B4A] mb-1.5">
              Add <span className="font-semibold text-[#C4622D]">₹{999 - subtotal}</span> more for free shipping!
            </p>
            <div className="h-1.5 bg-[#EDE4D0] rounded-full overflow-hidden">
              <div
                className="h-full bg-[#C4622D] rounded-full transition-all duration-500"
                style={{ width: `${Math.min((subtotal / 999) * 100, 100)}%` }}
              />
            </div>
          </div>
        )}
        {subtotal >= 999 && (
          <div className="px-6 py-3 bg-[#EBF3EA] text-[#5C7A5A] text-xs font-medium text-center">
            🎉 You've unlocked free shipping!
          </div>
        )}

        {/* Items */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {items.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="text-6xl mb-4">🧶</div>
              <p className="text-[#8B6B4A] font-medium">Your basket is empty</p>
              <p className="text-[#8B6B4A] text-sm mt-1">Fill it with handmade love!</p>
              <button onClick={onClose} className="mt-6 px-6 py-2.5 bg-[#C4622D] text-white rounded-full text-sm font-semibold hover:bg-[#D4795A] transition-colors">
                Continue Shopping
              </button>
            </div>
          ) : items.map(({ lineItemId, product, quantity }) => (
            <div key={lineItemId ?? product.id} className="flex gap-4">
              <img
                src={product.image}
                alt={product.name}
                className="w-20 h-20 object-cover rounded-xl bg-[#F5EDE0] shrink-0"
              />
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-semibold text-[#2C1810] leading-snug" style={{ fontFamily: 'var(--font-serif)' }}>
                  {product.name}
                </h4>
                <p className="text-xs text-[#8B6B4A] mt-0.5">{product.category}</p>
                <div className="flex items-center justify-between mt-3">
                  {/* Qty controls */}
                  <div className="flex items-center gap-2 border border-[#EDE4D0] rounded-full px-2 py-1">
                    <button
                      onClick={() => quantity > 1 ? onUpdateQty(lineItemId ?? product.id, quantity - 1) : onRemove(lineItemId ?? product.id)}
                      className="w-6 h-6 flex items-center justify-center text-[#5C3D2E] hover:text-[#C4622D] transition-colors"
                    >
                      <MinusIcon size={14} />
                    </button>
                    <span className="text-sm font-semibold w-5 text-center">{quantity}</span>
                    <button
                      onClick={() => onUpdateQty(lineItemId ?? product.id, quantity + 1)}
                      className="w-6 h-6 flex items-center justify-center text-[#5C3D2E] hover:text-[#C4622D] transition-colors"
                    >
                      <PlusIcon size={14} />
                    </button>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-[#2C1810] text-sm">₹{product.price * quantity}</span>
                    <button onClick={() => onWishlist(product)} className="p-1 text-[#8B6B4A] hover:text-[#C4622D] transition-colors" aria-label="Move to wishlist">
                      <HeartIcon size={14} />
                    </button>
                    <button onClick={() => onRemove(lineItemId ?? product.id)} className="p-1 text-[#8B6B4A] hover:text-red-500 transition-colors" aria-label="Remove">
                      <TrashIcon size={14} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        {items.length > 0 && (
          <div className="px-6 py-5 border-t border-[#EDE4D0] bg-[#FAF7F2]">
            <div className="space-y-2 mb-4 text-sm">
              <div className="flex justify-between text-[#8B6B4A]">
                <span>Subtotal</span>
                <span className="font-medium text-[#2C1810]">₹{subtotal}</span>
              </div>
              <div className="flex justify-between text-[#8B6B4A]">
                <span>Shipping</span>
                <span className={`font-medium ${shipping === 0 ? 'text-[#8FAF8C]' : 'text-[#2C1810]'}`}>
                  {shipping === 0 ? 'FREE' : `₹${shipping}`}
                </span>
              </div>
              <div className="flex justify-between font-bold text-[#2C1810] text-base pt-2 border-t border-[#EDE4D0]">
                <span>Total</span>
                <span>₹{total}</span>
              </div>
            </div>
            {/* Discount code */}
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                placeholder="Discount code"
                className="flex-1 px-4 py-2.5 border border-[#EDE4D0] rounded-xl text-sm focus:outline-none focus:border-[#C4622D] transition-colors bg-white"
              />
              <button className="px-4 py-2.5 border border-[#C4622D] text-[#C4622D] rounded-xl text-sm font-semibold hover:bg-[#C4622D] hover:text-white transition-colors">
                Apply
              </button>
            </div>
            <button
              onClick={onCheckout}
              className="w-full py-3.5 bg-[#C4622D] text-white rounded-full font-semibold hover:bg-[#D4795A] transition-colors"
            >
              Proceed to Checkout →
            </button>
            <p className="text-center text-xs text-[#8B6B4A] mt-3">
              Secure checkout · 100% handmade guarantee
            </p>
          </div>
        )}
      </div>
    </>
  );
}

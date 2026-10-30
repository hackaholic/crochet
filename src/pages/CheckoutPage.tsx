import { useCheckoutForm } from '../hooks/useCheckoutForm';
import type { User } from '../lib/api/auth';
import './checkout.css';
import ProductRecommendations from '../components/ProductRecommendations';
import type { Product } from '../data/products';
import PersonalizationNote from '../components/PersonalizationNote';
import { guestTrackingPath } from '../lib/routes';
import { useEffect, useRef, useState } from 'react';
import { CheckIcon, ArrowRightIcon } from '../components/Icons';
import type { CartItem } from '../components/CartDrawer';
import { createOrder, type OrderOut } from '../lib/api/orders';
import { createPaymentIntent, verifyCashfreePayment, verifyMockPayment, type PaymentVerification } from '../lib/api/payments';
import { openCashfreeCheckout } from '../lib/payment/cashfreeCheckout';

interface CheckoutPageProps {
  customer?: User | null;
  items: CartItem[];
  wishlist?: number[];
  onComplete: () => void;
  onNavigate: (page: 'home' | 'shop' | 'product' | 'cart' | 'wishlist' | 'checkout' | 'about') => void;
  couponCode: string | null;
  onAddToCart: (product: Product) => Promise<void>;
  onProductClick: (product: Product) => void;
  onToggleWishlist?: (product: Product) => void;
}

type Step = 'contact' | 'delivery' | 'payment' | 'review';
type PaymentReturnState = { status: 'verifying' } | { status: 'failed'; message: string } | { status: 'success'; payment: PaymentVerification };
const steps: { id: Step; label: string }[] = [
  { id: 'contact', label: 'Contact' },
  { id: 'delivery', label: 'Delivery' },
  { id: 'payment', label: 'Payment' },
  { id: 'review', label: 'Review' },
];

const paymentMethods = [
  { id: 'upi', label: 'UPI', icon: '📱', desc: 'Google Pay, PhonePe, Paytm' },
  { id: 'card', label: 'Credit / Debit Card', icon: '💳', desc: 'Visa, Mastercard, RuPay' },
  { id: 'netbanking', label: 'Net Banking', icon: '🏦', desc: 'All major Indian banks' },
  { id: 'wallet', label: 'Wallet', icon: '👛', desc: 'Paytm, Mobikwik, Freecharge' },
  { id: 'cod', label: 'Cash on Delivery', icon: '💵', desc: 'Pay when delivered' },
];

export default function CheckoutPage({ customer, items, wishlist = [], onToggleWishlist, onComplete, onNavigate, couponCode, onAddToCart, onProductClick }: CheckoutPageProps) {
  const [addingItem, setAddingItem] = useState(false);
  const addRecommendation = async (product: Product) => {
    setAddingItem(true);
    try { await onAddToCart(product); } finally { setAddingItem(false); }
  };
  const [step, setStep] = useState<Step>('contact');
  const [selectedPayment, setSelectedPayment] = useState('upi');
  const [completedOrder, setCompletedOrder] = useState<OrderOut>();
  const [completedProductIds, setCompletedProductIds] = useState<number[]>([]);
  const [orderPlaced, setOrderPlaced] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [paymentReturn, setPaymentReturn] = useState<PaymentReturnState>();
  const [paymentReturnAttempt, setPaymentReturnAttempt] = useState(0);
  const onCompleteRef = useRef(onComplete);
  const { form, input } = useCheckoutForm(customer);

  useEffect(() => { onCompleteRef.current = onComplete; }, [onComplete]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const paymentIdValue = params.get('paymentId');
    const providerOrderId = params.get('cfOrderId');
    if (!paymentIdValue && !providerOrderId) return;

    const paymentId = Number(paymentIdValue);
    const validPaymentIdText = paymentIdValue !== null && /^[1-9]\d{0,9}$/.test(paymentIdValue);
    if (!validPaymentIdText || !Number.isSafeInteger(paymentId) || paymentId > 2_147_483_647 || !providerOrderId || providerOrderId.length > 128) {
      setPaymentReturn({ status: 'failed', message: 'We could not verify this payment return. Please check your orders or contact support.' });
      return;
    }

    let active = true;
    setPaymentReturn({ status: 'verifying' });
    verifyCashfreePayment(paymentId, providerOrderId).then(payment => {
      const verified = payment.status.toUpperCase() === 'SUCCESS'
        && payment.provider === 'cashfree'
        && payment.id === paymentId
        && payment.providerOrderId === providerOrderId;
      if (!active) return;
      if (!verified) {
        setPaymentReturn({ status: 'failed', message: 'Cashfree has not confirmed this payment yet. You can safely try verification again.' });
        return;
      }
      setPaymentReturn({ status: 'success', payment });
      setCompletedProductIds(items.map(item => item.product.id));
      onCompleteRef.current();
      window.history.replaceState(null, '', `${window.location.pathname}${window.location.hash}`);
    }).catch(() => {
      if (active) setPaymentReturn({ status: 'failed', message: 'We could not confirm this payment yet. Please retry verification.' });
    });
    return () => { active = false; };
  }, [paymentReturnAttempt]);

  const subtotal = items.reduce((s, i) => s + i.product.price * i.quantity, 0);
  const shipping = subtotal >= 999 ? 0 : 79;
  const total = subtotal + shipping;

  const stepIndex = steps.findIndex(s => s.id === step);

  const next = async () => {
    if (addingItem || submitting) return;
    const idx = stepIndex;
    if (idx < steps.length - 1) setStep(steps[idx + 1].id);
    else {
      if (!form.firstName || !form.email || !form.phone || !form.line1 || !form.city || !form.state || !form.postalCode) {
        setError('Please complete your contact and delivery details before placing the order.');
        return;
      }
      setSubmitting(true); setError('');
      try {
        const paymentMethod = selectedPayment === 'cod' ? 'COD' : selectedPayment === 'card' ? 'CARD' : selectedPayment === 'netbanking' ? 'NETBANKING' : 'UPI';
        const order = await createOrder({ paymentMethod, customerEmail: form.email, couponCode: couponCode ?? undefined, shippingAddress: { name: `${form.firstName} ${form.lastName}`.trim(), phone: form.phone, line1: form.line1, line2: form.line2 || undefined, landmark: form.landmark || undefined, city: form.city, state: form.state, postalCode: form.postalCode } });
        if (paymentMethod !== 'COD') {
          const intent = await createPaymentIntent(order.orderNumber);
          if (intent.provider === 'cashfree') {
            await openCashfreeCheckout(intent);
            return;
          }
          if (intent.provider !== 'mock') throw new Error('This payment provider is not available in this checkout.');
          await verifyMockPayment(intent, paymentMethod === 'UPI' ? 'UPI / Mock gateway' : `${paymentMethod} / Mock gateway`);
        }
        setCompletedOrder(order); setCompletedProductIds(items.map(item => item.product.id)); setOrderPlaced(true); onComplete();
      } catch (requestError) { setError(requestError instanceof Error ? requestError.message : 'We could not place your order. Please try again.'); }
      finally { setSubmitting(false); }
    }
  };



  if (paymentReturn?.status === 'verifying') {
    return <div className="min-h-screen bg-[#FAF7F2] pt-28 flex items-center justify-center px-4"><div className="checkout-panel max-w-lg text-center" role="status" aria-live="polite"><h1 className="text-2xl font-medium text-[#2C1810]" style={{fontFamily:'var(--font-serif)'}}>Checking your payment</h1><p className="mt-3 text-sm text-[#8B6B4A]">We are confirming the status securely with Cashfree.</p></div></div>;
  }

  if (orderPlaced || paymentReturn?.status === 'success') {
    return (
      <div className="checkout-page">
        <main className="checkout-container">
          <div className="w-full">
            <section className="checkout-panel mb-6 w-full text-center" aria-labelledby="checkout-success-title">
              <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-[#EBF3EA] text-3xl" aria-hidden="true">🎉</div>
              <h1 id="checkout-success-title" className="mb-2 text-3xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>
                {paymentReturn?.status === 'success' ? 'Payment Confirmed!' : 'Order Placed!'}
              </h1>
              <p className="text-sm text-[#8B6B4A]">Your order is confirmed. You can follow its progress from the order timeline.</p>
              <div className="mt-5 grid gap-5 text-left md:grid-cols-[minmax(0,1fr)_minmax(15rem,.8fr)]">
                <div className="rounded-xl border border-[#EDE4D0] bg-[#FFFCF8] p-4">
                  <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-[#8B6B4A]">Order progress</h2>
                  {['Order placed', 'Order confirmed', 'Preparation and quality check', 'Shipping updates', 'Delivered'].map((label, index) => (
                    <div key={label} className="flex items-center gap-3 py-1.5">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#EBF3EA] text-xs font-bold text-[#526A48]">{index + 1}</span>
                      <span className="text-sm text-[#5C3D2E]">{label}</span>
                    </div>
                  ))}
                </div>
                <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-[#EDE4D0] bg-white p-4 text-center">
                  {completedOrder && <>
                    <p className="text-sm font-semibold text-[#2C1810]">Order {completedOrder.orderNumber}</p>
                    {completedOrder.guestTrackingToken && <a className="underline text-[#C4622D]" href={guestTrackingPath(completedOrder.orderNumber, completedOrder.guestTrackingToken)}>Track your order</a>}
                  </>}
                  {paymentReturn?.status === 'success' && <p className="text-sm font-semibold text-[#2C1810]">{paymentReturn.payment.orderNumber ? `Order ${paymentReturn.payment.orderNumber}` : 'Your order payment has been verified.'}</p>}
                  <button onClick={() => onNavigate('home')} className="min-h-11 rounded-full bg-[#C4622D] px-7 py-3 font-semibold text-white transition-colors hover:bg-[#D4795A]">
                    Continue Shopping
                  </button>
                </div>
              </div>
            </section>
            <ProductRecommendations extended open layout="checkout" context="checkout"
              excludedIds={[...new Set([...items.map(item => item.product.id), ...completedProductIds])]}
              wishlistIds={wishlist} onToggleWishlist={onToggleWishlist}
              onAddToCart={addRecommendation} onProductClick={onProductClick} />
          </div>
        </main>
      </div>
    );
  }

  if (!items.length) return (
    <div className="checkout-page"><div className="checkout-container">
      <section className="checkout-panel text-center">
        {paymentReturn?.status === 'failed' && <div className="mb-5 text-sm text-[#9D3B28]" role="alert"><p>{paymentReturn.message}</p><button className="checkout-browse mt-3" onClick={() => setPaymentReturnAttempt(value => value + 1)}>Retry payment verification</button></div>}
        <h1 className="text-2xl font-medium" style={{fontFamily: 'var(--font-serif)'}}>Your basket is empty</h1>
        <button className="checkout-browse" onClick={() => onNavigate('shop')}>Browse the collection</button>
      </section>
    </div></div>
  );

  return (
    <div className="checkout-page">
      <div className="checkout-container">
        {paymentReturn?.status === 'failed' && <section className="checkout-panel mb-4 text-sm text-[#9D3B28]" role="alert"><p>{paymentReturn.message}</p><button className="checkout-browse mt-3" onClick={() => setPaymentReturnAttempt(value => value + 1)}>Retry payment verification</button></section>}
        <header className="checkout-heading">
          <h1 style={{ fontFamily: 'var(--font-serif)' }}>Checkout</h1>
          <button onClick={() => onNavigate('cart')} className="checkout-back">← Back to basket</button>
        </header>

        {/* Step indicators */}
        <nav aria-label="Checkout progress" className="checkout-progress">
          {steps.map(({ id, label }, i) => (
            <div key={id} aria-current={id === step ? 'step' : undefined} className="checkout-step flex items-center flex-1">
              <div className="flex items-center gap-2 shrink-0">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${i < stepIndex ? 'bg-[#8FAF8C] text-white' : i === stepIndex ? 'bg-[#C4622D] text-white' : 'bg-[#EDE4D0] text-[#8B6B4A]'}`}>
                  {i < stepIndex ? <CheckIcon size={14} /> : i + 1}
                </div>
                <span className={`checkout-step-label text-sm font-medium ${i === stepIndex ? 'text-[#C4622D]' : 'text-[#8B6B4A]'}`}>{label}</span>
              </div>
              {i < steps.length - 1 && (
                <div className={`flex-1 h-0.5 mx-3 ${i < stepIndex ? 'bg-[#8FAF8C]' : 'bg-[#EDE4D0]'}`} />
              )}
            </div>
          ))}
        </nav>

        <div className="checkout-grid">
          {/* Form */}
          <div className="min-w-0">
            <div className="checkout-panel">
              {step === 'contact' && (
                <div>
                  <h2 className="text-xl font-semibold text-[#2C1810] mb-6" style={{ fontFamily: 'var(--font-serif)' }}>Contact Information</h2>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { label: 'First Name', placeholder: 'First name', col: 1, name: 'firstName' },
                      { label: 'Last Name', placeholder: 'Last name', col: 1, name: 'lastName' },
                      { label: 'Email', placeholder: 'you@example.com', col: 2, type: 'email', name: 'email' },
                      { label: 'Phone Number', placeholder: '+91 98765 43210', col: 2, type: 'tel', name: 'phone' },
                    ].map(({ label, placeholder, col, type = 'text', name }) => (
                      <div key={label} className={col === 2 ? 'col-span-2 md:col-span-1' : ''}>
                        <label htmlFor={`checkout-${name}`} className="block text-sm font-medium text-[#2C1810] mb-1.5">{label}{['First Name', 'Email', 'Phone Number'].includes(label) ? ' *' : ''}</label>
                        <input
                          id={`checkout-${name}`}
                          type={type}
                          required={['First Name', 'Email', 'Phone Number'].includes(label)}
                          placeholder={placeholder}
                          {...input(name as keyof typeof form)}
                          className="w-full px-4 py-3 border border-[#EDE4D0] rounded-xl text-sm focus:outline-none focus:border-[#C4622D] transition-colors bg-[#FAF7F2]"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {step === 'delivery' && (
                <div>
                  <h2 className="text-xl font-semibold text-[#2C1810] mb-6" style={{ fontFamily: 'var(--font-serif)' }}>Delivery Address</h2>
                  <div className="grid md:grid-cols-2 gap-4">
                    {[
                      { label: 'Address Line 1', placeholder: 'House / Flat No., Building Name', col: 2, name: 'line1' },
                      { label: 'Address Line 2', placeholder: 'Street, Area, Locality (optional)', col: 2, name: 'line2' },
                      { label: 'City', placeholder: 'Mumbai', col: 1, name: 'city' },
                      { label: 'State', placeholder: 'Maharashtra', col: 1, name: 'state' },
                      { label: 'PIN Code', placeholder: '400001', col: 1, name: 'postalCode' },
                      { label: 'Landmark (optional)', placeholder: 'Near XYZ', col: 1, name: 'landmark' },
                    ].map(({ label, placeholder, col, name }) => (
                      <div key={label} className={col === 2 ? 'md:col-span-2' : ''}>
                        <label htmlFor={`checkout-${name}`} className="block text-sm font-medium text-[#2C1810] mb-1.5">{label}</label>
                        <input
                          id={`checkout-${name}`}
                          type="text"
                          placeholder={placeholder}
                          {...input(name as keyof typeof form)}
                          className="w-full px-4 py-3 border border-[#EDE4D0] rounded-xl text-sm focus:outline-none focus:border-[#C4622D] transition-colors bg-[#FAF7F2]"
                        />
                      </div>
                    ))}
                  </div>
                  {/* Delivery options */}
                  <div className="mt-6">
                    <h3 className="text-sm font-semibold text-[#2C1810] mb-3">Delivery Option</h3>
                    <div className="space-y-3">
                      {[
                        { id: 'standard', label: 'Standard Delivery', time: '5–7 working days', price: shipping === 0 ? 'FREE' : `₹${shipping}` },
                        { id: 'express', label: 'Express Delivery', time: '2–3 working days', price: '₹149' },
                      ].map(opt => (
                        <label key={opt.id} className="flex items-center justify-between p-4 border border-[#EDE4D0] rounded-xl cursor-pointer hover:border-[#C4622D] transition-colors">
                          <div className="flex items-center gap-3">
                            <input type="radio" name="delivery" value={opt.id} defaultChecked={opt.id === 'standard'} className="accent-[#C4622D]" />
                            <div>
                              <p className="font-medium text-sm text-[#2C1810]">{opt.label}</p>
                              <p className="text-xs text-[#8B6B4A]">{opt.time}</p>
                            </div>
                          </div>
                          <span className="font-semibold text-sm text-[#2C1810]">{opt.price}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {step === 'payment' && (
                <div>
                  <h2 className="text-xl font-semibold text-[#2C1810] mb-6" style={{ fontFamily: 'var(--font-serif)' }}>Payment Method</h2>
                  <div className="space-y-3 mb-6">
                    {paymentMethods.map(method => (
                      <label
                        key={method.id}
                        className={`flex items-center gap-4 p-4 border-2 rounded-xl cursor-pointer transition-colors ${selectedPayment === method.id ? 'border-[#C4622D] bg-[#FDF5F1]' : 'border-[#EDE4D0] hover:border-[#C4622D]/40'}`}
                        onClick={() => setSelectedPayment(method.id)}
                      >
                        <input type="radio" name="payment" value={method.id} checked={selectedPayment === method.id} onChange={() => setSelectedPayment(method.id)} className="accent-[#C4622D]" />
                        <span className="text-2xl">{method.icon}</span>
                        <div>
                          <p className="font-semibold text-sm text-[#2C1810]">{method.label}</p>
                          <p className="text-xs text-[#8B6B4A]">{method.desc}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                  {selectedPayment === 'upi' && (
                    <div>
                      <label className="block text-sm font-medium text-[#2C1810] mb-1.5">UPI ID</label>
                      <input type="text" placeholder="yourname@paytm" className="w-full px-4 py-3 border border-[#EDE4D0] rounded-xl text-sm focus:outline-none focus:border-[#C4622D] bg-[#FAF7F2]" />
                    </div>
                  )}
                  {selectedPayment === 'card' && (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-[#2C1810] mb-1.5">Card Number</label>
                        <input type="text" placeholder="1234 5678 9012 3456" className="w-full px-4 py-3 border border-[#EDE4D0] rounded-xl text-sm focus:outline-none focus:border-[#C4622D] bg-[#FAF7F2]" />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-[#2C1810] mb-1.5">Expiry</label>
                          <input type="text" placeholder="MM / YY" className="w-full px-4 py-3 border border-[#EDE4D0] rounded-xl text-sm focus:outline-none focus:border-[#C4622D] bg-[#FAF7F2]" />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-[#2C1810] mb-1.5">CVV</label>
                          <input type="text" placeholder="•••" className="w-full px-4 py-3 border border-[#EDE4D0] rounded-xl text-sm focus:outline-none focus:border-[#C4622D] bg-[#FAF7F2]" />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {step === 'review' && (
                <div>
                  <h2 className="text-xl font-semibold text-[#2C1810] mb-6" style={{ fontFamily: 'var(--font-serif)' }}>Review Your Order</h2>
                  <div className="space-y-4 mb-6">
                    {items.map(({ product, quantity, personalization }) => (
                      <div key={product.id} className="flex gap-4">
                        <img src={product.image} alt={product.name} className="w-16 h-16 rounded-xl object-cover bg-[#F5EDE0] shrink-0" />
                        <div className="flex-1">
                          <p className="font-semibold text-sm text-[#2C1810]">{product.name}</p>
                          <PersonalizationNote personalization={personalization} />
                          <p className="text-xs text-[#8B6B4A]">Qty: {quantity}</p>
                        </div>
                        <p className="font-bold text-sm text-[#2C1810]">₹{product.price * quantity}</p>
                      </div>
                    ))}
                  </div>
                  <div className="bg-[#F5EDE0] rounded-xl p-4 space-y-2 text-sm">
                    <div className="flex justify-between text-[#8B6B4A]"><span>Subtotal</span><span>₹{subtotal}</span></div>
                    <div className="flex justify-between text-[#8B6B4A]"><span>Shipping</span><span>{shipping === 0 ? 'FREE' : `₹${shipping}`}</span></div>
                    <div className="flex justify-between font-bold text-[#2C1810] text-base pt-2 border-t border-[#EDE4D0]"><span>Total</span><span>₹{total}</span></div>
                  </div>
                  <div className="mt-4 bg-[#EBF3EA] rounded-xl p-4 flex gap-2 items-start">
                    <span>🌿</span>
                    <p className="text-xs text-[#5C7A5A] leading-relaxed">Your order will be packed in our eco-friendly, 100% recyclable packaging. A handwritten note of care will accompany your gift.</p>
                  </div>
                </div>
              )}

              <div className="flex gap-3 mt-8">
                {stepIndex > 0 && (
                  <button
                    onClick={() => setStep(steps[stepIndex - 1].id)}
                    className="px-6 py-3 border border-[#EDE4D0] text-[#5C3D2E] rounded-full font-medium text-sm hover:border-[#C4622D] transition-colors"
                  >
                    ← Back
                  </button>
                )}
                <button
                  onClick={next}
                  disabled={submitting || addingItem}
                  className="disabled:opacity-60 disabled:cursor-wait flex-1 py-3.5 bg-[#C4622D] text-white rounded-full font-semibold hover:bg-[#D4795A] transition-colors flex items-center justify-center gap-2"
                >
                  {submitting ? 'Placing your order…' : step === 'review' ? '✓ Place Order' : `Continue to ${steps[stepIndex + 1]?.label}`}
                  {step !== 'review' && <ArrowRightIcon size={16} />}
                </button>
              </div>
              {error && <p className="mt-4 text-sm text-[#C4622D]" role="alert">{error}</p>}
            </div>
          </div>

          {/* Mini order summary */}
          <aside className="checkout-summary" aria-label="Order summary">
            <div className="checkout-panel">
              <h2 className="checkout-summary-title" style={{ fontFamily: 'var(--font-serif)' }}>Order Summary <span>{items.reduce((count, item) => count + item.quantity, 0)} items</span></h2>
              <div className="space-y-3 mb-5">
                {items.map(({ product, quantity, personalization }) => (
                  <div key={product.id} className="flex items-center gap-3">
                    <div className="relative">
                      <img src={product.image} alt={product.name} className="w-12 h-12 rounded-lg object-cover bg-[#F5EDE0]" />
                      <span className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-[#C4622D] text-white text-xs rounded-full flex items-center justify-center">{quantity}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-[#2C1810] truncate">{product.name}</p>
                          <PersonalizationNote personalization={personalization} />
                    </div>
                    <p className="text-xs font-bold text-[#2C1810]">₹{product.price * quantity}</p>
                  </div>
                ))}
              </div>
              <div className="space-y-2 text-sm border-t border-[#EDE4D0] pt-4">
                <div className="flex justify-between text-[#8B6B4A]"><span>Subtotal</span><span>₹{subtotal}</span></div>
                <div className="flex justify-between text-[#8B6B4A]"><span>Shipping</span><span>{shipping === 0 ? 'FREE' : `₹${shipping}`}</span></div>
                <div className="flex justify-between font-bold text-[#2C1810] pt-2 border-t border-[#EDE4D0]"><span>Total</span><span>₹{total}</span></div>
              </div>
            </div>
          </aside>
        </div>
        <ProductRecommendations extended open={!submitting} layout="checkout" openProductInNewTab
          excludedIds={items.map(item => item.product.id)}
          wishlistIds={wishlist} onToggleWishlist={onToggleWishlist}
          onAddToCart={addRecommendation} onProductClick={onProductClick} />
      </div>
    </div>
  );
}

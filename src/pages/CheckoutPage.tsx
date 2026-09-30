import { useState } from 'react';
import { CheckIcon, ArrowRightIcon } from '../components/Icons';
import type { CartItem } from '../components/CartDrawer';
import { createOrder } from '../lib/api/orders';
import { createPaymentIntent, verifyMockPayment } from '../lib/api/payments';

interface CheckoutPageProps {
  items: CartItem[];
  onComplete: () => void;
  onNavigate: (page: 'home' | 'shop' | 'product' | 'cart' | 'wishlist' | 'checkout' | 'about') => void;
}

type Step = 'contact' | 'delivery' | 'payment' | 'review';
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

export default function CheckoutPage({ items, onComplete, onNavigate }: CheckoutPageProps) {
  const [step, setStep] = useState<Step>('contact');
  const [selectedPayment, setSelectedPayment] = useState('upi');
  const [orderPlaced, setOrderPlaced] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ firstName: '', lastName: '', email: '', phone: '', line1: '', line2: '', city: '', state: '', postalCode: '', landmark: '' });

  const subtotal = items.reduce((s, i) => s + i.product.price * i.quantity, 0);
  const shipping = subtotal >= 999 ? 0 : 79;
  const total = subtotal + shipping;

  const stepIndex = steps.findIndex(s => s.id === step);

  const next = async () => {
    const idx = stepIndex;
    if (idx < steps.length - 1) setStep(steps[idx + 1].id);
    else {
      if (!form.firstName || !form.phone || !form.line1 || !form.city || !form.state || !form.postalCode) {
        setError('Please complete your contact and delivery details before placing the order.');
        return;
      }
      setSubmitting(true); setError('');
      try {
        const paymentMethod = selectedPayment === 'cod' ? 'COD' : selectedPayment === 'card' ? 'CARD' : selectedPayment === 'netbanking' ? 'NETBANKING' : 'UPI';
        const order = await createOrder({ paymentMethod, customerEmail: form.email || undefined, shippingAddress: { name: `${form.firstName} ${form.lastName}`.trim(), phone: form.phone, line1: form.line1, line2: form.line2 || undefined, landmark: form.landmark || undefined, city: form.city, state: form.state, postalCode: form.postalCode } });
        if (paymentMethod !== 'COD') {
          const intent = await createPaymentIntent(order.orderNumber);
          await verifyMockPayment(intent, paymentMethod === 'UPI' ? 'UPI / Mock gateway' : `${paymentMethod} / Mock gateway`);
        }
        setOrderPlaced(true); onComplete();
      } catch (requestError) { setError(requestError instanceof Error ? requestError.message : 'We could not place your order. Please try again.'); }
      finally { setSubmitting(false); }
    }
  };

  const input = (name: keyof typeof form) => ({ value: form[name], onChange: (event: React.ChangeEvent<HTMLInputElement>) => setForm(current => ({ ...current, [name]: event.target.value })) });

  if (orderPlaced) {
    return (
      <div className="min-h-screen bg-[#FAF7F2] pt-28 flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <div className="w-24 h-24 bg-[#EBF3EA] rounded-full flex items-center justify-center text-5xl mx-auto mb-6">
            🎉
          </div>
          <h1 className="text-4xl font-medium text-[#2C1810] mb-4" style={{ fontFamily: 'var(--font-serif)' }}>
            Order Placed!
          </h1>
          <p className="text-[#8B6B4A] mb-2">Thank you for your order. Our artisans are already working on your handmade creation.</p>
          <p className="text-sm text-[#8B6B4A] mb-8">Order confirmation sent to your email. Expected delivery: 5–7 working days.</p>
          <div className="bg-white rounded-2xl p-5 border border-[#EDE4D0] mb-8 text-left">
            <p className="text-xs text-[#8B6B4A] font-semibold uppercase tracking-wider mb-3">What happens next?</p>
            {['Order confirmed & artisan assigned', 'Handcrafted with care (3–5 days)', 'Quality checked & packaged beautifully', 'Dispatched & delivered to you'].map((s, i) => (
              <div key={i} className="flex items-center gap-3 py-2">
                <div className="w-6 h-6 rounded-full bg-[#EBF3EA] text-[#8FAF8C] flex items-center justify-center text-xs font-bold shrink-0">{i + 1}</div>
                <span className="text-sm text-[#5C3D2E]">{s}</span>
              </div>
            ))}
          </div>
          <button onClick={() => onNavigate('home')} className="px-10 py-4 bg-[#C4622D] text-white rounded-full font-semibold hover:bg-[#D4795A] transition-colors">
            Continue Shopping
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAF7F2] pt-28">
      <div className="max-w-5xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-medium text-[#2C1810] mb-8" style={{ fontFamily: 'var(--font-serif)' }}>Checkout</h1>

        {/* Step indicators */}
        <div className="flex items-center mb-10">
          {steps.map(({ id, label }, i) => (
            <div key={id} className="flex items-center flex-1">
              <div className="flex items-center gap-2 shrink-0">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${i < stepIndex ? 'bg-[#8FAF8C] text-white' : i === stepIndex ? 'bg-[#C4622D] text-white' : 'bg-[#EDE4D0] text-[#8B6B4A]'}`}>
                  {i < stepIndex ? <CheckIcon size={14} /> : i + 1}
                </div>
                <span className={`text-sm font-medium hidden md:block ${i === stepIndex ? 'text-[#C4622D]' : 'text-[#8B6B4A]'}`}>{label}</span>
              </div>
              {i < steps.length - 1 && (
                <div className={`flex-1 h-0.5 mx-3 ${i < stepIndex ? 'bg-[#8FAF8C]' : 'bg-[#EDE4D0]'}`} />
              )}
            </div>
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl p-7 border border-[#EDE4D0]" style={{ boxShadow: '0 2px 8px rgba(44,24,16,0.04)' }}>
              {step === 'contact' && (
                <div>
                  <h2 className="text-xl font-semibold text-[#2C1810] mb-6" style={{ fontFamily: 'var(--font-serif)' }}>Contact Information</h2>
                  <div className="grid md:grid-cols-2 gap-4">
                    {[
                      { label: 'First Name', placeholder: 'Priya', col: 1, name: 'firstName' },
                      { label: 'Last Name', placeholder: 'Sharma', col: 1, name: 'lastName' },
                      { label: 'Email', placeholder: 'priya@example.com', col: 2, type: 'email', name: 'email' },
                      { label: 'Phone Number', placeholder: '+91 98765 43210', col: 1, type: 'tel', name: 'phone' },
                    ].map(({ label, placeholder, col, type = 'text', name }) => (
                      <div key={label} className={col === 2 ? 'md:col-span-2' : ''}>
                        <label className="block text-sm font-medium text-[#2C1810] mb-1.5">{label}</label>
                        <input
                          type={type}
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
                        <label className="block text-sm font-medium text-[#2C1810] mb-1.5">{label}</label>
                        <input
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
                    {items.map(({ product, quantity }) => (
                      <div key={product.id} className="flex gap-4">
                        <img src={product.image} alt={product.name} className="w-16 h-16 rounded-xl object-cover bg-[#F5EDE0] shrink-0" />
                        <div className="flex-1">
                          <p className="font-semibold text-sm text-[#2C1810]">{product.name}</p>
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
                  disabled={submitting}
                  className="flex-1 py-3.5 bg-[#C4622D] text-white rounded-full font-semibold hover:bg-[#D4795A] transition-colors flex items-center justify-center gap-2"
                >
                  {submitting ? 'Placing your order…' : step === 'review' ? '✓ Place Order' : `Continue to ${steps[stepIndex + 1]?.label}`}
                  {step !== 'review' && <ArrowRightIcon size={16} />}
                </button>
              </div>
              {error && <p className="mt-4 text-sm text-[#C4622D]" role="alert">{error}</p>}
            </div>
          </div>

          {/* Mini order summary */}
          <div className="hidden lg:block">
            <div className="bg-white rounded-2xl p-6 border border-[#EDE4D0] sticky top-28">
              <h3 className="text-base font-semibold text-[#2C1810] mb-4" style={{ fontFamily: 'var(--font-serif)' }}>Order Summary</h3>
              <div className="space-y-3 mb-5">
                {items.map(({ product, quantity }) => (
                  <div key={product.id} className="flex items-center gap-3">
                    <div className="relative">
                      <img src={product.image} alt={product.name} className="w-12 h-12 rounded-lg object-cover bg-[#F5EDE0]" />
                      <span className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-[#C4622D] text-white text-xs rounded-full flex items-center justify-center">{quantity}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-[#2C1810] truncate">{product.name}</p>
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
          </div>
        </div>
      </div>
    </div>
  );
}

import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import CheckoutPage from './CheckoutPage';
import { getProductDiscovery } from '../lib/api/productDiscovery';
import { createOrder } from '../lib/api/orders';
import { accountProfileApi } from '../lib/api/account';
import { createPaymentIntent, getGuestPaymentCapability, rememberGuestPaymentCapability, retryCashfreePayment, verifyCashfreePayment, verifyMockPayment } from '../lib/api/payments';
import { openCashfreeCheckout } from '../lib/payment/cashfreeCheckout';
vi.mock('../lib/api/productDiscovery', () => ({ getProductDiscovery: vi.fn() }));
vi.mock('../lib/api/orders', () => ({ createOrder: vi.fn() }));
vi.mock('../lib/api/account', () => ({ accountProfileApi: { overview: vi.fn() } }));
vi.mock('../lib/api/payments', () => ({ createPaymentIntent: vi.fn(), getGuestPaymentCapability: vi.fn(), rememberGuestPaymentCapability: vi.fn(), retryCashfreePayment: vi.fn(), forgetGuestPaymentCapability: vi.fn(), verifyMockPayment: vi.fn(), verifyCashfreePayment: vi.fn() }));
vi.mock('../lib/payment/cashfreeCheckout', () => ({ openCashfreeCheckout: vi.fn() }));
const rose = {id:1, name:'Crochet Rose Bouquet', slug:'rose', image:'/rose.webp', price:1299, category:'Flowers', rating:0, reviews:0};
const bunny = {...rose,id:2,name:'<Bunny>',slug:'bunny',price:799};
const props = () => ({ items:[{product:rose,quantity:1}], wishlist:[2], onToggleWishlist:vi.fn(), couponCode:null, onComplete:vi.fn(), onNavigate:vi.fn(), onProductClick:vi.fn(), onAddToCart:vi.fn().mockResolvedValue(undefined) });
afterEach(() => { cleanup(); vi.resetAllMocks(); window.history.replaceState(null, '', '/checkout'); });

it('shows the backend-authoritative shipping amount before creating a payment intent', () => {
  render(<CheckoutPage {...props()} items={[{product:bunny,quantity:1}]}/>);
  const summary = within(screen.getByRole('complementary', { name: 'Order summary' }));
  expect(summary.getByText('Shipping').parentElement).toHaveTextContent('₹99');
  expect(summary.getByText('Total').parentElement).toHaveTextContent('₹898');
  expect(createOrder).not.toHaveBeenCalled();
  expect(createPaymentIntent).not.toHaveBeenCalled();
});

const completeCheckoutForm = () => {
  for (const [label, value] of [['First Name *','QA'],['Email *','demo.customer@example.com'],['Phone Number *','9876543210']] as const) fireEvent.change(screen.getByLabelText(label), {target:{value}});
  fireEvent.click(screen.getByRole('button',{name:'Continue to Delivery'}));
  for (const [label, value] of [['Address Line 1','12 Craft Lane'],['City','Mumbai'],['State','Maharashtra'],['PIN Code','400001']] as const) fireEvent.change(screen.getByLabelText(label), {target:{value}});
  fireEvent.click(screen.getByRole('button',{name:'Continue to Payment'}));
  fireEvent.click(screen.getByRole('button',{name:'Continue to Review'}));
  fireEvent.click(screen.getByRole('button',{name:/Place Order/}));
};

const useLocalMockPayment = (id: number, orderNumber: string) => {
  vi.mocked(createPaymentIntent).mockResolvedValue({paymentId:id,orderId:id,orderNumber,provider:'mock',providerOrderId:`mock-${id}`,amount:1378,amountPaise:137800,currency:'INR'});
  vi.mocked(verifyMockPayment).mockResolvedValue(undefined);
};

it('does not offer Cash on Delivery and keeps online payment methods available', () => {
  render(<CheckoutPage {...props()}/>);
  fireEvent.click(screen.getByRole('button',{name:'Continue to Delivery'}));
  fireEvent.click(screen.getByRole('button',{name:'Continue to Payment'}));
  expect(screen.queryByText('Cash on Delivery')).not.toBeInTheDocument();
  expect(screen.getByText('UPI')).toBeInTheDocument();
  expect(screen.getByText('Credit / Debit Card')).toBeInTheDocument();
  expect(screen.getByText('Net Banking')).toBeInTheDocument();
});

it('hands a Cashfree intent to hosted checkout and never uses mock verification', async () => {
  vi.mocked(createOrder).mockResolvedValue({id:7,orderNumber:'SLC-TEST-7',status:'PENDING_PAYMENT',paymentStatus:'PENDING',paymentMethod:'UPI',totalAmount:1378,totalAmountPaise:137800});
  const intent = {paymentId:9,orderId:7,orderNumber:'SLC-TEST-7',provider:'cashfree',providerOrderId:'cf-7',paymentSessionId:'opaque-session',environment:'sandbox' as const,amount:1378,amountPaise:137800,currency:'INR'};
  vi.mocked(createPaymentIntent).mockResolvedValue(intent);
  render(<CheckoutPage {...props()}/>);
  completeCheckoutForm();
  await waitFor(() => expect(openCashfreeCheckout).toHaveBeenCalledWith(intent));
  expect(verifyMockPayment).not.toHaveBeenCalled();
});

it('retains the guest order capability and sends it only in the payment-intent body', async () => {
  vi.mocked(createOrder).mockResolvedValue({id:17,orderNumber:'CB-20261031-AB12',guestTrackingToken:'guest-capability',status:'PENDING_PAYMENT',paymentStatus:'PENDING',paymentMethod:'UPI',totalAmount:898,totalAmountPaise:89800});
  vi.mocked(createPaymentIntent).mockResolvedValue({paymentId:19,orderId:17,orderNumber:'CB-20261031-AB12',provider:'cashfree',providerOrderId:'cf-19',paymentSessionId:'session',environment:'sandbox',amount:898,amountPaise:89800,currency:'INR'});
  render(<CheckoutPage {...props()} items={[{product:bunny,quantity:1}]}/>);
  completeCheckoutForm();
  await waitFor(() => expect(openCashfreeCheckout).toHaveBeenCalled());
  expect(rememberGuestPaymentCapability).toHaveBeenCalledWith('CB-20261031-AB12','guest-capability');
  expect(createPaymentIntent).toHaveBeenCalledWith('CB-20261031-AB12','guest-capability');
});

it('offers secure same-order retry after server-confirmed failure without creating another order', async () => {
  window.history.replaceState(null, '', '/checkout?paymentId=9&cfOrderId=cf-9');
  vi.mocked(verifyCashfreePayment).mockResolvedValue({id:9,orderId:7,orderNumber:'CB-20261031-AB12',provider:'cashfree',providerOrderId:'cf-9',amount:898,amountPaise:89800,currency:'INR',status:'FAILED',verificationState:'FAILED',canRetry:true});
  vi.mocked(getGuestPaymentCapability).mockReturnValue('guest-capability');
  vi.mocked(retryCashfreePayment).mockResolvedValue({paymentId:10,orderId:7,orderNumber:'CB-20261031-AB12',provider:'cashfree',providerOrderId:'cf-10',paymentSessionId:'new-session',environment:'sandbox',amount:898,amountPaise:89800,currency:'INR'});
  render(<CheckoutPage {...props()} items={[]}/>);
  expect(await screen.findByRole('alert')).toHaveTextContent('Your payment was not completed');
  fireEvent.click(await screen.findByRole('button',{name:'Retry payment'}));
  await waitFor(() => expect(retryCashfreePayment).toHaveBeenCalledWith(9,'guest-capability'));
  expect(openCashfreeCheckout).toHaveBeenCalledWith(expect.objectContaining({paymentId:10,orderNumber:'CB-20261031-AB12'}));
  expect(createOrder).not.toHaveBeenCalled();
});

it('keeps pending payment state distinct and enables retry only when the server allows it', async () => {
  window.history.replaceState(null, '', '/checkout?paymentId=9&cfOrderId=cf-9');
  vi.mocked(verifyCashfreePayment).mockResolvedValue({id:9,orderId:7,orderNumber:'CB-20261031-AB12',provider:'cashfree',providerOrderId:'cf-9',amount:898,amountPaise:89800,currency:'INR',status:'PENDING',verificationState:'PENDING',canRetry:false});
  render(<CheckoutPage {...props()} items={[]}/>);
  expect(await screen.findByRole('alert')).toHaveTextContent('still being confirmed');
  expect(screen.queryByRole('button',{name:'Retry payment'})).not.toBeInTheDocument();
  expect(createOrder).not.toHaveBeenCalled();
});

it('does not trust redirect query text as payment proof and offers server verification retry', async () => {
  window.history.replaceState(null, '', '/checkout?paymentId=9&cfOrderId=cf-7&orderNumber=FAKE&payment_status=PAID');
  vi.mocked(verifyCashfreePayment).mockResolvedValue({id:9,orderId:7,orderNumber:'SLC-TEST-7',provider:'cashfree',providerOrderId:'cf-7',amount:1378,amountPaise:137800,currency:'INR',status:'PENDING'});
  render(<CheckoutPage {...props()}/>);
  expect(await screen.findByRole('alert')).toHaveTextContent('Your payment is still being confirmed');
  expect(screen.queryByText('Payment Confirmed!')).not.toBeInTheDocument();
  expect(verifyCashfreePayment).toHaveBeenCalledWith(9,'cf-7');
  expect(window.location.search).toContain('payment_status=PAID');
});

it('rejects non-decimal payment IDs from the return URL before calling verification', async () => {
  window.history.replaceState(null, '', '/checkout?paymentId=1e3&cfOrderId=cf-7');
  render(<CheckoutPage {...props()}/>);
  expect(await screen.findByRole('alert')).toHaveTextContent('could not verify this payment return');
  expect(verifyCashfreePayment).not.toHaveBeenCalled();
});

it('shows confirmation only for a matching server-verified Cashfree payment', async () => {
  window.history.replaceState(null, '', '/checkout?paymentId=9&cfOrderId=cf-7&orderNumber=FAKE');
  vi.mocked(getProductDiscovery).mockResolvedValue({sections:[{id:'new-arrivals',title:'New arrivals',strategy:'newest',products:[bunny]},{id:'featured',title:'Featured',strategy:'featured',products:[{...rose,id:3,name:'Crochet Daisy',slug:'daisy'}]}],nextCursor:null});
  vi.mocked(verifyCashfreePayment).mockResolvedValue({id:9,orderId:7,orderNumber:'SLC-TEST-7',provider:'cashfree',providerOrderId:'cf-7',amount:1378,amountPaise:137800,currency:'INR',status:'SUCCESS'});
  const p=props();
  render(<CheckoutPage {...p}/>);
  expect(await screen.findByRole('heading',{name:'Payment Confirmed!'})).toBeVisible();
  expect(await screen.findByRole('heading',{name:'New arrivals'})).toBeVisible();
  expect(screen.getByRole('heading',{name:'Featured'})).toBeVisible();
  expect(screen.getByText('Order SLC-TEST-7')).toBeVisible();
  expect(p.onComplete).toHaveBeenCalledOnce();
  expect(window.location.search).toBe('');
});

it('shows multiple API-driven recommendation layers after placing a local order', async () => {
  vi.mocked(createOrder).mockResolvedValue({id:8,orderNumber:'SLC-TEST-8',status:'PENDING_PAYMENT',paymentStatus:'PENDING',paymentMethod:'UPI',totalAmount:1378,totalAmountPaise:137800});
  useLocalMockPayment(8,'SLC-TEST-8');
  vi.mocked(getProductDiscovery).mockResolvedValue({sections:[{id:'popular',title:'Popular',strategy:'popular',products:[bunny]},{id:'new-arrivals',title:'New arrivals',strategy:'newest',products:[{...rose,id:3,name:'Crochet Daisy',slug:'daisy'}]}],nextCursor:null});
  const p=props();
  render(<CheckoutPage {...p}/>);
  completeCheckoutForm();
  const confirmation = await screen.findByRole('heading',{name:'Order Placed!'});
  expect(confirmation).toBeVisible();
  expect(confirmation.closest('section')).toHaveClass('w-full');
  expect(await screen.findByRole('heading',{name:'Popular'})).toBeVisible();
  expect(screen.getByRole('heading',{name:'New arrivals'})).toBeVisible();
  const heart=screen.getByRole('button',{name:'Remove <Bunny> from wishlist'});
  expect(heart).toHaveAttribute('aria-pressed','true');
  fireEvent.click(heart);
  expect(p.onToggleWishlist).toHaveBeenCalledWith(bunny);
  expect(screen.getByText('Order SLC-TEST-8')).toBeVisible();
  expect(screen.queryByText(/working days|3–5 days|Expected delivery/i)).not.toBeInTheDocument();
  expect(getProductDiscovery).toHaveBeenCalledWith('checkout',null,expect.any(AbortSignal));
});

it('keeps confirmed order visible when recommendations fail to load', async () => {
  vi.mocked(createOrder).mockResolvedValue({id:10,orderNumber:'SLC-TEST-10',status:'PENDING_PAYMENT',paymentStatus:'PENDING',paymentMethod:'UPI',totalAmount:1378,totalAmountPaise:137800});
  useLocalMockPayment(10,'SLC-TEST-10');
  vi.mocked(getProductDiscovery).mockRejectedValue(new Error('private discovery detail'));
  render(<CheckoutPage {...props()}/>);
  completeCheckoutForm();
  expect(await screen.findByRole('heading',{name:'Order Placed!'})).toBeVisible();
  expect(await screen.findByRole('alert')).toHaveTextContent('More creations could not load');
  expect(screen.getByText('Order SLC-TEST-10')).toBeVisible();
  expect(screen.queryByText('private discovery detail')).not.toBeInTheDocument();
});

it('continues excluding purchased products after the basket is cleared on completion', async () => {
  vi.mocked(createOrder).mockResolvedValue({id:12,orderNumber:'SLC-TEST-12',status:'PENDING_PAYMENT',paymentStatus:'PENDING',paymentMethod:'UPI',totalAmount:1378,totalAmountPaise:137800});
  useLocalMockPayment(12,'SLC-TEST-12');
  vi.mocked(getProductDiscovery).mockResolvedValue({sections:[{id:'best-sellers',title:'Best Sellers',strategy:'popular',products:[rose,bunny]}],nextCursor:null});
  const p=props();
  const view=render(<CheckoutPage {...p}/>);
  completeCheckoutForm();
  expect(await screen.findByRole('heading',{name:'Best Sellers'})).toBeVisible();
  view.rerender(<CheckoutPage {...p} items={[]}/>);
  expect(screen.getByRole('link',{name:'<Bunny>'})).toBeVisible();
  expect(screen.queryByRole('link',{name:'Crochet Rose Bouquet'})).not.toBeInTheDocument();
  expect(screen.getByText('Order SLC-TEST-12')).toBeVisible();
});

it('adds a recommendation to the next basket without creating or changing the placed order', async () => {
  vi.mocked(createOrder).mockResolvedValue({id:11,orderNumber:'SLC-TEST-11',status:'PENDING_PAYMENT',paymentStatus:'PENDING',paymentMethod:'UPI',totalAmount:1378,totalAmountPaise:137800});
  useLocalMockPayment(11,'SLC-TEST-11');
  vi.mocked(getProductDiscovery).mockResolvedValue({sections:[{id:'new-arrivals',title:'New arrivals',strategy:'newest',products:[bunny]}],nextCursor:null});
  const p=props();
  render(<CheckoutPage {...p}/>);
  completeCheckoutForm();
  expect(await screen.findByRole('heading',{name:'New arrivals'})).toBeVisible();
  fireEvent.click(screen.getByRole('button',{name:'Add <Bunny> to basket'}));
  await waitFor(()=>expect(screen.getByRole('status')).toHaveTextContent('<Bunny> added to your basket'));
  expect(screen.getByText('Order SLC-TEST-11')).toBeVisible();
  expect(createOrder).toHaveBeenCalledOnce();
  expect(createPaymentIntent).toHaveBeenCalledOnce();
  expect(p.onAddToCart).toHaveBeenCalledExactlyOnceWith(bunny);
});

it('adds without losing contact draft or navigating, updates summary, and excludes basket products', async () => {
  vi.mocked(getProductDiscovery).mockResolvedValue({sections:[{id:'suggestions',title:'You may also like',strategy:'newest',products:[rose,bunny]}],nextCursor:null});
  const p=props(); let finish=()=>{};
  p.onAddToCart.mockImplementation(()=>new Promise<void>(resolve=>{finish=resolve;}));
  const {rerender}=render(<CheckoutPage {...p}/>);
  fireEvent.change(screen.getByLabelText('First Name *'),{target:{value:'Anupama'}});
  const add=await screen.findByRole('button',{name:'Add <Bunny> to basket'});
  fireEvent.click(add); fireEvent.click(add);
  expect(p.onAddToCart).toHaveBeenCalledExactlyOnceWith(bunny);
  expect(screen.getByRole('button',{name:'Continue to Delivery'})).toBeDisabled();
  await act(async()=>finish());
  rerender(<CheckoutPage {...p} items={[...p.items,{product:bunny,quantity:1}]}/>);
  expect(screen.getByLabelText('First Name *')).toHaveValue('Anupama');
  const summary=within(screen.getByRole('complementary',{name:'Order summary'}));
  expect(summary.getByText('<Bunny>')).toBeVisible();
  expect(summary.getByText('Total').parentElement).toHaveTextContent('₹2098');
  expect(screen.queryByRole('button',{name:'Add <Bunny> to basket'})).not.toBeInTheDocument();
  expect(p.onNavigate).not.toHaveBeenCalled(); expect(p.onProductClick).not.toHaveBeenCalled();
  expect(createOrder).not.toHaveBeenCalled(); expect(createPaymentIntent).not.toHaveBeenCalled();
});

it('keeps discovery detail links separate from checkout and renders API text safely', async()=>{
  vi.mocked(getProductDiscovery).mockResolvedValue({sections:[{id:'suggestions',title:'You may also like',strategy:'newest',products:[bunny]}],nextCursor:null});
  render(<CheckoutPage {...props()}/>);
  const link=await screen.findByRole('link',{name:'<Bunny>'});
  expect(link).toHaveAttribute('href','/products/bunny');
  expect(link).toHaveAttribute('target','_blank');
  expect(link).toHaveAttribute('rel','noopener noreferrer');
  expect(document.querySelector('bunny')).toBeNull();
  expect(screen.getByRole('navigation',{name:'Checkout progress'})).toBeVisible();
});

it('shows a safe failed-add message and allows retry while retaining form and step',async()=>{
  vi.mocked(getProductDiscovery).mockResolvedValue({sections:[{id:'suggestions',title:'You may also like',strategy:'newest',products:[bunny]}],nextCursor:null});
  const p=props();p.onAddToCart.mockRejectedValueOnce(new Error('private provider detail'));
  render(<CheckoutPage {...p}/>);
  fireEvent.change(screen.getByLabelText('Email *'),{target:{value:'customer@example.com'}});
  fireEvent.click(await screen.findByRole('button',{name:'Add <Bunny> to basket'}));
  expect(await screen.findByRole('alert')).toHaveTextContent('Could not add this item. Please try again.');
  expect(screen.queryByText('private provider detail')).not.toBeInTheDocument();
  expect(screen.getByLabelText('Email *')).toHaveValue('customer@example.com');
  expect(screen.getByRole('button',{name:'Continue to Delivery'})).toBeEnabled();
  fireEvent.click(screen.getByRole('button',{name:'Add <Bunny> to basket'}));
  await waitFor(()=>expect(screen.getByRole('status')).toHaveTextContent('added to your basket'));
  expect(createOrder).not.toHaveBeenCalled();
});

it('does not request discovery or allow checkout for an empty basket; discovery failure never blocks a nonempty checkout',async()=>{
  const p=props();const {rerender}=render(<CheckoutPage {...p} items={[]}/>);
  expect(screen.getByRole('heading',{name:'Your basket is empty'})).toBeVisible();
  expect(getProductDiscovery).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button',{name:'Browse the collection'}));
  expect(p.onNavigate).toHaveBeenCalledWith('shop');
  vi.mocked(getProductDiscovery).mockRejectedValue(new Error('offline'));
  rerender(<CheckoutPage {...p}/>);
  await screen.findByRole('button',{name:'Try loading products again'});
  expect(screen.getByRole('button',{name:'Continue to Delivery'})).toBeEnabled();
  fireEvent.click(screen.getByRole('button',{name:'Continue to Delivery'}));
  expect(screen.getByRole('heading',{name:'Delivery Address'})).toBeVisible();
  expect(screen.getByLabelText('Address Line 1')).toBeVisible();
});

it('keeps API discovery across Contact, Delivery, Payment and Review and makes the basket action usable',async()=>{
  vi.mocked(getProductDiscovery).mockResolvedValue({sections:[{id:'new-arrivals',title:'New arrivals',strategy:'newest',products:[bunny]}],nextCursor:null});
  const p=props();render(<CheckoutPage {...p}/>);
  await screen.findByRole('heading',{name:'New arrivals'});
  for(const next of ['Delivery','Payment','Review']) {
    fireEvent.click(screen.getByRole('button',{name:`Continue to ${next}`}));
    expect(screen.getByRole('heading',{name:'New arrivals'})).toBeVisible();
  }
  expect(screen.getByRole('heading',{name:'Review Your Order'})).toBeVisible();
  expect(getProductDiscovery).toHaveBeenCalledTimes(1);
  fireEvent.click(screen.getByRole('button',{name:'← Back to basket'}));
  expect(p.onNavigate).toHaveBeenCalledWith('cart');expect(createOrder).not.toHaveBeenCalled();
});

it('renders the signed-in customer contact, retaining manual edits during basket updates', async () => {
  vi.mocked(accountProfileApi.overview).mockRejectedValue(new Error('offline'));
  const customer = { id: 5, name: 'Demo Customer', email: 'demo.customer@example.com', phone: '+919876543210', role: 'CUSTOMER', identities: ['email'] };
  const p = props(); const { rerender } = render(<CheckoutPage {...p} customer={customer} />);
  expect(screen.getByLabelText('First Name *')).toHaveValue('Demo');
  expect(screen.getByLabelText('Last Name')).toHaveValue('Customer');
  expect(screen.getByLabelText('Email *')).toHaveValue(customer.email);
  expect(screen.getByLabelText('Phone Number *')).toHaveValue(customer.phone);
  fireEvent.change(screen.getByLabelText('First Name *'), { target: { value: 'Delivery Recipient' } });
  rerender(<CheckoutPage {...p} customer={customer} items={[{ product: rose, quantity: 2 }]} />);
  expect(screen.getByLabelText('First Name *')).toHaveValue('Delivery Recipient');
  await act(async () => {});
  expect(createOrder).not.toHaveBeenCalled();
  expect(createPaymentIntent).not.toHaveBeenCalled();
});

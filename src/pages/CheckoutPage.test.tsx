import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import CheckoutPage from './CheckoutPage';
import { getProductDiscovery } from '../lib/api/productDiscovery';
import { createOrder } from '../lib/api/orders';
import { accountProfileApi } from '../lib/api/account';
import { createPaymentIntent } from '../lib/api/payments';
vi.mock('../lib/api/productDiscovery', () => ({ getProductDiscovery: vi.fn() }));
vi.mock('../lib/api/orders', () => ({ createOrder: vi.fn() }));
vi.mock('../lib/api/account', () => ({ accountProfileApi: { overview: vi.fn() } }));
vi.mock('../lib/api/payments', () => ({ createPaymentIntent: vi.fn(), verifyMockPayment: vi.fn() }));
const rose = {id:1, name:'Crochet Rose Bouquet', slug:'rose', image:'/rose.webp', price:1299, category:'Flowers', rating:0, reviews:0};
const bunny = {...rose,id:2,name:'<Bunny>',slug:'bunny',price:799};
const props = () => ({ items:[{product:rose,quantity:1}], couponCode:null, onComplete:vi.fn(), onNavigate:vi.fn(), onProductClick:vi.fn(), onAddToCart:vi.fn().mockResolvedValue(undefined) });
afterEach(() => { cleanup(); vi.resetAllMocks(); });

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

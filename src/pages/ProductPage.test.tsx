import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { renderToString } from 'react-dom/server';
import type { SeoMetadata } from '../lib/api/seo';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ProductPage from './ProductPage';
import {getProductInformation} from '../lib/api/catalogue';
import {informationFields} from '../lib/products/information';
import type { Product } from '../data/products';

vi.mock('../lib/api/catalogue',()=>({getProductInformation:vi.fn()}));
beforeEach(()=>{vi.mocked(getProductInformation).mockResolvedValue({});});
vi.mock('../components/CatalogueProvider', () => ({ useCatalogue: () => ({ products: [] }) }));

const product: Product = {
  id: 42,
  name: 'Crochet Rose Bouquet',
  slug: 'crochet-rose-bouquet',
  price: 1299,
  rating: 4.8,
  reviews: 12,
  image: '/rose.webp',
  images: ['/rose.webp'],
  category: 'Flowers',
  customizable: true,
};

afterEach(()=>{cleanup();vi.resetAllMocks();});

describe('ProductPage options', () => {
  it('does not show hardcoded color choices while product color variants are unavailable', () => {
    render(
      <ProductPage
        product={product}
        onAddToCart={vi.fn()}
        onToggleWishlist={vi.fn()}
        wishlist={[]}
        onProductClick={vi.fn()}
        onNavigate={vi.fn()}
      />,
    );

    expect(screen.queryByText('Flower Color')).not.toBeInTheDocument();
    expect(screen.queryByText('50+ options available')).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: product.name })).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: 'Add to Basket' })).toHaveLength(2);
  });
});

it('renders saved full description and product information in initial HTML without invented claims',()=>{
 const metadata={productEntity:{id:42,description:'Owner-written full product story',materialsUsed:'Owner supplied yarn',aggregateRating:null}} as SeoMetadata;
 const html=renderToString(<ProductPage product={product} seoMetadata={metadata} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} wishlist={[]} onProductClick={vi.fn()} onNavigate={vi.fn()}/>);
 expect(html).toContain('Owner-written full product story');expect(html).toContain('Owner supplied yarn');expect(html).not.toContain('premium cotton');expect(html).not.toContain('Free Shipping ₹999+');expect(html).not.toContain('Gift Wrapping');expect(html).not.toContain('Purchased:');expect(html.match(/<h1/g)).toHaveLength(1);
});


it('forwards the personalized note for basket and buy-now actions', () => {
  const add = vi.fn();
  render(<ProductPage product={product} onAddToCart={add} onToggleWishlist={vi.fn()} wishlist={[]} onProductClick={vi.fn()} onNavigate={vi.fn()} />);
  fireEvent.change(screen.getByLabelText('Add a Personalized Note (optional)'), {target:{value:'For Mum <with love>'}});
  fireEvent.click(screen.getAllByRole('button',{name:'Add to Basket'})[0]);
  expect(add).toHaveBeenCalledWith(product,1,{note:'For Mum <with love>'});
  fireEvent.click(screen.getByRole('button',{name:'Buy Now'}));
  expect(add).toHaveBeenLastCalledWith(product,1,{note:'For Mum <with love>'});
});

it('renders and expands all six saved specification fields on the actual product page, including after an empty SEO snapshot',async()=>{
 const information=Object.fromEntries(informationFields.map(([key,label])=>[key,`Confirmed ${label} <plain text>`]));
 vi.mocked(getProductInformation).mockResolvedValue(information);
 const metadata={productEntity:{id:42,materialsUsed:null,handmadeDetails:null}} as SeoMetadata;
 render(<ProductPage product={product} seoMetadata={metadata} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} wishlist={[]} onProductClick={vi.fn()} onNavigate={vi.fn()}/>);
 await screen.findByRole('button',{name:'Handmade Details'});
 for(const [key,label] of informationFields){
   const disclosure=screen.getByRole('button',{name:label});
   if(disclosure.getAttribute('aria-expanded')!=='true')fireEvent.click(disclosure);
   expect(disclosure).toHaveAttribute('aria-expanded','true');
   expect(screen.getByText(information[key])).toBeVisible();
 }
 expect(getProductInformation).toHaveBeenCalledWith(product.slug,expect.any(AbortSignal));
 expect(document.querySelector('plain')).toBeNull();
});

it('does not invent specifications when the product API returns null or deliberately cleared fields',async()=>{
 vi.mocked(getProductInformation).mockResolvedValue({handmadeDetails:null,materialsUsed:'',sizeDimensions:null,processingTime:'',careInstructions:null,shippingDelivery:''});
 render(<ProductPage product={product} onAddToCart={vi.fn()} onToggleWishlist={vi.fn()} wishlist={[]} onProductClick={vi.fn()} onNavigate={vi.fn()}/>);
 await waitFor(()=>expect(screen.queryByText('Loading product information…')).not.toBeInTheDocument());
 for(const [,label] of informationFields)expect(screen.queryByRole('button',{name:label})).not.toBeInTheDocument();
 expect(screen.getByRole('heading',{name:product.name})).toBeVisible();
});

import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { renderToString } from 'react-dom/server';
import type { SeoMetadata } from '../lib/api/seo';
import { afterEach, describe, expect, it, vi } from 'vitest';
import ProductPage from './ProductPage';
import type { Product } from '../data/products';

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

afterEach(cleanup);

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

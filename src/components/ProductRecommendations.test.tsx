import { cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import ProductRecommendations from './ProductRecommendations';
import { getProductDiscovery } from '../lib/api/productDiscovery';
vi.mock('../lib/api/productDiscovery',()=>({getProductDiscovery:vi.fn()}));
const product=(id:number)=>({id,name:`Product ${id}`,slug:`product-${id}`,price:400,image:'/rose.webp',category:'Flowers',rating:0,reviews:0});
const row=(id:string,ids:number[])=>({id,title:id,strategy:id,products:ids.map(product)});
const props=()=>({open:true,extended:true,onProductClick:vi.fn(),onAddToCart:vi.fn().mockResolvedValue(undefined),excludedIds:[1]});
afterEach(()=>{cleanup();vi.resetAllMocks();vi.unstubAllGlobals();});
it('appends API sections, deduplicates and excludes cart products, stopping repeated cursors',async()=>{
 vi.mocked(getProductDiscovery).mockResolvedValueOnce({sections:[row('newest',[1,2])],nextCursor:'next'}).mockResolvedValueOnce({sections:[row('featured',[2,3]),row('trending',[4]),row('popular',[5])],nextCursor:'next'});
 render(<ProductRecommendations {...props()}/>);
 expect(await screen.findByRole('heading',{name:'newest'})).toBeVisible();expect(screen.queryByText('Product 1')).not.toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Load more products'}));
 expect(await screen.findByRole('heading',{name:'featured'})).toBeVisible();
 expect(screen.getByRole('heading',{name:'trending'})).toBeVisible();expect(screen.getByRole('heading',{name:'popular'})).toBeVisible();
 expect(screen.getAllByText('Product 2')).toHaveLength(1);expect(screen.queryByRole('button',{name:'Load more products'})).not.toBeInTheDocument();
 fireEvent.click(screen.getByRole('button',{name:'Add Product 4 to basket'}));
});
it('retries pagination without dropping loaded products or leaking server errors',async()=>{
 vi.mocked(getProductDiscovery).mockResolvedValueOnce({sections:[row('newest',[2])],nextCursor:'next'}).mockRejectedValueOnce(new Error('private')).mockResolvedValueOnce({sections:[row('popular',[3])],nextCursor:null});
 render(<ProductRecommendations {...props()}/>);
 fireEvent.click(await screen.findByRole('button',{name:'Load more products'}));
 fireEvent.click(await screen.findByRole('button',{name:'Try loading products again'}));
 expect(screen.queryByText('private')).not.toBeInTheDocument();expect(await screen.findByText('Product 3')).toBeVisible();expect(screen.getByText('Product 2')).toBeVisible();
});

it('requests the next page near the scroll sentinel, without duplicate concurrent requests',async()=>{
 let intersect:IntersectionObserverCallback=()=>{};
 const observe=vi.fn();
 vi.stubGlobal('IntersectionObserver',class { constructor(callback:IntersectionObserverCallback){intersect=callback;} observe=observe;disconnect=vi.fn();unobserve=vi.fn(); });
 vi.mocked(getProductDiscovery).mockResolvedValueOnce({sections:[row('newest',[2])],nextCursor:'next'}).mockResolvedValueOnce({sections:[row('popular',[3])],nextCursor:null});
 render(<ProductRecommendations {...props()}/>);
 await screen.findByRole('button',{name:'Load more products'});
 intersect([{isIntersecting:true}] as IntersectionObserverEntry[],{} as IntersectionObserver);
 intersect([{isIntersecting:true}] as IntersectionObserverEntry[],{} as IntersectionObserver);
 expect(await screen.findByText('Product 3')).toBeVisible();expect(getProductDiscovery).toHaveBeenCalledTimes(2);expect(observe).toHaveBeenCalled();
});

it('fills the first compatibility row after cart exclusions instead of leaving a nearly empty row',async()=>{
 vi.mocked(getProductDiscovery).mockResolvedValue({compatibility:true,sections:[row('suggestions',[1,2,3,4]),row('new-arrivals',[5,6,7,8])],nextCursor:null});
 render(<ProductRecommendations {...props()} excludedIds={[1,2,3]}/>);
 const suggestions=await screen.findByRole('region',{name:'suggestions'});
 expect(within(suggestions).getAllByTestId('product-card')).toHaveLength(4);
 expect(within(screen.getByRole('region',{name:'new-arrivals'})).getAllByTestId('product-card')).toHaveLength(1);
 expect(screen.getAllByTestId('product-card')).toHaveLength(5);
});

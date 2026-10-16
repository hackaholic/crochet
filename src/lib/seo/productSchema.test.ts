import { describe, expect, it } from 'vitest';
import { buildProductSchema } from './productSchema';
import type { SeoMetadata } from '../api/seo';
import type { Product } from '../../data/products';
const visible = { id: 8, name: 'Sunflower Bouquet', price: 2199, description: 'Crochet sunflower' } as Product;
const metadata: SeoMetadata = {
  title: visible.name, description: visible.description!, canonicalPath: '/products/sunflower-bouquet', robots: 'index,follow', pageType: 'product', breadcrumbs: [],
  productEntity: {id:8,name:visible.name,slug:'sunflower-bouquet',sku:'SUN-REAL-001',price:2199,currency:'INR',inStock:false,inventoryStatus:'OUT_OF_STOCK',brand:'Sulocraft',imageUrls:['https://images.sulocraft.com/sun.png','javascript:alert(1)'],variants:[]},
};
describe('truthful Product schema',()=>{
  it('uses the API SKU/current visible price and actual stock, without fabricated claims',()=>{
    const schema=buildProductSchema(metadata,'https://sulocraft.com/products/sunflower-bouquet',visible)!;
    expect(schema.sku).toBe('SUN-REAL-001');expect(schema.offers.price).toBe(2199);
    expect(schema.offers.availability).toBe('https://schema.org/OutOfStock');
    expect(schema.image).toEqual(['https://images.sulocraft.com/sun.png']);
    expect(schema).not.toHaveProperty('aggregateRating');expect(schema.offers).not.toHaveProperty('priceValidUntil');
  });
  it('omits contradictory cached-price data and private/missing entities',()=>{
    expect(buildProductSchema(metadata,'https://sulocraft.com', {...visible,price:1999})).toBeUndefined();
    expect(buildProductSchema({...metadata,robots:'noindex,nofollow'},'https://sulocraft.com',visible)).toBeUndefined();
    expect(buildProductSchema({...metadata,productEntity:null},'https://sulocraft.com',visible)).toBeUndefined();
  });
});

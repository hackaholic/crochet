import { describe, it, expect } from 'vitest';
import { buildPageSchemas, publicBreadcrumbs } from './pageSchemas';
import type { SeoMetadata } from '../api/seo';
import type { Category } from '../api/catalogue';
const metadata: SeoMetadata = {title:'Sunflower', description:'Crochet flowers', canonicalPath:'/products/sunflower', canonicalUrl:'https://store.example/products/sunflower', robots:'index,follow',pageType:'product',breadcrumbs:[{name:'Home',path:'/'},{name:'Shop',path:'/shop'},{name:'Sunflowers',path:'/categories/sunflowers'},{name:'Sunflower',path:'/products/sunflower'}]};
const categories = [{name:'Flowers',slug:'flowers',children:[{name:'Single Flowers',slug:'single-flowers',children:[{name:'Sunflowers',slug:'sunflowers',children:[]}]}]}] as unknown as Category[];
describe('shared page schemas', () => {
  it('uses full DB tree ancestry and the canonical origin for visible and structured breadcrumbs', () => {
    const trail=publicBreadcrumbs(metadata,categories);
    expect(trail.map(item=>item.name)).toEqual(['Home','Shop','Flowers','Single Flowers','Sunflowers','Sunflower']);
    const schema=buildPageSchemas(metadata,metadata.canonicalUrl!,null,categories)['sulocraft-breadcrumb-schema'] as {itemListElement:Array<{position:number;item:string}>};
    expect(schema.itemListElement.map(item=>item.item)).toEqual(trail.map(item=>item.url));
    expect(schema.itemListElement.map(item=>item.position)).toEqual([1,2,3,4,5,6]);
  });
  it('uses actual brand data and omits unprovided founding, social and search claims', () => {
    const schema=buildPageSchemas({...metadata,pageType:'website',breadcrumbs:[],brand:{name:'API Brand',legalName:'Unverified legal name',whatsappUrl:'https://contact.example/chat',logoUrl:'https://images.example/logo.png',sameAs:['https://contact.example/chat','https://social.example/brand','javascript:alert(1)','https://user:secret@social.example'] }},metadata.canonicalUrl!)['sulocraft-site-schema'];
    const encoded=JSON.stringify(schema);
    expect(encoded).toContain('API Brand'); expect(encoded).toContain('https://images.example/logo.png');
    expect(encoded).not.toMatch(/legalName|contact.example|foundingDate|founder|SearchAction|instagram|javascript|secret/);
  });
  it('omits unsupported/private schemas and invalid breadcrumb trails', () => {
    expect(buildPageSchemas({...metadata,robots:'noindex,nofollow'},metadata.canonicalUrl!)).toEqual({});
    expect(buildPageSchemas(metadata,'javascript:alert(1)')).toEqual({});
    for(const path of ['//evil.example','/admin','/shop?q=duplicate','/../secret']) expect(publicBreadcrumbs({...metadata,breadcrumbs:[{name:'Bad',path}]})).toEqual([]);
    expect(buildPageSchemas({...metadata,pageType:'website',brand:null},metadata.canonicalUrl!)).not.toHaveProperty('sulocraft-site-schema');
  });
  it('emits collection schema only for its visible API heading, without invented rankings', () => {
    const schemas=buildPageSchemas({...metadata,pageType:'collection',h1:'Flowers',categoryEntity:{id:1,name:'Flowers',slug:'flowers'}},'https://store.example/categories/flowers');
    expect(schemas['sulocraft-category-schema']).toMatchObject({'@type':'CollectionPage',name:'Flowers'});
    expect(JSON.stringify(schemas)).not.toContain('ItemList');
    expect(buildPageSchemas({...metadata,pageType:'collection',h1:'Wrong',categoryEntity:{id:1,name:'Flowers',slug:'flowers'}},metadata.canonicalUrl!)).not.toHaveProperty('sulocraft-category-schema');
  });
});

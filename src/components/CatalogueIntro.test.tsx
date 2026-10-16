import { renderToString } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import CatalogueIntro from './CatalogueIntro';
import type { SeoMetadata } from '../lib/api/seo';
const metadata = { categoryEntity:{id:1,name:'Flowers',slug:'flowers',description:'Crochet blooms.\n<img src=x onerror=alert(1)>'} } as SeoMetadata;
describe('database catalogue intro',()=>{
 it('is present in initial HTML as escaped plain text',()=>{
   const html=renderToString(<CatalogueIntro pathname="/categories/flowers" metadata={metadata}/>);
   expect(html).toContain('Crochet blooms.');expect(html).toContain('&lt;img');expect(html).not.toContain('<img');expect(html).not.toContain('<h1');
 });
 it('omits stale route, missing and blank descriptions instead of inventing copy',()=>{
   expect(renderToString(<CatalogueIntro pathname="/categories/baby" metadata={metadata}/>)).toBe('');
   expect(renderToString(<CatalogueIntro pathname="/shop" metadata={metadata}/>)).toBe('');
   expect(renderToString(<CatalogueIntro pathname="/categories/flowers" metadata={{...metadata,categoryEntity:{...metadata.categoryEntity!,description:' '}}}/>)).toBe('');
 });
 it('uses collection content independently',()=>{
   expect(renderToString(<CatalogueIntro pathname="/collections/gifts" metadata={{...metadata,collectionEntity:{id:2,name:'Gifts',slug:'gifts',description:'DB gift selection'}}}/>)).toContain('DB gift selection');
 });
});

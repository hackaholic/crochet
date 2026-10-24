import { afterEach, expect, it, vi } from 'vitest';
import { getProductDiscovery } from './productDiscovery';
const product={id:1,name:'Rose',slug:'rose',price:400,currency:'INR',inStock:true,image:'/rose.webp'};
const signal=()=>new AbortController().signal;
afterEach(()=>vi.unstubAllGlobals());
it('uses credentialed bounded discovery and rejects unsafe/ineligible products',async()=>{
 const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({sections:[{id:'featured',title:'Featured',strategy:'featured',products:[product,{...product,id:2,image:'javascript:alert(1)'},{...product,id:3,inStock:false}]}],nextCursor:'page:2'})});vi.stubGlobal('fetch',fetch);
 const page=await getProductDiscovery('checkout',null,signal());
 expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/storefront/discovery?context=checkout&limit=16'),expect.objectContaining({credentials:'include'}));
 expect(page.sections[0].products.map(p=>p.id)).toEqual([1]);expect(page.nextCursor).toBe('page:2');
});
it('falls back only for a missing API, advances newest pages, and stops at exhaustion',async()=>{
 const fetch=vi.fn().mockResolvedValueOnce({ok:false,status:404}).mockResolvedValueOnce({ok:true,json:async()=>Array.from({length:8},(_,i)=>({...product,id:i+1}))}).mockResolvedValueOnce({ok:true,json:async()=>[]});vi.stubGlobal('fetch',fetch);
 const page=await getProductDiscovery('checkout',null,signal());
 expect(page.sections.map(s=>s.title)).toEqual(['You may also like','New arrivals']);expect(page.nextCursor).toBe('catalogue:8');
 expect((await getProductDiscovery('checkout',page.nextCursor,signal())).nextCursor).toBeNull();
 expect(fetch.mock.calls[2][0]).toContain('sort=newest&limit=8&offset=8');
});
it('fails closed on API errors, malformed/oversized pages and invalid cursors without catalogue fallback',async()=>{
 const fetch=vi.fn().mockResolvedValueOnce({ok:false,status:403}).mockResolvedValueOnce({ok:true,json:async()=>({sections:[],nextCursor:'x'.repeat(513)})}).mockResolvedValueOnce({ok:true,json:async()=>({sections:Array(6).fill({}),nextCursor:null})});vi.stubGlobal('fetch',fetch);
 await expect(getProductDiscovery('checkout',null,signal())).rejects.toThrow('unavailable');
 await expect(getProductDiscovery('checkout',null,signal())).rejects.toThrow('Invalid');
 await expect(getProductDiscovery('checkout',null,signal())).rejects.toThrow('Invalid');
 await expect(getProductDiscovery('checkout','catalogue:-1',signal())).rejects.toThrow('Invalid');
 expect(fetch).toHaveBeenCalledTimes(3);
});

it('prepends cart-aware products once, deduplicates ranked rows and preserves paging', async () => {
 const fetch = vi.fn().mockImplementation(async (url: string) => url.includes('/cart/recommendations')
   ? { ok: true, json: async () => ({ strategy: 'personalized', products: [product] }) }
   : { ok: true, json: async () => ({ sections: [{ id: 'featured', title: 'Featured', strategy: 'featured', products: [product, {...product,id:2}] }], nextCursor: url.includes('cursor=') ? null : 'next' }) });
 vi.stubGlobal('fetch', fetch);
 const page = await getProductDiscovery('basket',null,signal());
 expect(page.sections.map(row=>row.id)).toEqual(['basket-suggestions','featured']);
 expect(page.sections[0].strategy).toBe('personalized');
 expect(page.sections.flatMap(row=>row.products.map(p=>p.id))).toEqual([1,2]);
 expect(page.nextCursor).toBe('next');
 await getProductDiscovery('basket',page.nextCursor,signal());
 expect(fetch.mock.calls.filter(([url])=>String(url).includes('/cart/recommendations'))).toHaveLength(1);
 expect(fetch.mock.calls).toHaveLength(3);
});
it('retains ordinary sections if the cart endpoint is absent, but never hides denied/malformed cart responses', async () => {
 const fetch = vi.fn().mockResolvedValueOnce({ok:false,status:404}).mockResolvedValueOnce({ok:true,json:async()=>({sections:[],nextCursor:null})}).mockResolvedValueOnce({ok:false,status:403}).mockResolvedValueOnce({ok:true,json:async()=>({strategy:'invented',products:[]})});
 vi.stubGlobal('fetch',fetch);
 expect((await getProductDiscovery('basket',null,signal())).sections).toEqual([]);
 await expect(getProductDiscovery('basket',null,signal())).rejects.toThrow('unavailable');
 await expect(getProductDiscovery('basket',null,signal())).rejects.toThrow('Invalid');
 expect(fetch).toHaveBeenCalledTimes(4);
});
it('keeps cart lead and honest newest pagination when only ranked discovery is absent', async () => {
 const fetch = vi.fn().mockResolvedValueOnce({ok:true,json:async()=>({strategy:'related',products:[product]})}).mockResolvedValueOnce({ok:false,status:404}).mockResolvedValueOnce({ok:true,json:async()=>Array.from({length:8},(_,i)=>({...product,id:i+1}))});
 vi.stubGlobal('fetch',fetch);
 const page=await getProductDiscovery('basket',null,signal());
 expect(page.compatibility).toBe(false);
 expect(page.sections.map(row=>row.title)).toEqual(['You may also like','New arrivals']);
 expect(page.sections.flatMap(row=>row.products.map(p=>p.id))).toEqual([1,2,3,4,5,6,7,8]);
 expect(page.nextCursor).toBe('catalogue:8');
});

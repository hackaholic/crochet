import { afterEach, expect, it, vi } from 'vitest';
import { getBasketDiscovery, getCartRecommendations } from './basketRecommendations';
const product = { id: 1, name: 'Rose', slug: 'rose', image: '/rose.webp', price: 400, currency: 'INR', inStock: true };
afterEach(() => vi.unstubAllGlobals());
it('uses cookie-bound cart recommendations and excludes duplicate/unsafe/ineligible products', async () => {
 const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({strategy:'related',products:[product,product,{...product,id:2,image:'javascript:alert(1)'},{...product,id:3,inStock:false}]})});
 vi.stubGlobal('fetch',fetch);
 const signal=new AbortController().signal;
 expect(await getBasketDiscovery(signal)).toEqual([expect.objectContaining({id:1})]);
 expect(fetch).toHaveBeenCalledExactlyOnceWith(expect.stringContaining('/cart/recommendations?limit=4'),{signal,credentials:'include'});
});
it('falls back to bounded newest only for404, never for forbidden or server errors', async () => {
 const fetch=vi.fn().mockResolvedValueOnce({ok:false,status:404}).mockResolvedValueOnce({ok:true,json:async()=>[product]}).mockResolvedValueOnce({ok:false,status:403}).mockResolvedValueOnce({ok:false,status:500});
 vi.stubGlobal('fetch',fetch);
 expect(await getBasketDiscovery()).toHaveLength(1);
 expect(fetch.mock.calls[1][0]).toContain('/products?sort=newest&limit=8');
 await expect(getBasketDiscovery()).rejects.toThrow('unavailable');
 await expect(getBasketDiscovery()).rejects.toThrow('unavailable');
 expect(fetch).toHaveBeenCalledTimes(4);
});
it.each([null, {strategy:'invented',products:[]},{strategy:'related',products:{}},{strategy:'newest',products:Array(5).fill(product)}])('rejects malformed or oversized cart response %#',async value=>{
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>value}));
 await expect(getCartRecommendations()).rejects.toThrow('Invalid');
});
it('preserves empty results and propagates cancellation without catalogue fallback',async()=>{
 const fetch=vi.fn().mockResolvedValueOnce({ok:true,json:async()=>({strategy:'featured',products:[]})}).mockRejectedValueOnce(new DOMException('Aborted','AbortError'));
 vi.stubGlobal('fetch',fetch);
 expect(await getBasketDiscovery()).toEqual([]);
 await expect(getBasketDiscovery(new AbortController().signal)).rejects.toThrow('Aborted');
 expect(fetch).toHaveBeenCalledTimes(2);
});

import {afterEach, expect, it, vi} from 'vitest';
import {cartApi} from './cart';

afterEach(()=>{vi.unstubAllGlobals();});
it('sends customer personalization as JSON with the authenticated cart request',async()=>{
 const fetcher=vi.fn().mockResolvedValue({ok:true,json:async()=>({items:[]})});
 vi.stubGlobal('fetch',fetcher);
 await cartApi.add(42,2,{note:'For Mum <with love>'});
 const [url,request]=fetcher.mock.calls[0];
 expect(url).toMatch(/\/cart\/items$/);
 expect(request.credentials).toBe('include');
 expect(JSON.parse(request.body)).toEqual({product_id:42,quantity:2,personalization:{note:'For Mum <with love>'}});
 await cartApi.add(42,1);
 expect(JSON.parse(fetcher.mock.calls[1][1].body)).toEqual({product_id:42,quantity:1});
});

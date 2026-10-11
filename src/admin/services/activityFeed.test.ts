import {afterEach,it,expect,vi} from 'vitest';
import {getActivityFeed} from './api';
vi.mock('../../lib/api/client',()=>({apiUrl:(path:string)=>path}));
afterEach(()=>vi.unstubAllGlobals());
it('preserves the source order ID across events and never guesses missing IDs',async()=>{
 const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({recentOrders:[
  {id:'order-uuid',orderNumber:'PUBLIC-123',statusHistory:[{id:'a',status:'CONFIRMED'},{id:'b',status:'SHIPPED'}]},
  {id:42,orderNumber:'NUMERIC-ID',statusHistory:[{id:'d',status:'PAID'}]},
  {orderNumber:'NO-ID',statusHistory:[{id:'c',status:'DELIVERED'}]}
 ]})});vi.stubGlobal('fetch',fetch);
 const feed=await getActivityFeed();expect(feed.map(item=>item.orderId)).toEqual(['order-uuid','order-uuid','42',undefined]);
 expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/admin/dashboard/summary?'),expect.objectContaining({credentials:'include'}));
});
it('returns an empty feed for no recent orders',async()=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:true,json:async()=>({})}));expect(await getActivityFeed()).toEqual([]);});
it('rejects authorization denial without reading private response content',async()=>{const json=vi.fn();vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,status:403,json}));await expect(getActivityFeed()).rejects.toThrow('Admin request failed (403)');expect(json).not.toHaveBeenCalled();});

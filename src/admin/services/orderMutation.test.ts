import {afterEach,expect,it,vi} from 'vitest';
import {updateOrderStatus} from './api';
afterEach(()=>vi.unstubAllGlobals());
it('uses the authenticated status API response including persisted tracking and history',async()=>{
 const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({id:42,orderNumber:'ORDER-QA',status:'SHIPPED',trackingNumber:'TRACK-42',courierName:'QA courier',items:[],statusHistory:[{id:1,status:'SHIPPED',timestamp:'2026-10-01',note:'API note'}]})});vi.stubGlobal('fetch',fetch);
 const order=await updateOrderStatus('42','SHIPPED',undefined,'TRACK-42');expect(fetch.mock.calls[0][1]).toMatchObject({method:'PATCH',credentials:'include'});expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({status:'SHIPPED',trackingNumber:'TRACK-42'});expect(order.shipment).toMatchObject({trackingId:'TRACK-42',courier:'QA courier',createdDate:'',history:[]});expect(order.timeline[0]).toMatchObject({status:'SHIPPED',note:'API note'});
});
it('rejects denied status changes without returning success data',async()=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,status:403}));await expect(updateOrderStatus('42','CONFIRMED')).rejects.toThrow('403');});

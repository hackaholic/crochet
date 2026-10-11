import {afterEach,it,expect,vi} from 'vitest';
import {getProductInformation} from './catalogue';
vi.mock('./client',()=>({apiUrl:(p:string)=>p}));
afterEach(()=>vi.unstubAllGlobals());
it('fetches exact encoded product detail and preserves null/blank without invented copy',async()=>{const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({materialsUsed:'Cotton',careInstructions:null})});vi.stubGlobal('fetch',fetch);const signal=new AbortController().signal;const result=await getProductInformation('bunny/one',signal);expect(fetch).toHaveBeenCalledWith('/products/bunny%2Fone',{signal});expect(result).toMatchObject({materialsUsed:'Cotton',careInstructions:'',shippingDelivery:''});});
it('does not expose upstream error details',async()=>{const json=vi.fn();vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,json}));await expect(getProductInformation(6)).rejects.toThrow('Product information unavailable');expect(json).not.toHaveBeenCalled();});
